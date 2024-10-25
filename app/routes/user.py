from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.services.crud.auth import create_user_api_key, get_current_user
from app.services.crud.user import (
    calculate_storage_size_for_user,
    delete_all_user_entities,
)
from app.services.database import DbSession, get_db
from app.services.models import User
from app.services.resources import templates

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile/")
def get_user_profile(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.storage_usage = round(calculate_storage_size_for_user(db, user.id), 2)
    return templates.TemplateResponse(
        "pages/profile.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.get("/settings/")
def get_user_settings(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.delete("/data/all/")
def delete_all_entities(
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_all_user_entities(db, user)
    return RedirectResponse("/user/profile", status_code=303)


@router.post("/api_key/")
def create_api_key(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "partials/user/generated_api_token_dialog.html",
        {
            "request": request,
            "generated_api_token": create_user_api_key(db, user),
        },
    )


@router.delete("/api_key/")
def delete_api_key(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.hashed_api_key = None
    db.commit()
    return templates.TemplateResponse(
        "partials/user/create_api_key_action.html",
        {
            "request": request,
        },
    )
