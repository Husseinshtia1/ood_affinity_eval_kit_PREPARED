def test_worker_tasks_import_successfully():
    from worker.tasks import evaluate_job, send_invitation_email_task, cleanup_expired_invitations

    assert evaluate_job.name == 'prepared.evaluate'
    assert send_invitation_email_task.name == 'prepared.send_invitation_email'
    assert cleanup_expired_invitations.name == 'prepared.cleanup_expired_invitations'


def test_celery_app_imports_successfully():
    from worker.celery_app import celery_app

    assert celery_app.main == 'prepared_worker'
