from datetime import datetime, timedelta, timezone

from core.db import get_conn


# Анонимные точки поведения на главной странице. К заявке не привязаны.
class BehaviorMetrics:
    """
    CREATE TABLE IF NOT EXISTS behavior_metrics (
        id SERIAL PRIMARY KEY,
        time_on_page INTEGER NOT NULL DEFAULT 0,
        buttons_clicked TEXT NOT NULL DEFAULT '',
        cursor_positions TEXT NOT NULL DEFAULT '',
        return_frequency INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    columns = (
        "time_on_page",
        "buttons_clicked",
        "cursor_positions",
        "return_frequency",
    )


class BehaviorMetricsCRUD:
    @staticmethod
    def create(data: dict) -> dict:
        columns = BehaviorMetrics.columns
        sql = (
            f"INSERT INTO behavior_metrics ({', '.join(columns)}) "
            f"VALUES ({', '.join(['%s'] * len(columns))}) RETURNING *"
        )
        values = [
            data.get("time_on_page", 0),
            data.get("buttons_clicked", ""),
            data.get("cursor_positions", ""),
            data.get("return_frequency", 0),
        ]
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def list_page(skip: int, limit: int) -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM behavior_metrics ORDER BY id LIMIT %s OFFSET %s",
                    (limit, skip),
                )
                return cur.fetchall()

    @staticmethod
    def rows_since(since: datetime) -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT time_on_page, cursor_positions, created_at
                    FROM behavior_metrics
                    WHERE created_at >= %s
                    ORDER BY id
                    """,
                    (since,),
                )
                return cur.fetchall()


def summarize_behavior(rows: list[dict], now: datetime | None = None) -> dict:
    """Среднее и максимальное время визита за сутки, неделю и месяц, плюс сетка курсора."""
    moment = now or datetime.now(timezone.utc)
    visits = []
    current = None
    for row in rows:
        created = row["created_at"]
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        seconds = int(row["time_on_page"] or 0)
        start_new = current is None
        if current is not None:
            gap = (created - current["last_at"]).total_seconds()
            if gap > 3 or seconds < current["max_seconds"]:
                start_new = True
        if start_new:
            current = {"last_at": created, "max_seconds": seconds}
            visits.append(current)
        else:
            current["last_at"] = created
            if seconds > current["max_seconds"]:
                current["max_seconds"] = seconds

    def period(name: str, title: str, days: int) -> dict:
        border = moment - timedelta(days=days)
        chosen = [visit for visit in visits if visit["last_at"] >= border]
        if not chosen:
            return {
                "name": name,
                "title": title,
                "visits": 0,
                "average_seconds": 0,
                "max_seconds": 0,
            }
        peaks = [visit["max_seconds"] for visit in chosen]
        return {
            "name": name,
            "title": title,
            "visits": len(chosen),
            "average_seconds": round(sum(peaks) / len(peaks)),
            "max_seconds": max(peaks),
        }

    bucket = 32
    counts = {}
    max_x = 1
    max_y = 1
    for row in rows:
        raw = str(row.get("cursor_positions") or "")
        left, _, right = raw.partition(",")
        try:
            x = int(left.strip())
            y = int(right.strip().split()[0])
        except ValueError:
            continue
        if x == 0 and y == 0:
            continue
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        cell = ((x // bucket) * bucket + bucket // 2, (y // bucket) * bucket + bucket // 2)
        counts[cell] = counts.get(cell, 0) + 1

    points = [
        {"x": x, "y": y, "count": count}
        for (x, y), count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:400]
    ]
    return {
        "periods": [
            period("day", "Сутки", 1),
            period("week", "7 дней", 7),
            period("month", "30 дней", 30),
        ],
        "points": points,
        "max_x": max_x,
        "max_y": max_y,
    }
