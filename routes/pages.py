from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from services.crud import get_current_user
from services.models import User
from services.resources import templates

router = APIRouter(tags=["pages"])


@router.get("/")
def get_index_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/home.html",
        {"request": request, "user": user},
    )


@router.get("/register")
def get_register_page(request: Request, user: User = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard/", status_code=303)
    return templates.TemplateResponse(
        "pages/register.html",
        {"request": request, "user": user},
    )


@router.get("/login")
def get_login(request: Request, user: User = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard/", status_code=303)
    return templates.TemplateResponse(
        "pages/login.html",
        {"request": request, "user": user},
    )


@router.get("/about")
def get_about_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/about.html",
        {"request": request, "user": user},
    )


@router.get("/pricing")
def get_pricing_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/pricing.html",
        {"request": request, "user": user},
    )


@router.get("/contact")
def get_contact_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "pages/contact.html",
        {"request": request, "user": user},
    )
