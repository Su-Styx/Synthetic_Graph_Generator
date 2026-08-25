import csv
import io
import logging
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import networkx as nx
from scipy.io import mmread

from django.conf import settings
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import GenModelSerializer, RunSerializer
from .models import GenModel, Run
from .serializers import RunSerializer, UserSignupSerializer
from .services.metrics import compute_all_metrics
from .services.query_engine import run_custom_query, run_generic_queries
from .tasks import execute_run

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health(request):
    return Response({"status": "ok"})

# NOTE that each class 

class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().order_by('-created_at')
    serializer_class = RunSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        run = serializer.save(status="pending")
        transaction.on_commit(lambda: execute_run.delay(run.id))

    def get_queryset(self):
        user = self.request.user
        return Run.objects.filter(created_by=user)

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for item in data:
            item.pop("result", None)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        result = data.get("result")
        if result and isinstance(result, dict):
            meta = result.get("metadata") or {}
            n_nodes = meta.get("n_nodes") or len(result.get("nodes", []))

            print("DEBUG retrieve run", instance.id, "n_nodes", n_nodes)

            if n_nodes > 1500:
                # large graphs will only return a stripped metadata set instead of the whole graph
                stripped_meta = {
                    "model": meta.get("model"),
                    "n_nodes": n_nodes,
                    "n_edges": meta.get("n_edges", len(result.get("edges", []))),
                    "directed": meta.get("directed"),
                    "parameters": meta.get("parameters"),
                }

                data["result"] = {
                    "nodes": [],     # or omit entirely
                    "edges": [],
                    "metadata": stripped_meta,
                }

        return Response(data)

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

def _sample_graph(result: dict, max_nodes: int = 1500) -> dict:
    nodes = result.get("nodes", [])
    edges = result.get("edges", [])

    if len(nodes) <= max_nodes:
        return result

    sampled_ids = {node["id"] for node in nodes[:max_nodes]}
    sampled_nodes = [node for node in nodes if node["id"] in sampled_ids]
    sampled_edges = [
        e for e in edges
        if e["source"] in sampled_ids and e["target"] in sampled_ids
    ]

    meta = result.get("metadata") or {}
    sampled_meta = {
        **meta,
        "n_nodes": len(sampled_nodes),
        "n_edges": len(sampled_edges),
        "sampled_from_n_nodes": meta.get("n_nodes", len(nodes)),
        "sampled_from_n_edges": meta.get("n_edges", len(edges)),
    }

    return {
        "nodes": sampled_nodes,
        "edges": sampled_edges,
        "metadata": sampled_meta,
    }





class WorkloadQueryView(APIView):
    def post(self, request):
        run_id = request.data.get("run_id")
        source_run_id = request.data.get("source_run_id")
        query_type = request.data.get("query_type")
        query_params = request.data.get("query_params", {})

        try:
            run = Run.objects.get(id=run_id)
        except Run.DoesNotExist:
            return Response({"error": "run not found"}, status=status.HTTP_404_NOT_FOUND)

        if run.status != "completed" or not run.result:
            return Response({"error": "run has no completed result"}, status=status.HTTP_400_BAD_REQUEST)

        result = run.result  # full graph from DB

        source_result = None
        if source_run_id:
            try:
                source_run = Run.objects.get(id=source_run_id)
                source_result = source_run.result
            except Run.DoesNotExist:
                pass

        metrics = compute_all_metrics(result, source_result)
        generic_results = run_generic_queries(result)

        custom_result = None
        if query_type:
            custom_result = run_custom_query(result, query_type, query_params)

        return Response({
            "run_id": run.id,
            "metrics": metrics,
            "generic_queries": generic_results,
            "custom_query_result": custom_result,
        })


