from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from services.crud import calculate_storage_size_for_user, get_current_user, search_user
from services.database import DbSession, get_db
from services.models import ContactResponse, User, UserRole
from services.resources import templates

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def get_admin_dashboard(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    users = db.query(User).all()
    message_query = db.query(ContactResponse)
    message_count = message_query.count()
    messages = message_query.limit(100).all()

    for user in users:
        user_usage = calculate_storage_size_for_user(db, user.id)
        user.storage_usage = round(user_usage)

    return templates.TemplateResponse(
        "pages/admin.html",
        {
            "request": request,
            "users": users,
            "message_count": message_count,
            "messages": messages,
            "user": user,
        },
    )


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    request: Request,
    user_id: str,
    db: DbSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user.role == UserRole.ADMIN.name:
        return templates.TemplateResponse(
            "partials/admin/user_active_status_button.html",
            {"request": request, "user": user},
        )
    user.active = False
    db.commit()

    return templates.TemplateResponse(
        "partials/admin/user_active_status_button.html",
        {"request": request, "user": user},
    )


@router.post("/users/{user_id}/activate")
def activate_user(
    request: Request,
    user_id: str,
    db: DbSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    user.active = True
    db.commit()

    return templates.TemplateResponse(
        "partials/admin/user_active_status_button.html",
        {"request": request, "user": user},
    )


@router.post("/users/{user_id}/role")
def change_user_role(
    request: Request,
    user_id: str,
    role: str,
    db: DbSession = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    user.role = role
    db.commit()

    return templates.TemplateResponse(
        "partials/admin/user_row.html",
        {"request": request, "user": user},
    )


@router.get("/users/search/")
def search_users(
    request: Request,
    search_term: str,
    db: DbSession = Depends(get_db),
):
    users = search_user(db, search_term)
    return templates.TemplateResponse(
        "partials/admin/users_rows.html",
        {"request": request, "users": users, "roles": UserRole.__members__.keys()},
    )


@router.get("/messages/{message_id}")
def get_message(
    request: Request,
    message_id: str,
    db: DbSession = Depends(get_db),
):
    message = db.query(ContactResponse).filter(ContactResponse.id == message_id).first()
    return templates.TemplateResponse(
        "partials/admin/message.html",
        {"request": request, "message": message},
    )


@router.delete("/messages/{message_id}")
def delete_message(
    message_id: str,
    db: DbSession = Depends(get_db),
):
    message = db.query(ContactResponse).filter(ContactResponse.id == message_id).first()
    db.delete(message)
    db.commit()
    return HTMLResponse()
