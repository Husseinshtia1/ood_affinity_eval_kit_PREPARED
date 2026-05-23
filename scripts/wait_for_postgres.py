import time
import sys
from sqlalchemy import create_engine, text
from apps.api.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)

for attempt in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('[PREPARED] PostgreSQL is ready.')
        sys.exit(0)
    except Exception as exc:
        print(f'[PREPARED] Waiting for PostgreSQL... attempt={attempt + 1}/30 error={exc}')
        time.sleep(2)

print('[PREPARED] PostgreSQL readiness timeout.')
sys.exit(1)
