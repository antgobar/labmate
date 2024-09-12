from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from services.crud import (
    delete_all_user_archives,
    get_current_user,
    get_user_archived_entity_summary,
)
from services.database import DbSession, get_db
from services.models import User
from services.resources import templates

router = APIRouter(prefix="/archives", tags=["archives"])


@router.get("/")
def get_archives_page(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    (
        archived_samples_count,
        archived_experiments_count,
    ) = get_user_archived_entity_summary(db, user)
    return templates.TemplateResponse(
        "pages/archives.html",
        {
            "request": request,
            "user": user,
            "archived_samples_count": archived_samples_count,
            "archived_experiments_count": archived_experiments_count,
        },
    )


@router.delete("/")
def delete_all_archives(
    db: DbSession = Depends(get_db), user: User = Depends(get_current_user)
):
    delete_all_user_archives(db, user)
    return HTMLResponse(
        """<button style="border: none;" class="pico-background-green-500">Deleted</button>"""
    )
