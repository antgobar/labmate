from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from services.crud import get_current_user
from services.database import DbSession, get_db
from services.models import ContactResponse
from services.resources import templates
from services.schemas import ContactForm

router = APIRouter(prefix="/contact", tags=["contact"])


@router.get("/messages")
def contact_form():
    return RedirectResponse("/contact")


@router.post("/messages")
async def contact_form_submission(
    request: Request,
    db: DbSession = Depends(get_db),
    user: str = Depends(get_current_user),
):
    form_data = await request.form()

    if form_data.get("website"):
        return RedirectResponse("/")

    try:
        contact_data = ContactForm(
            name=form_data.get("name"),
            email=form_data.get("email"),
            message=form_data.get("message"),
        )
    except ValidationError as e:
        error_messages = [error["ctx"].get("reason") for error in e.errors()]
        response = templates.TemplateResponse(
            "pages/contact.html",
            {"request": request, "error_messages": error_messages, "user": user},
        )
        response.headers["HX-Target"] = "main"
        return response

    contact = ContactResponse(
        name=contact_data.name,
        email=contact_data.email,
        message=contact_data.message,
        created_at=datetime.now(tz=UTC),
    )

    db.add(contact)
    db.commit()

    response = templates.TemplateResponse(
        "pages/contact.html",
        {
            "request": request,
            "success_message": "Thank you for your message! We will get back to you soon.",
            "user": user,
        },
    )
    response.headers["HX-Target"] = "main"
    return response
