from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from services import schemas
from services.crud import (
    add_measurements_to_user_sample,
    archive_user_sample_by_id,
    create_user_sample,
    delete_user_sample_by_id,
    edit_user_sample_by_id,
    get_current_user,
    get_user_archived_samples,
    get_user_sample_by_id,
    get_user_samples,
    search_user_samples,
    unarchive_user_sample_by_id,
)
from services.database import DbSession, get_db
from services.errors import (
    CSVFieldError,
    DataPointNotInEveryVariableError,
    DuplicateVariableNameError,
)
from services.file_handler import parse_measurements, parse_user_samples
from services.models import LabSample, User
from services.resources import templates

router = APIRouter(prefix="/samples", tags=["samples"])


@router.get("/")
async def get_user_samples_page(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    samples = get_user_samples(db, user, skip, limit)
    return templates.TemplateResponse(
        "pages/samples.html",
        {
            "request": request,
            "user": user,
            "samples": samples,
            "skip": skip,
            "limit": limit,
        },
    )


@router.get("/{sample_id}")
async def get_sample_by_id(
    request: Request,
    sample_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sample = get_user_sample_by_id(db, user, sample_id)
    if sample is None:
        return RedirectResponse("/samples", status_code=303)

    return templates.TemplateResponse(
        "pages/sample_detail.html",
        {
            "request": request,
            "user": user,
            "sample": sample,
            "queries": f"?linkable=true&sample_id={sample_id}",
            "sample_id": sample_id,
            "linkable": True,
        },
    )


@router.post("/")
async def create_sample(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    if not any(form_data.values()):
        return templates.TemplateResponse(
            "partials/samples/row.html",
            {"request": request, "sample": None},
        )

    sample = create_user_sample(
        db=db,
        user=user,
        sample_data=schemas.LabSample.model_validate(form_data),
    )
    return templates.TemplateResponse(
        "partials/samples/row.html",
        {"request": request, "sample": sample},
    )


@router.put("/{sample_id}/")
async def edit_sample_by_id(
    request: Request,
    sample_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    updated_sample = edit_user_sample_by_id(
        db, user, sample_id, schemas.LabSample(**form_data)
    )
    if not updated_sample:
        return Response(status_code=404)

    return templates.TemplateResponse(
        "partials/samples/detail.html",
        {"request": request, "sample": updated_sample},
    )


@router.post("/{sample_id}/archive/")
def archive_sample_by_id(
    sample_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sample = archive_user_sample_by_id(db, user, sample_id)
    if sample is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.post("/{sample_id}/unarchive/")
async def unarchive_sample_by_id(
    sample_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sample = unarchive_user_sample_by_id(db, user, sample_id)
    if sample is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.delete("/{sample_id}")
async def delete_sample_by_id(
    sample_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted_sample = delete_user_sample_by_id(db, user, sample_id)
    if deleted_sample is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.get("/archived/")
async def get_archived_samples(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    archived_samples = get_user_archived_samples(db, user)
    return templates.TemplateResponse(
        "partials/samples/table.html",
        {"request": request, "samples": archived_samples, "archived": True},
    )


@router.post("/upload/")
async def upload_samples_file(
    request: Request,
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename.endswith(".csv"):
        return templates.TemplateResponse(
            "partials/samples/upload_response.html",
            {
                "request": request,
                "error": "File must be a CSV!",
            },
        )

    samples = await parse_user_samples(file)

    for sample in samples:
        if sample is not None:
            create_user_sample(db, user, sample)

    return templates.TemplateResponse(
        "partials/samples/upload_response.html",
        {
            "request": request,
            "upload_entity": "samples",
            "samples_created_count": len(samples),
            "sample_created_error_count": samples.count(None),
        },
    )


@router.post("/search/")
async def search_samples(
    request: Request,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    search_term = form_data.get("search_term")
    samples = search_user_samples(
        db,
        user,
        search_term,
    )
    return templates.TemplateResponse(
        "partials/samples/table.html",
        {"request": request, "samples": samples},
    )


def measurements_upload_response_error(
    request: Request, sample: LabSample, error_message: str
):
    return templates.TemplateResponse(
        "partials/samples/upload_response.html",
        {
            "request": request,
            "error": error_message,
            "upload_entity": "measurements",
            "sample": sample,
        },
    )


@router.post("/{sample_id}/measurements/")
async def upload_sample_measurement(
    request: Request,
    sample_id: int,
    name: Annotated[str, Form()] | None = None,
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not name:
        name = file.filename.replace(".csv", "")

    sample = get_user_sample_by_id(db, user, sample_id)

    if not file.filename.endswith(".csv"):
        return measurements_upload_response_error(
            request, sample, "File must be a CSV!"
        )

    if sample is None:
        return measurements_upload_response_error(request, sample, "Sample not found!")

    try:
        measurement_data = await parse_measurements(name, file)
    except CSVFieldError:
        return measurements_upload_response_error(
            request, sample, "Invalid CSV field format!"
        )
    except DuplicateVariableNameError:
        return measurements_upload_response_error(
            request, sample, "Duplicate variable names!"
        )
    except DataPointNotInEveryVariableError:
        return measurements_upload_response_error(
            request, sample, "Data point missing variable!"
        )

    add_measurements_to_user_sample(
        db=db,
        user=user,
        sample_id=sample_id,
        measurement_data=measurement_data,
    )

    return templates.TemplateResponse(
        "partials/samples/upload_response.html",
        {
            "request": request,
            "upload_entity": "measurements",
            "sample": sample,
            "measurement_name": name,
            "data_points_count": len(measurement_data.data_points),
        },
    )