class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded under field 'file'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload_dir = Path(settings.MEDIA_ROOT) / "ergm_uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(uploaded_file.name).suffix
        filename = f"{uuid.uuid4().hex}{suffix}"
        saved_path = upload_dir / filename

        with saved_path.open("wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        relative_path = str(saved_path.relative_to(settings.MEDIA_ROOT)) #abs path
        return Response(
            {
                "filepath": relative_path, 
                "filename": uploaded_file.name,
            },
            status=status.HTTP_201_CREATED,
        )



class QuickViewUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded under field 'file'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        suffix = Path(uploaded_file.name).suffix.lower()

        try:
            if suffix == ".csv":
                graph = self._parse_csv(uploaded_file)
            elif suffix == ".mtx":
                graph = self._parse_mtx(uploaded_file)
            elif suffix == ".txt":
                graph = self._parse_edgelist(uploaded_file)
            else:
                return Response(
                    {"error": f"Unsupported file type: {suffix}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as exc:
            logger.exception(f"Failed to parse graph: {exc}")
            return Response(
                {"error": f"Failed to parse graph: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        graph_data = self._serialise_graph(graph, uploaded_file.name)
        metrics = self._calculate_metrics(graph)

        graph_data["metadata"]["metrics"] = metrics

        try:
            logger.info(f"Creating Run record: name=Uploaded: {uploaded_file.name}, user={request.user}")
            run = Run.objects.create(
                name=f"Uploaded: {uploaded_file.name}",
                job_type="upload",
                model=None,
                status=Run.Status.COMPLETED,
                params={
                    "source": "upload",
                    "filename": uploaded_file.name,
                    "file_type": suffix,
                    "directed": graph.is_directed(),
                },
                result=graph_data,
                created_by=request.user,  # now guaranteed to be authenticated
                started_at=None,
                finished_at=None,
            )
            logger.info(f"Run created successfully with id={run.id}")
        except Exception as exc:
            logger.exception(f"Failed to create Run: {exc}")
            return Response(
                {"error": f"Graph was parsed but could not be saved as a run: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "run_id": run.id,
                "name": run.name,
                "job_type": run.job_type,
                "model": run.model,
                "status": run.status,
                "nodes": graph_data["nodes"],
                "edges": graph_data["edges"],
                "metadata": graph_data["metadata"],
                "metrics": metrics,
            },
            status=status.HTTP_201_CREATED,
        )

    def _serialise_graph(self, graph, filename):
        nodes = [{"id": str(node)} for node in graph.nodes()]

        edges = [
            {
                "source": str(source),
                "target": str(target),
                **(
                    {"weight": data["weight"]}
                    if "weight" in data
                    else {}
                ),
            }
            for source, target, data in graph.edges(data=True)
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "model": "upload",
                "source_file": filename,
                "n_nodes": graph.number_of_nodes(),
                "n_edges": graph.number_of_edges(),
                "directed": graph.is_directed(),
            },
        }

    def _calculate_metrics(self, graph):
        node_count = graph.number_of_nodes()
        edge_count = graph.number_of_edges()

        degrees = [degree for _, degree in graph.degree()]
        average_degree = (
            sum(degrees) / len(degrees)
            if degrees
            else 0
        )
        maximum_degree = max(degrees) if degrees else 0

        density = nx.density(graph) if node_count > 1 else 0

        try:
            average_clustering = nx.average_clustering(graph.to_undirected())
        except Exception:
            average_clustering = 0

        return {
            "nodeCount": node_count,
            "edgeCount": edge_count,
            "avgDegree": round(average_degree, 4),
            "maxDegree": maximum_degree,
            "density": round(density, 6),
            "avgClustering": round(average_clustering, 6),
        }

    def _parse_edgelist(self, uploaded_file):
        text = uploaded_file.read().decode("utf-8")

        lines = [
            line
            for line in text.splitlines()
            if line.strip()
            and not line.strip().startswith(("#", "%"))
        ]

        if not lines:
            raise ValueError("Edge-list file is empty")

        return nx.parse_edgelist(lines, nodetype=str)

    def _parse_csv(self, uploaded_file):
        text = uploaded_file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty")

        header = rows[0]
        has_header = any(
            value.isalpha()
            for value in "".join(header)
        )

        edge_rows = rows[1:] if has_header else rows

        graph = nx.Graph()

        for row in edge_rows:
            if len(row) < 2:
                continue

            source = str(row[0]).strip()
            target = str(row[1]).strip()

            if source and target and source != target:
                graph.add_edge(source, target)

        if graph.number_of_edges() == 0:
            raise ValueError("No usable edges found in CSV")

        return graph

    def _parse_mtx(self, uploaded_file):
        matrix = mmread(uploaded_file)
        graph = nx.from_scipy_sparse_array(matrix)

        if graph.number_of_edges() == 0:
            raise ValueError("Matrix contains no usable edges")

        return graph

def vgae_generate_view(request):
    """
    Expects multipart/form-data with:
      - edges_file: CSV of edges
      - nodes_file: CSV of nodes
      - threshold, epochs, hidden1, hidden2, lr, seed, n (optional) as form fields
    """

    edges_file = request.FILES["edges_file"]
    nodes_file = request.FILES["nodes_file"]

    edges_path = default_storage.save(
        os.path.join("uploads", edges_file.name),
        ContentFile(edges_file.read()),
    )
    nodes_path = default_storage.save(
        os.path.join("uploads", nodes_file.name),
        ContentFile(nodes_file.read()),
    )

    # build abs paths 
    edges_abs = default_storage.path(edges_path)
    nodes_abs = default_storage.path(nodes_path)

    # parse numeric parameters with defaults
    threshold = float(request.POST.get("threshold", 0.5))
    epochs    = int(request.POST.get("epochs", 200))
    hidden1   = int(request.POST.get("hidden1", 32))
    hidden2   = int(request.POST.get("hidden2", 16))
    lr        = float(request.POST.get("lr", 0.01))
    seed      = request.POST.get("seed")
    n         = request.POST.get("n")
    n         = int(n) if n is not None else None

    params = {
        "filepath": edges_abs,
        "nodes_filepath": nodes_abs,
        "threshold": threshold,
        "epochs": epochs,
        "hidden1": hidden1,
        "hidden2": hidden2,
        "lr": lr,
        "seed": int(seed) if seed is not None else None,
        "n": n,
        "model_name": "VGAE",
        "checkpoint": None,
    }

    result = generate_VGAE(params)  # calls your endpoint logic

    return JsonResponse(result, safe=False)


from export_layer.schema_func import (
    json_export,
    csv_export,
    neo4j_export,
    rdf_export,
    turtle_export,
)

def download_run_graph(request, pk: int):
    fmt = request.GET.get("format", "JSON").upper()

    # IMPORTANT: drop created_by filter here
    run = get_object_or_404(Run, pk=pk)

    graph = run.result
    if not graph:
        raise Http404("Run has no result to export")

    tmp_dir = Path(tempfile.mkdtemp(prefix="run_export_"))

    if fmt == "JSON":
        out_path = tmp_dir / f"run_{pk}.json"
        json_export(graph, str(out_path))

    elif fmt == "CSV":
        out_dir = tmp_dir / "csv"
        csv_export(graph, str(out_dir))
        zip_base = tmp_dir / f"run_{pk}_csv"
        shutil.make_archive(str(zip_base), "zip", out_dir)
        out_path = zip_base.with_suffix(".zip")

    elif fmt == "NEO4J":
        out_dir = tmp_dir / "neo4j"
        neo4j_export(graph, str(out_dir))
        zip_base = tmp_dir / f"run_{pk}_neo4j"
        shutil.make_archive(str(zip_base), "zip", out_dir)
        out_path = zip_base.with_suffix(".zip")

    elif fmt == "RDF":
        out_path = tmp_dir / f"run_{pk}.rdf"
        rdf_export(graph, str(out_path))

    else:
        out_path = tmp_dir / f"run_{pk}.json"
        json_export(graph, str(out_path))

    fh = open(out_path, "rb")
    return FileResponse(fh, as_attachment=True, filename=out_path.name)








EFFICIENCY_RANK = {"poor": 1, "fair": 2, "good": 3, "great": 4}


class GenModelListView(ListAPIView):
    """
    GET /api/models/
    Query params:
      search    - free text, matches type / efficiency / parameters /
                  documentation / paper (case-insensitive contains)
      sort_by   - "type" or "efficiency" (optional)
      invert    - "true" / "false" (optional, default "false")

    Default ordering when sort_by=efficiency: great -> poor.
    invert=true reverses it: poor -> great.

    Default ordering when sort_by=type: alphabetical A -> Z.
    invert=true reverses it: Z -> A.
    """

    serializer_class = GenModelSerializer

    def get_queryset(self):
        qs = GenModel.objects.all()

        search = self.request.query_params.get("search", "").strip()
        sort_by = self.request.query_params.get("sort_by", "").strip()
        invert = self.request.query_params.get("invert", "false").lower() == "true"

        if search:
            qs = qs.filter(
                Q(type__icontains=search)
                | Q(efficiency__icontains=search)
                | Q(parameters__icontains=search)
                | Q(documentation__icontains=search)
                | Q(paper__icontains=search)
            )

        if sort_by == "efficiency":
            whens = [
                When(efficiency=key, then=Value(rank))
                for key, rank in EFFICIENCY_RANK.items()
            ]
            qs = qs.annotate(
                efficiency_rank=Case(
                    *whens, default=Value(0), output_field=IntegerField()
                )
            )
            qs = qs.order_by("efficiency_rank" if invert else "-efficiency_rank")

        elif sort_by == "type":
            qs = qs.order_by("-type" if invert else "type")

        return qs
