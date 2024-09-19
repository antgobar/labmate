from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from services.crud import get_current_user
from services.database import DbSession, get_db
from services.models import ContactResponse
from services.schemas import ContactForm

router = APIRouter(prefix="/contact", tags=["contact"])


@router.get("/messages")
def contact_form():
    return RedirectResponse("/contact")


@router.post("/messages")
async def contact_form_submission(
    request: Request,
    db: DbSession = Depends(get_db),
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
    except ValidationError:
        RedirectResponse("/")

    contact = ContactResponse(
        name=contact_data.name,
        email=contact_data.email,
        message=contact_data.message,
        created_at=datetime.now(tz=UTC),
    )

    db.add(contact)
    db.commit()

    RedirectResponse("/")
