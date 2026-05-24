from __future__ import annotations

from dataclasses import asdict, dataclass

from .hosting_adaptation import detect_hosting_capabilities


@dataclass(frozen=True)
class RuntimeMutationPlan:
    task_execution: str
    database_mode: str
    storage_mode: str
    email_mode: str
    persistence_warning: bool
    safe_for_real_customer_data: bool
    actions: list[str]


def build_runtime_mutation_plan() -> RuntimeMutationPlan:
    capabilities = detect_hosting_capabilities()
    actions: list[str] = []

    if capabilities.queue == 'redis':
        task_execution = 'celery-worker'
        actions.append('Celery worker workflows may be enabled.')
    else:
        task_execution = 'inline-or-disabled'
        actions.append('Disable Celery-dependent workflows or run lightweight tasks inline.')

    if capabilities.database == 'postgresql':
        database_mode = 'managed-postgresql'
        actions.append('Use managed PostgreSQL as the system of record.')
    elif capabilities.database == 'sqlite':
        database_mode = 'sqlite-demo'
        actions.append('Use SQLite only for demo/free-hosting mode.')
    else:
        database_mode = 'ephemeral-bootstrap'
        actions.append('Configure DATABASE_URL; fallback mode should not store real customer data.')

    if capabilities.storage == 's3-compatible':
        storage_mode = 'persistent-object-storage'
        actions.append('Persistent report storage is available.')
    else:
        storage_mode = 'local-temp'
        actions.append('Use temporary local storage; reports may disappear after redeploys.')

    if capabilities.email == 'smtp':
        email_mode = 'smtp'
        actions.append('Transactional email may be enabled.')
    else:
        email_mode = 'log-only'
        actions.append('Do not send emails; log invitation links or require manual delivery.')

    persistence_warning = database_mode != 'managed-postgresql' or storage_mode == 'local-temp'
    safe_for_real_customer_data = (
        database_mode == 'managed-postgresql'
        and storage_mode == 'persistent-object-storage'
        and task_execution == 'celery-worker'
    )

    if not safe_for_real_customer_data:
        actions.append('Mark deployment as demo/MVP only until PostgreSQL, Redis, and persistent storage are configured.')

    return RuntimeMutationPlan(
        task_execution=task_execution,
        database_mode=database_mode,
        storage_mode=storage_mode,
        email_mode=email_mode,
        persistence_warning=persistence_warning,
        safe_for_real_customer_data=safe_for_real_customer_data,
        actions=actions,
    )


def runtime_mutation_plan_dict() -> dict:
    return asdict(build_runtime_mutation_plan())
