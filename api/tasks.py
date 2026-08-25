from celery import shared_task
from django.utils import timezone
from .models import Run
from .services.generators import generate_er, generate_ba, generate_ERGM, generate_VGAE
from .services.attributes import apply_schema

# note this needs to be updated for each model added
JOB_DISPATCH = {
    "er": generate_er,
    "ba": generate_ba,
    "ergm": generate_ERGM,
    "vgae": generate_VGAE
}

# celery worker will execute the defined function 
@shared_task
def execute_run(run_id):
    run = Run.objects.get(id=run_id)
    # status, time and error messages are automatically updated in sequential exection 
    try:
        run.status = "running"
        run.started_at = timezone.now()
        run.error_message = ""
        run.save(update_fields=["status", "started_at", "error_message", "updated_at"])
        # normaliseed job_type for easy matching
        job_type = run.job_type.lower().strip()

        if job_type not in JOB_DISPATCH:
            raise ValueError(f"Unsupported job_type: {run.job_type}")

        generator_fn = JOB_DISPATCH[job_type]
        result = generator_fn(run.params)

        result = apply_schema(result, run.params.get("schema"))   #schema is applied to the results here

        run.result = result
        run.status = "completed"
        run.finished_at = timezone.now()
        run.save(update_fields=["result", "status", "finished_at", "updated_at"])

        return {"run_id": run.id, "status": run.status}

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        run.finished_at = timezone.now()
        run.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
        raise