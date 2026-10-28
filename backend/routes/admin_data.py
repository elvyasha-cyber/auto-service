from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator

from models.admin_data import AdminDataCRUD
from routes.auth import require_admin

router = APIRouter(prefix="/admin-data", tags=["admin-data"])


class AdminDataIn(BaseModel):
    service_name: str = ""
    budget_min: int = 0
    budget_max: int = 0

    @model_validator(mode="after")
    def check_range(self):
        if self.budget_max < self.budget_min:
            raise ValueError("Верхняя граница бюджета меньше нижней")
        return self


class AdminDataUpdate(BaseModel):
    service_name: str | None = None
    budget_min: int | None = None
    budget_max: int | None = None


@router.post("")
def create_admin_data(body: AdminDataIn, admin: dict = Depends(require_admin)):
    return AdminDataCRUD.create(body.model_dump())


@router.get("")
def list_admin_data():
    return AdminDataCRUD.list_all()


@router.get("/{item_id}")
def get_admin_data(item_id: int):
    row = AdminDataCRUD.get(item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return row


@router.put("/{item_id}")
def update_admin_data(item_id: int, body: AdminDataUpdate, admin: dict = Depends(require_admin)):
    data = body.model_dump(exclude_unset=True)
    current = AdminDataCRUD.get(item_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    budget_min = data.get("budget_min", current["budget_min"])
    budget_max = data.get("budget_max", current["budget_max"])
    if budget_max < budget_min:
        raise HTTPException(status_code=422, detail="Верхняя граница бюджета меньше нижней")
    row = AdminDataCRUD.update(item_id, data)
    return row


@router.delete("/{item_id}")
def delete_admin_data(item_id: int, admin: dict = Depends(require_admin)):
    if not AdminDataCRUD.delete(item_id):
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"deleted": item_id}
