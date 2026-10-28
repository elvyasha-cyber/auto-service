import os
import textwrap
import time

import psycopg
from psycopg.rows import dict_row


def get_conn():
    """Подключение к Postgres из сети контейнеров. Хост — имя сервиса в compose."""
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        row_factory=dict_row,
    )


def init_tables():
    """Создаёт таблицы из SQL в докстрингах моделей. Ждёт, пока поднимется Postgres."""
    from models.admin import Admin
    from models.admin_data import AdminData
    from models.behavior_metrics import BehaviorMetrics
    from models.lead import Lead
    from models.lead_metrics import LeadMetrics

    last_error = None
    for _ in range(20):
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    for model in (Lead, LeadMetrics, AdminData, Admin, BehaviorMetrics):
                        cur.execute(textwrap.dedent(model.__doc__).strip())
                    for statement in getattr(Lead, "migrations", ()):
                        cur.execute(statement)
            return
        except psycopg.OperationalError as exc:
            last_error = exc
            time.sleep(1)
    raise last_error
