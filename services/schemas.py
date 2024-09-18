from typing import Any

from pydantic import BaseModel, EmailStr, model_validator

from services.errors import DataPointNotInEveryVariableError, DuplicateVariableNameError


class LabSample(BaseModel):
    formula: str
    label: str
    format: str
    family: str


class Experiment(BaseModel):
    name: str
    description: str


class Variable(BaseModel):
    name: str
    unit: str


class Measurements(BaseModel):
    name: str
    variables: list[Variable]
    data_points: list[dict[str, Any]]

    @model_validator(mode="after")
    def validate_data_contains_variables(self):
        names = [variable.name for variable in self.variables]
        if len(names) != len(set(names)):
            raise DuplicateVariableNameError

        if set(self.data_points[0].keys()) != set(names):
            raise DataPointNotInEveryVariableError


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str
