import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import List
from fastapi import Request
from fastapi.templating import Jinja2Templates

from medperf.account_management import get_medperf_user_data
from medperf.entities.dataset import Dataset

router = APIRouter()

templates = Jinja2Templates(directory="medperf/web_ui/templates")

logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Dataset])
def get_datasets(local_only: bool = False, mine_only: bool = False):
    filters = {}
    if mine_only:
        filters["owner"] = get_medperf_user_data()["id"]

    return Dataset.all(
        local_only=local_only,
        filters=filters,
    )


@router.get("/ui", response_class=HTMLResponse)
def datasets_ui(request: Request, local_only: bool = False, mine_only: bool = False):
    datasets = get_datasets(local_only, mine_only)
    return templates.TemplateResponse("datasets.html", {"request": request, "datasets": datasets})