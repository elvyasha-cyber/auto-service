from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.lead_metrics import LeadMetricsCRUD

router = APIRouter(prefix="/lead-metrics", tags=["lead-metrics"])


class LeadMetricsIn(BaseModel):
    lead_id: int
    time_on_page: int = 0
    buttons_clicked: str = ""
    cursor_pauses: str = ""
    return_count: int = 0


class LeadMetricsUpdate(BaseModel):
    time_on_page: int | None = None
    buttons_clicked: str | None = None
    cursor_pauses: str | None = None
    return_count: int | None = None


@router.post("")
def create_metrics(body: LeadMetricsIn):
    row = LeadMetricsCRUD.create(body.model_dump())
    if row is None:
        raise HTTPException(status_code=404, detail="Заявка для этих метрик не найдена")
    return row


@router.get("")
def list_metrics():
    return LeadMetricsCRUD.list_all()


@router.get("/{lead_id}")
def get_metrics(lead_id: int):
    row = LeadMetricsCRUD.get(lead_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Метрики не найдены")
    return row


@router.put("/{lead_id}")
def update_metrics(lead_id: int, body: LeadMetricsUpdate):
    row = LeadMetricsCRUD.update(lead_id, body.model_dump(exclude_unset=True))
    if row is None:
        raise HTTPException(status_code=404, detail="Метрики не найдены")
    return row


@router.delete("/{lead_id}")
def delete_metrics(lead_id: int):
    if not LeadMetricsCRUD.delete(lead_id):
        raise HTTPException(status_code=404, detail="Метрики не найдены")
    return {"deleted": lead_id}
