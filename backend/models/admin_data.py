from core.db import get_conn


# Услуги и диапазон бюджета, по которым фронтенд собирает форму.
class AdminData:
    """
    CREATE TABLE IF NOT EXISTS admin_data (
        id SERIAL PRIMARY KEY,
        service_name TEXT NOT NULL DEFAULT '',
        budget_min INTEGER NOT NULL DEFAULT 0,
        budget_max INTEGER NOT NULL DEFAULT 0
    );
    """

    columns = (
        "service_name",
        "budget_min",
        "budget_max",
    )


class AdminDataCRUD:
    @staticmethod
    def create(data: dict) -> dict:
        columns = AdminData.columns
        sql = (
            f"INSERT INTO admin_data ({', '.join(columns)}) "
            f"VALUES ({', '.join(['%s'] * len(columns))}) RETURNING *"
        )
        values = [
            data.get("service_name", ""),
            data.get("budget_min", 0),
            data.get("budget_max", 0),
        ]
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def get(item_id: int) -> dict | None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM admin_data WHERE id = %s", (item_id,))
                return cur.fetchone()

    @staticmethod
    def list_all() -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM admin_data ORDER BY id")
                return cur.fetchall()

    @staticmethod
    def update(item_id: int, data: dict) -> dict | None:
        sets = []
        values = []
        for column in AdminData.columns:
            if column in data and data[column] is not None:
                sets.append(f"{column} = %s")
                values.append(data[column])
        if not sets:
            return AdminDataCRUD.get(item_id)
        values.append(item_id)
        sql = f"UPDATE admin_data SET {', '.join(sets)} WHERE id = %s RETURNING *"
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def delete(item_id: int) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM admin_data WHERE id = %s", (item_id,))
                return cur.rowcount > 0
