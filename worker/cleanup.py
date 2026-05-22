from datetime import datetime,timedelta
from apps.api.settings import get_settings
from apps.api.storage import delete_job

settings=get_settings()


def cleanup_expired_jobs():
    root=settings.temp_storage_dir

    for item in root.iterdir():
        if not item.is_dir():
            continue

        age=datetime.now()-datetime.fromtimestamp(item.stat().st_mtime)

        if age>timedelta(minutes=settings.report_ttl_minutes):
            delete_job(item.name)
