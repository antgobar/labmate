from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from services.crud import (
    calculate_storage_size_for_user,
    delete_all_user_entities,
    get_current_user,
)
from services.database import DbSession, get_db
from services.models import User
from services.resources import templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_user_dashboard(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.storage_usage = round(calculate_storage_size_for_user(db, user.id), 2)
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.delete("/all_entities/")
def delete_all_entities(
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_all_user_entities(db, user)
    return RedirectResponse("/dashboard", status_code=303)
