from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query
from pydantic import BaseModel

from models.behavior_metrics import BehaviorMetricsCRUD, summarize_behavior

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])


class BehaviorIn(BaseModel):
    application_id: int = 0
    time_on_page: int = 0
    buttons_clicked: str = ""
    cursor_positions: str = ""
    return_frequency: int = 0

    model_config = {"extra": "ignore"}


@router.post("")
def create_behavior(body: BehaviorIn):
    # application_id из урока не храним: это не номер заявки.
    saved = body.model_dump(exclude={"application_id"})
    return BehaviorMetricsCRUD.create(saved)


@router.get("/summary")
def behavior_summary():
    now = datetime.now(timezone.utc)
    rows = BehaviorMetricsCRUD.rows_since(now - timedelta(days=30))
    return summarize_behavior(rows, now)


@router.get("")
def list_behavior(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return BehaviorMetricsCRUD.list_page(skip, limit)
