import csv
from io import StringIO

import polars as pl
from fastapi import UploadFile
from pydantic import ValidationError

from app.services import schemas
from app.services.errors import CSVFieldError


async def parse_user_samples(contents) -> list[schemas.LabSample]:
    csv_data = StringIO(contents.decode("utf-8"))
    csv_reader = csv.DictReader(csv_data)

    return [parse_csv_sample_row(row) for row in csv_reader]


def parse_csv_sample_row(row) -> schemas.LabSample | None:
    try:
        sample_data = schemas.LabSample(
            formula=row.get("formula"),
            label=row.get("label"),
            format=row.get("format"),
            family=row.get("family"),
        )
        return sample_data
    except ValidationError:
        return None


async def parse_measurements(name: str, file: UploadFile) -> schemas.Measurements:
    contents = await file.read()
    await file.close()

    csv_data = StringIO(contents.decode("utf-8"))
    csv_reader = csv.DictReader(csv_data)

    variables = [
        validate_variable_name__and_unit(field) for field in csv_reader.fieldnames
    ]

    df = pl.DataFrame(csv_reader)
    df = df.rename({col: col.split()[0] for col in df.columns})

    return schemas.Measurements(
        name=name,
        variables=variables,
        data_points=df.to_dicts(),
    )


def validate_variable_name__and_unit(field) -> schemas.Variable:
    field = field.strip().replace(")", "").replace("(", "")
    try:
        variable_name, unit = field.split(" ")
        return schemas.Variable(name=variable_name, unit=unit)
    except ValueError:
        raise CSVFieldError
