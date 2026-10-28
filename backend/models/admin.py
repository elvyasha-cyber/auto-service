from core.db import get_conn


# Учётные записи мастеров. В базе лежит только хеш пароля.
class Admin:
    """
    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        login TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """

    columns = (
        "login",
        "password_hash",
    )


def public_admin(row: dict | None) -> dict | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "login": row["login"],
        "created_at": row["created_at"],
    }


class AdminCRUD:
    @staticmethod
    def create(login: str, password_hash: str) -> dict:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO admins (login, password_hash) VALUES (%s, %s) RETURNING *",
                    (login, password_hash),
                )
                return cur.fetchone()

    @staticmethod
    def get(admin_id: int) -> dict | None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM admins WHERE id = %s", (admin_id,))
                return cur.fetchone()

    @staticmethod
    def get_by_login(login: str) -> dict | None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM admins WHERE login = %s", (login,))
                return cur.fetchone()

    @staticmethod
    def count() -> int:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total FROM admins")
                return int(cur.fetchone()["total"])

    @staticmethod
    def list_all() -> list[dict]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, login, created_at FROM admins ORDER BY id")
                return cur.fetchall()

    @staticmethod
    def update(admin_id: int, data: dict) -> dict | None:
        sets = []
        values = []
        for column in Admin.columns:
            if column in data and data[column] is not None:
                sets.append(f"{column} = %s")
                values.append(data[column])
        if not sets:
            return AdminCRUD.get(admin_id)
        values.append(admin_id)
        sql = f"UPDATE admins SET {', '.join(sets)} WHERE id = %s RETURNING *"
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.fetchone()

    @staticmethod
    def delete(admin_id: int) -> bool:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM admins WHERE id = %s", (admin_id,))
                return cur.rowcount > 0
