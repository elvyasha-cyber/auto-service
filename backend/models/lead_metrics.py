from core.db import get_conn


# Поведение посетителя на странице. Одна заявка — одна запись метрик.
class LeadMetrics:
    """
    CREATE TABLE IF NOT EXISTS lead_metrics (
        lead_id INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
        time_on_page INTEGER NOT NULL DEFAULT 0,
        buttons_clicked TEXT NOT NULL DEFAULT '',
        cursor_pauses TEXT NOT NULL DEFAULT '',
        return_count INTEGER NOT NULL DEFAULT 0
    );
    """

    columns = (
        "time_on_page",
        "buttons_clicked",
        "cursor_pauses",
        "return_count",
    )


class LeadMetricsCRUD:
    @staticmethod
    def create(data: dict) -> dict | None:
        columns = ("lead_id",) + LeadMetrics.columns
        sql = (
            f"INSERT INTO lead_metrics ({', '.join(columns)}) "
            f"VALUES ({', '.join(['%s'] * len(columns))}) RETURNING *"
        )
        values = [data.get("lead_id")] + [
            data.get(column, 0 if column in ("time_on_page", "return_count") else "")
            for column in LeadMetrics.columns
        ]
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM leads WHERE id = %s", (data.get("lead_id"),))
                if cur.fetchone() is None:
                    return None
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def get(lead_id: int) -> dict | None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM lead_metrics WHERE lead_id = %s",
                    (lead_id,),
                )
                return cur.fetchone()

    @staticmethod
    def list_all() -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM lead_metrics ORDER BY lead_id")
                return cur.fetchall()

    @staticmethod
    def update(lead_id: int, data: dict) -> dict | None:
        sets = []
        values = []
        for column in LeadMetrics.columns:
            if column in data and data[column] is not None:
                sets.append(f"{column} = %s")
                values.append(data[column])
        if not sets:
            return LeadMetricsCRUD.get(lead_id)
        values.append(lead_id)
        sql = (
            f"UPDATE lead_metrics SET {', '.join(sets)} "
            "WHERE lead_id = %s RETURNING *"
        )
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def delete(lead_id: int) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM lead_metrics WHERE lead_id = %s",
                    (lead_id,),
                )
                return cur.rowcount > 0
