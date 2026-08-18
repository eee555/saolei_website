from django_tasks_db.models import DBTaskResult
from ninja import Schema
from ninja.orm import create_schema


class IdIn(Schema):
    id: int


DBTaskOut = create_schema(
    DBTaskResult,
    fields=['id', 'status', 'enqueued_at', 'started_at', 'finished_at', 'run_after', 'return_value', 'exception_class_path', 'traceback'],
)
