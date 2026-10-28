from core.db import get_conn


# Заявка тёплого клиента: контакты, бизнес и параметры задачи.
class Lead:
    """
    CREATE TABLE IF NOT EXISTS leads (
        id SERIAL PRIMARY KEY,
        first_name TEXT NOT NULL DEFAULT '',
        last_name TEXT NOT NULL DEFAULT '',
        middle_name TEXT NOT NULL DEFAULT '',
        business_info TEXT NOT NULL DEFAULT '',
        budget TEXT NOT NULL DEFAULT '',
        contact_method TEXT NOT NULL DEFAULT '',
        phone TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL DEFAULT '',
        telegram TEXT NOT NULL DEFAULT '',
        whatsapp TEXT NOT NULL DEFAULT '',
        max_contact TEXT NOT NULL DEFAULT '',
        comment TEXT NOT NULL DEFAULT '',
        business_niche TEXT NOT NULL DEFAULT '',
        company_size TEXT NOT NULL DEFAULT '',
        task_volume TEXT NOT NULL DEFAULT '',
        client_role TEXT NOT NULL DEFAULT '',
        business_size TEXT NOT NULL DEFAULT '',
        need_volume TEXT NOT NULL DEFAULT '',
        deadline TEXT NOT NULL DEFAULT '',
        task_type TEXT NOT NULL DEFAULT '',
        product TEXT NOT NULL DEFAULT '',
        convenient_time TEXT NOT NULL DEFAULT ''
    );
    """

    columns = (
        "first_name",
        "last_name",
        "middle_name",
        "business_info",
        "budget",
        "contact_method",
        "phone",
        "email",
        "telegram",
        "whatsapp",
        "max_contact",
        "comment",
        "business_niche",
        "company_size",
        "task_volume",
        "client_role",
        "business_size",
        "need_volume",
        "deadline",
        "task_type",
        "product",
        "convenient_time",
    )

    # Таблица уже создана на сервере: CREATE IF NOT EXISTS новые колонки не добавит.
    migrations = (
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS email TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS telegram TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS whatsapp TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS max_contact TEXT NOT NULL DEFAULT ''",
    )


class LeadCRUD:
    @staticmethod
    def create(data: dict) -> dict:
        columns = Lead.columns
        sql = (
            f"INSERT INTO leads ({', '.join(columns)}) "
            f"VALUES ({', '.join(['%s'] * len(columns))}) RETURNING *"
        )
        values = [data.get(column, "") for column in columns]
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def get(lead_id: int) -> dict | None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM leads WHERE id = %s", (lead_id,))
                return cur.fetchone()

    @staticmethod
    def list_all() -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM leads ORDER BY id")
                return cur.fetchall()

    @staticmethod
    def update(lead_id: int, data: dict) -> dict | None:
        sets = []
        values = []
        for column in Lead.columns:
            if column in data and data[column] is not None:
                sets.append(f"{column} = %s")
                values.append(data[column])
        if not sets:
            return LeadCRUD.get(lead_id)
        values.append(lead_id)
        sql = f"UPDATE leads SET {', '.join(sets)} WHERE id = %s RETURNING *"
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def delete(lead_id: int) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM leads WHERE id = %s", (lead_id,))
                return cur.rowcount > 0
