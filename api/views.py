# from django.shortcuts import render

# Create your views here.
from api.serializers import RunSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from django.db import transaction
from .tasks import execute_run



from .models import Run
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