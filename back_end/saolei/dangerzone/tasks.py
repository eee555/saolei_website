from django.tasks import task


@task
def task_echo(message: str):
    """Harmless task for E2E restart fixtures."""
    return message
