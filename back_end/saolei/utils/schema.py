from typing import Annotated

from django_tasks_db.models import DBTaskResult
from ninja import Schema
from ninja.orm import create_schema
from pydantic import Field, StrictInt


# 对应 MySQL 的 models.PositiveIntegerField：允许 0，禁止类型转换；上限不适用于所有数据库。
MySQLPositiveInteger = Annotated[StrictInt, Field(ge=0, le=4294967295)]


class IdIn(Schema):
    id: int


DBTaskOut = create_schema(
    DBTaskResult,
    fields=['id', 'status', 'enqueued_at', 'started_at', 'finished_at', 'run_after', 'return_value', 'exception_class_path', 'traceback'],
)
