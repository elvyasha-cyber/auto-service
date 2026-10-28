from fastapi import APIRouter

from routes.admin_data import router as admin_data_router
from routes.auth import router as auth_router
from routes.behavior_metrics import router as behavior_metrics_router
from routes.lead_metrics import router as lead_metrics_router
from routes.leads import router as leads_router

api_router = APIRouter()
api_router.include_router(leads_router)
api_router.include_router(lead_metrics_router)
api_router.include_router(admin_data_router)
api_router.include_router(auth_router)
api_router.include_router(behavior_metrics_router)
