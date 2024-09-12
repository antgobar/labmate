from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from services import schemas
from services.crud import (
    archive_user_experiment_by_id,
    create_user_experiment,
    delete_user_experiment_by_id,
    edit_user_experiment_by_id,
    get_current_user,
    get_user_archived_experiments,
    get_user_experiment_by_id,
    get_user_experiments,
    get_user_samples_by_family,
    link_sample_and_experiment,
    search_unique_lab_sample_families,
    search_user_experiments,
    unarchive_user_experiment_by_id,
    unlink_sample_and_experiment,
)
from services.database import DbSession, get_db
from services.models import User
from services.resources import templates

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/")
def get_experiments_page(
    request: Request,
    user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    return templates.TemplateResponse(
        "pages/experiments.html",
        {
            "request": request,
            "user": user,
            "experiments": get_user_experiments(db, user, skip, limit),
            "skip": skip,
            "limit": limit,
        },
    )


@router.post("/")
async def create_experiments(
    request: Request,
    user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    form_data = await request.form()

    if not any(form_data.values()):
        return templates.TemplateResponse(
            "partials/experiments/row.html",
            {"request": request, "experiment": None},
        )

    experiment = create_user_experiment(
        db=db,
        user=user,
        **form_data,
    )

    return templates.TemplateResponse(
        "partials/experiments/row.html",
        {"request": request, "experiment": experiment},
    )


@router.get("/{experiment_id}")
def get_experiment_by_id(
    request: Request,
    experiment_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    experiment = get_user_experiment_by_id(db, user, experiment_id)
    attached_samples = experiment.lab_samples

    if experiment is None:
        return RedirectResponse("/experiments", status_code=303)

    return templates.TemplateResponse(
        "pages/experiment_detail.html",
        {
            "request": request,
            "experiment": experiment,
            "user": user,
            "experiment_lab_sample_families": list(
                {sample.family for sample in attached_samples}
            ),
        },
    )


@router.put("/{experiment_id}/")
async def edit_experiment_by_id(
    request: Request,
    experiment_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    updated_experiment = edit_user_experiment_by_id(
        db, user, experiment_id, schemas.Experiment(**form_data)
    )
    if not updated_experiment:
        return Response(status_code=404)

    return templates.TemplateResponse(
        "partials/experiments/detail.html",
        {"request": request, "experiment": updated_experiment},
    )


@router.post("/{experiment_id}/archive/")
def archive_experiment_by_id(
    experiment_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    experiment = archive_user_experiment_by_id(db, user, experiment_id)
    if experiment is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.post("/{experiment_id}/unarchive/")
def unarchive_experiment_by_id(
    experiment_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    experiment = unarchive_user_experiment_by_id(db, user, experiment_id)
    if experiment is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.delete("/{experiment_id}")
def delete_experiment_by_id(
    experiment_id: int,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted_experiment = delete_user_experiment_by_id(db, user, experiment_id)
    if deleted_experiment is None:
        return Response(status_code=404)
    return HTMLResponse()


@router.get("/archived/")
def get_archived_experiments(
    request: Request,
    user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    archived_experiments = get_user_archived_experiments(db, user)
    return templates.TemplateResponse(
        "partials/experiments/table.html",
        {"request": request, "experiments": archived_experiments, "archived": True},
    )


@router.post("/search/")
async def search_experiments(
    request: Request,
    linkable: bool = False,
    sample_id: int = None,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    form_data = await request.form()
    search_term = form_data.get("search_term")
    experiments = search_user_experiments(
        db,
        user,
        search_term,
        exclude_sample_id=sample_id,
    )

    return templates.TemplateResponse(
        "partials/experiments/table.html",
        {
            "request": request,
            "experiments": experiments,
            "linkable": linkable,
            "is_linked": True,
            "sample_id": sample_id,
        },
    )


@router.post("/{experiment_id}/link/")
def link_sample(
    request: Request,
    experiment_id: int,
    entity_type: str,
    entity_identifier: int | str,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if entity_type == "sample":
        experiment, sample = link_sample_and_experiment(
            db, user, experiment_id, entity_identifier
        )
        if experiment is None or sample is None:
            return Response(status_code=404)

        return templates.TemplateResponse(
            "pages/sample_detail.html",
            {"request": request, "sample": sample, "user": user},
        )

    if entity_type == "sample_family":
        samples_in_family = get_user_samples_by_family(db, user, entity_identifier)
        experiment = get_user_experiment_by_id(db, user, experiment_id)
        new_samples = list(
            {
                sample
                for sample in samples_in_family
                if sample not in experiment.lab_samples
            }
        )
        experiment.lab_samples.extend(new_samples)
        db.commit()

        return templates.TemplateResponse(
            "pages/experiment_detail.html",
            {
                "request": request,
                "experiment": experiment,
                "user": user,
                "experiment_lab_sample_families": list(
                    {sample.family for sample in experiment.lab_samples}
                ),
            },
        )

    return Response(status_code=404)


@router.post("/{experiment_id}/unlink/")
def unlink_sample(
    request: Request,
    experiment_id: int,
    entity_type: str,
    entity_identifier: int | str,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if entity_type == "sample":
        experiment, _ = unlink_sample_and_experiment(
            db, user, experiment_id, entity_identifier
        )
        if experiment is None:
            return Response(status_code=404)

        return templates.TemplateResponse(
            "pages/experiment_detail.html",
            {"request": request, "experiment": experiment, "user": user},
        )

    if entity_type == "sample_family":
        experiment = get_user_experiment_by_id(db, user, experiment_id)
        samples_to_remove = [
            sample
            for sample in experiment.lab_samples
            if sample.family.lower() == entity_identifier.lower()
        ]
        for sample in samples_to_remove:
            experiment.lab_samples.remove(sample)
        db.commit()

        return HTMLResponse()

    return Response(status_code=404)


@router.post("/{experiment_id}/families/")
async def search_samples_by_family(
    request: Request,
    experiment_id: int,
    search_term: str = Form(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    samples = search_unique_lab_sample_families(db, user, search_term)
    return templates.TemplateResponse(
        "partials/samples/families.html",
        {"request": request, "samples": samples, "experiment_id": experiment_id},
    )
