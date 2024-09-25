from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from fastapi.responses import HTMLResponse

from app.services.crud import (
    create_user_measurement,
    delete_user_measurement,
    edit_user_measurement_by_id,
    get_current_user,
    get_user_measurement_by_id,
    get_user_measurements,
    search_user_measurements,
)
from app.services.database import DbSession, get_db
from app.services.errors import (
    CSVFieldError,
    DataPointNotInEveryVariableError,
    DuplicateVariableNameError,
)
from app.services.file_handler import parse_measurements
from app.services.models import User
from app.services.resources import templates

ENDPOINT = "measurements"

router = APIRouter(prefix=f"/{ENDPOINT}", tags=[ENDPOINT])


@router.get("/")
def measurements_page(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
):
    measurements = get_user_measurements(db, user)

    return templates.TemplateResponse(
        "pages/measurements.html",
        {
            "request": request,
            "user": user,
            "measurements": measurements,
            "skip": skip,
            "limit": limit,
        },
    )


@router.get("/{measurement_id}")
def measurement_detail(
    request: Request,
    measurement_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    measurement = get_user_measurement_by_id(db, user, measurement_id)

    return templates.TemplateResponse(
        "pages/measurement_detail.html",
        {
            "request": request,
            "user": user,
            "measurement": measurement,
            "request_endpoint": str(request.base_url)
            + f"{ENDPOINT}/{measurement_id}/data/",
        },
    )


@router.put("/{measurement_id}/")
async def edit_measurement_by_id(
    request: Request,
    measurement_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    measurement = edit_user_measurement_by_id(
        db, user, measurement_id, form_data.get("name")
    )
    if not measurement:
        return Response(status_code=404)

    return templates.TemplateResponse(
        "pages/measurement_detail.html",
        {
            "request": request,
            "user": user,
            "measurement": measurement,
            "request_endpoint": str(request.base_url)
            + f"{ENDPOINT}/{measurement_id}/data/",
        },
    )


@router.get("/{measurement_id}/data/")
def measurement_data(
    measurement_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_user_measurement_by_id(db, user, measurement_id)


@router.delete("/{measurement_id}")
def delete_measurement(
    measurement_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted_measurement = delete_user_measurement(db, user, measurement_id)
    if deleted_measurement is None:
        return Response(status_code=404)
    return HTMLResponse()


def measurements_upload_response_error(request: Request, error_message: str):
    return templates.TemplateResponse(
        "partials/measurement/upload_response.html",
        {
            "request": request,
            "error": error_message,
            "upload_entity": "measurements",
        },
    )


@router.post("/")
async def upload_measurement(
    request: Request,
    name: str = Form(None),
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        return measurements_upload_response_error(request, "File must be a CSV!")

    if not name:
        name = file.filename.replace(".csv", "")
    
    try:
        measurement_data = await parse_measurements(name, file)
    except CSVFieldError:
        return measurements_upload_response_error(request, "Invalid CSV field format!")
    except DuplicateVariableNameError:
        return measurements_upload_response_error(request, "Duplicate variable names!")
    except DataPointNotInEveryVariableError:
        return measurements_upload_response_error(
            request, "Data point missing variable!"
        )

    create_user_measurement(
        db=db,
        user=user,
        measurement_data=measurement_data,
    )

    return templates.TemplateResponse(
        "partials/measurements/upload_response.html",
        {
            "request": request,
            "upload_entity": "measurements",
            "measurement_name": name,
            "data_points_count": len(measurement_data.data_points),
        },
    )


@router.post("/search/")
async def search_measurements(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    search_term = form_data.get("search_term")
    measurements = search_user_measurements(
        db,
        user,
        search_term,
    )
    return templates.TemplateResponse(
        "partials/measurements/table.html",
        {"request": request, "measurements": measurements},
    )
