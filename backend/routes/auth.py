import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg.errors import UniqueViolation
from pydantic import BaseModel, field_validator

from models.admin import AdminCRUD, public_admin

router = APIRouter(prefix="/auth", tags=["auth"])

TOKEN_DAYS = 7


class Credentials(BaseModel):
    login: str
    password: str

    @field_validator("login")
    @classmethod
    def clean_login(cls, value: str) -> str:
        login = value.strip()
        if len(login) < 2 or len(login) > 64:
            raise ValueError("Логин от 2 до 64 символов")
        if any(char.isspace() for char in login):
            raise ValueError("В логине не должно быть пробелов")
        return login

    @field_validator("password")
    @classmethod
    def clean_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Пароль не короче 6 символов")
        return value


class AdminUpdate(BaseModel):
    login: str | None = None
    password: str | None = None

    @field_validator("login")
    @classmethod
    def clean_login(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return Credentials.clean_login(value)

    @field_validator("password")
    @classmethod
    def clean_password(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return Credentials.clean_password(value)


def secret_key() -> str:
    key = os.environ.get("SECRET_KEY", "").strip()
    if not key:
        raise HTTPException(status_code=500, detail="На сервере не задан SECRET_KEY")
    return key


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def password_matches(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def make_token(admin_id: int, login: str) -> str:
    payload = {
        "sub": str(admin_id),
        "login": login,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS),
    }
    return jwt.encode(payload, secret_key(), algorithm="HS256")


def token_response(row: dict) -> dict:
    safe = public_admin(row)
    return {
        "access_token": make_token(safe["id"], safe["login"]),
        "token_type": "bearer",
        "admin": safe,
    }


def current_admin(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Нужен вход")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, secret_key(), algorithms=["HS256"])
        admin_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Сессия недействительна")
    row = AdminCRUD.get(admin_id)
    if row is None:
        raise HTTPException(status_code=401, detail="Администратор не найден")
    return row


bearer_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    header = f"Bearer {credentials.credentials}" if credentials is not None else None
    return current_admin(header)


@router.get("/check")
def check_admins():
    return {"has_admin": AdminCRUD.count() > 0}


@router.post("/register")
def register_admin(body: Credentials):
    if AdminCRUD.count() > 0:
        raise HTTPException(status_code=403, detail="Регистрация закрыта: администратор уже есть")
    try:
        row = AdminCRUD.create(body.login, hash_password(body.password))
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Такой логин уже занят")
    return token_response(row)


@router.post("/login")
def login_admin(body: Credentials):
    row = AdminCRUD.get_by_login(body.login)
    if row is None or not password_matches(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return token_response(row)


@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    return public_admin(current_admin(authorization))


@router.get("/admins")
def list_admins(authorization: str | None = Header(default=None)):
    current_admin(authorization)
    return AdminCRUD.list_all()


@router.get("/admins/{admin_id}")
def get_admin(admin_id: int, authorization: str | None = Header(default=None)):
    current_admin(authorization)
    row = public_admin(AdminCRUD.get(admin_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Администратор не найден")
    return row


@router.put("/admins/{admin_id}")
def update_admin(admin_id: int, body: AdminUpdate, authorization: str | None = Header(default=None)):
    current_admin(authorization)
    if AdminCRUD.get(admin_id) is None:
        raise HTTPException(status_code=404, detail="Администратор не найден")
    data = {}
    if body.login is not None:
        data["login"] = body.login
    if body.password is not None:
        data["password_hash"] = hash_password(body.password)
    try:
        row = AdminCRUD.update(admin_id, data)
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Такой логин уже занят")
    return public_admin(row)


@router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int, authorization: str | None = Header(default=None)):
    current_admin(authorization)
    if not AdminCRUD.delete(admin_id):
        raise HTTPException(status_code=404, detail="Администратор не найден")
    return {"deleted": admin_id}
