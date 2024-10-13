from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.services.crud import get_current_user
from app.services.models import User
from app.services.resources import templates

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
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "pages/register.html",
        {"request": request, "user": user},
    )


@router.get("/login")
def get_login(request: Request, user: User = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(
        "pages/login.html",
        {"request": request, "user": user},
    )


@router.get("/about")
def get_about_page():
    return RedirectResponse(url="/#about-section", status_code=301)


@router.get("/pricing")
def get_pricing_page():
    return RedirectResponse(url="/#pricing-section", status_code=301)


@router.get("/contact")
def get_contact_page():
    return RedirectResponse(url="/#contact-section", status_code=301)


@router.get("/features")
def get_features_page():
    return RedirectResponse(url="/#features-section", status_code=301)
