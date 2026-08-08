# from django.shortcuts import render

# Create your views here.
from api.serializers import RunSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.db import transaction
from .tasks import execute_run
from rest_framework.views import APIView 
from rest_framework import status
from .models import Run
from .services.metrics import compute_all_metrics
from .services.query_engine import run_generic_queries, run_custom_query

from pathlib import Path
import uuid
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
import csv 
import os
import io
from scipy.io import mmread

import networkx as nx



from .serializers import RunSerializer
# from .tasks import run_dummy_job

@api_view(['GET'])
def health(request):
    return Response({"status": "ok"})


# recieve the http request and return the response

# class RunViewSet(viewsets.ModelViewSet):
#     queryset = Run.objects.all().order_by('-created_at')
#     serializer_class = RunSerializer



#  for RunViewSet, it allows for 
# GET /api/runs/ - list all runs
# POST /api/runs/ - create a new run
# get /api/runs/{id}/ - retrieve a specific run

# queryset tells DRF what object to work with 
#  serializer_class tells DRF how to parse request data and return response
# perform_create customizes what happens after a valid post create request
from rest_framework import generics, permissions
from .serializers import UserSignupSerializer

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



class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]



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

        source_result = None
        if source_run_id:
            try:
                source_run = Run.objects.get(id=source_run_id)
                source_result = source_run.result
            except Run.DoesNotExist:
                pass

        metrics = compute_all_metrics(run.result, source_result)
        generic_results = run_generic_queries(run.result)

        custom_result = None
        if query_type:
            custom_result = run_custom_query(run.result, query_type, query_params)

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

        return Response(
            {
                "filepath": str(saved_path),
                "filename": uploaded_file.name,
            },
            status=status.HTTP_201_CREATED,
        )



class QuickViewUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

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
        except Exception as e:
            return Response(
                {"error": f"Failed to parse graph: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        nodes = [{"id": str(n)} for n in graph.nodes()]
        edges = [
            {
                "source": str(u),
                "target": str(v),
                **({"weight": data.get("weight")} if "weight" in data else {}),
            }
            for u, v, data in graph.edges(data=True)
        ]

        return Response({"nodes": nodes, "edges": edges}, status=status.HTTP_200_OK)

    def _parse_edgelist(self, uploaded_file):
        text = uploaded_file.read().decode("utf-8")
        lines = [ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith(("#", "%"))]
        return nx.parse_edgelist(lines, nodetype=str)

    def _parse_csv(self, uploaded_file):
        text = uploaded_file.read().decode("utf-8")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)

        if not rows:
            raise ValueError("CSV file is empty")

        header = rows[0]
        has_header = any(c.isalpha() for c in "".join(header))
        edge_rows = rows[1:] if has_header else rows

        graph = nx.Graph()
        for row in edge_rows:
            if len(row) < 2:
                continue
            source = str(row[0]).strip()
            target = str(row[1]).strip()
            if source and target:
                graph.add_edge(source, target)

        return graph

    def _parse_mtx(self, uploaded_file):
        matrix = mmread(uploaded_file)
        return nx.from_scipy_sparse_array(matrix)


def vgae_generate_view(request):
    """
    Expects multipart/form-data with:
      - edges_file: CSV of edges
      - nodes_file: CSV of nodes
      - threshold, epochs, hidden1, hidden2, lr, seed, n (optional) as form fields
    """

    edges_file = request.FILES["edges_file"]
    nodes_file = request.FILES["nodes_file"]

    # Save uploads to disk (e.g. under MEDIA_ROOT)
    edges_path = default_storage.save(
        os.path.join("uploads", edges_file.name),
        ContentFile(edges_file.read()),
    )
    nodes_path = default_storage.save(
        os.path.join("uploads", nodes_file.name),
        ContentFile(nodes_file.read()),
    )

    # Build absolute paths if your endpoint expects them
    edges_abs = default_storage.path(edges_path)
    nodes_abs = default_storage.path(nodes_path)

    # Parse numeric parameters with defaults
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

