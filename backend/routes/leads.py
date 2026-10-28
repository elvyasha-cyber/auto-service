from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.lead import LeadCRUD
from models.lead_rank import rank_queue

router = APIRouter(prefix="/leads", tags=["leads"])


class LeadIn(BaseModel):
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    business_info: str = ""
    budget: str = ""
    contact_method: str = ""
    phone: str = ""
    email: str = ""
    telegram: str = ""
    whatsapp: str = ""
    max_contact: str = ""
    comment: str = ""
    business_niche: str = ""
    company_size: str = ""
    task_volume: str = ""
    client_role: str = ""
    business_size: str = ""
    need_volume: str = ""
    deadline: str = ""
    task_type: str = ""
    product: str = ""
    convenient_time: str = ""


class LeadUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    business_info: str | None = None
    budget: str | None = None
    contact_method: str | None = None
    phone: str | None = None
    email: str | None = None
    telegram: str | None = None
    whatsapp: str | None = None
    max_contact: str | None = None
    comment: str | None = None
    business_niche: str | None = None
    company_size: str | None = None
    task_volume: str | None = None
    client_role: str | None = None
    business_size: str | None = None
    need_volume: str | None = None
    deadline: str | None = None
    task_type: str | None = None
    product: str | None = None
    convenient_time: str | None = None


@router.post("")
def create_lead(body: LeadIn):
    return LeadCRUD.create(body.model_dump())


@router.get("")
def list_leads():
    return LeadCRUD.list_all()


@router.get("/queue")
def lead_queue():
    """Горячие сверху. Температура считается по полям заявки, отдельной колонки в базе нет."""
    return rank_queue(LeadCRUD.list_all())


@router.get("/{lead_id}")
def get_lead(lead_id: int):
    row = LeadCRUD.get(lead_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return row


@router.put("/{lead_id}")
def update_lead(lead_id: int, body: LeadUpdate):
    row = LeadCRUD.update(lead_id, body.model_dump(exclude_unset=True))
    if row is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return row


@router.delete("/{lead_id}")
def delete_lead(lead_id: int):
    if not LeadCRUD.delete(lead_id):
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return {"deleted": lead_id}
