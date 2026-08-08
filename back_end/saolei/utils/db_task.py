from django_tasks_db.models import DBTaskResult
from ninja.orm import create_schema

DBTaskOut = create_schema(
    DBTaskResult,
    fields=['id', 'status', 'enqueued_at', 'started_at', 'finished_at', 'return_value', 'exception_class_path', 'traceback'],
)
