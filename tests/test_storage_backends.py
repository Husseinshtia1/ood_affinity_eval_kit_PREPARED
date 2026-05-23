from pathlib import Path

from apps.api.storage_backends import LocalStorageBackend, S3StorageBackend


def test_local_storage_backend_creates_job_dir(tmp_path):
    backend = LocalStorageBackend(tmp_path)

    path = backend.job_dir('job-123')

    assert path.exists()
    assert path == tmp_path / 'job-123'


def test_local_storage_backend_object_path(tmp_path):
    backend = LocalStorageBackend(tmp_path)

    path = backend.object_path('job-123', 'predictions.csv')

    assert path == tmp_path / 'job-123' / 'predictions.csv'


def test_s3_storage_backend_object_key():
    backend = S3StorageBackend(
        bucket='prepared-test-bucket',
        region='us-east-1',
        prefix='prepared/jobs'
    )

    assert backend.object_key('job-123', 'report.json') == 'prepared/jobs/job-123/report.json'
