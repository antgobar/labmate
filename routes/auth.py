import time
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse

from config import COOKIE_KEY, MAX_COOKIE_AGE, RESERVED_USERNAMES
from services.crud import (
    get_current_user,
    get_user_by_username,
    login_user,
    logout_user,
    register_user_if_not_registered,
)
from services.database import DbSession, get_db
from services.demo import populate_demo_data_on_registration
from services.models import User
from services.resources import templates

router = APIRouter(tags=["auth"])


def error_response(endpoint: str, message: str, request: Request):
    return templates.TemplateResponse(
        f"pages/{endpoint}.html", {"request": request, "error": message}
    )


@router.post("/register")
def register(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: DbSession = Depends(get_db),
):
    if username.lower() in RESERVED_USERNAMES:
        return error_response(
            "register",
            f"Username {username} already exists, please choose another.",
            request,
        )

    user = register_user_if_not_registered(db, username, password)
    if not user:
        time.sleep(1)
        return error_response(
            "register",
            f"Username {username} already exists, please choose another.",
            request,
        )
    populate_demo_data_on_registration(db, user)
    return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: DbSession = Depends(get_db),
):
    session = login_user(db, username, password)
    if not session:
        return error_response("login", "Invalid username or password", request)

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key=COOKIE_KEY,
        value=session.session_token,
        secure=True,
        httponly=True,
        samesite="Lax",
        max_age=MAX_COOKIE_AGE,
    )
    return response


@router.get("/logout")
def logout(
    response: Response,
    user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    if user:
        logout_user(db, user)
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key=COOKIE_KEY)
    return response


@router.get("/check_username_taken")
def check_username_exists(
    request: Request, username: str, db: DbSession = Depends(get_db)
):
    user = get_user_by_username(db, username)
    if user:
        return templates.TemplateResponse(
            "partials/auth/username_taken.html",
            {"request": request, "username": username},
        )
    return templates.TemplateResponse(
        "partials/auth/username_valid.html",
        {"request": request, "username": username},
    )
