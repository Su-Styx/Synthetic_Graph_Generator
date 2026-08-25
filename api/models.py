from django.db import models
from django.conf import settings
import uuid



# the run class is the primary class used to contain any model-generated content 
# each run object belongs to a user and contains integral fields such as job_type, a (non unique) name, parameters used for gen. etc...
class Run(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Models(models.TextChoices):
        ER = "erdos_renyi", "Erdos-Renyi",
        BA = "barabasi_albert", "Barabasi-Albert",
        ERGM ="ergm","ERGM",
        VGAE = "vgae", "Variational Graph Autoencoder", 

    name=models.CharField(max_length=100)
    job_type=models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    model = models.CharField(
        max_length=20,
        choices=Models.choices,
        null=True,
        blank=True,
        default=None,
    )
    params=models.JSONField(default=dict,blank=True)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="runs",
        null=True,  # rows added before model change can exist w/o user
        blank=True,  
    )

    def __str__(self):
        return f"{self.name} ({self.status})"



# Defining the generative models that will be added to the list
# based on key-details when going through the thought process of which model to pick 
# will be sorted on front-end by efficiency and/or type? 
class GenModel(models.Model):
    EFFICIENCY_CHOICES = [
        ("poor", "Poor"),
        ("fair", "Fair"),
        ("good", "Good"),
        ("great", "Great"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=255)
    efficiency = models.CharField(
        max_length=10, choices=EFFICIENCY_CHOICES, default="fair"
    )
    parameters = models.TextField(blank=True, default="")
    documentation = models.TextField(blank=True, default="")
    paper = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Generation Model"
        verbose_name_plural = "Generation Models"

    def __str__(self):
        return f"{self.type} ({self.get_efficiency_display()})"
