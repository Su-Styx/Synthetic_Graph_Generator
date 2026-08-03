# from cairo import Status
from django.db import models
from django.conf import settings


class Run(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Models(models.TextChoices):
        # ER = "erdos_renyi", "Erdos-Renyi","er","ER"
        # BA = "barabasi_albert", "Barabasi-Albert","ba","BA"
        ER = "erdos_renyi", "Erdos-Renyi",
        BA = "barabasi_albert", "Barabasi-Albert",
        ERGM ="ergm","ERGM",

    name=models.CharField(max_length=100)
    job_type=models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    model=models.CharField(
        max_length=20,
        choices=Models.choices,
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
        null=True,  # allow existing rows to have no user
        blank=True,  # optional in forms
    )

    def __str__(self):
        return f"{self.name} ({self.status})"


# Create your models here.
