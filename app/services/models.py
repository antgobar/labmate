import secrets
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from app.services.database import Base, engine


class SubscriptionLevel(Enum):
    STUDENT = "student"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class DataAccessLevel(Enum):
    VIEWER = "viewer"
    EXPERIMENTER = "experimenter"
    ORG_OWNER = "org_owner"


class UserRole(Enum):
    ADMIN = "admin"
    ORG_OWNER = "org_owner"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref="user_sessions")
    session_token = Column(String(255), unique=True, nullable=False)

    def __init__(self, user_id: int):
        self.session_token = self.generate_session_token()
        self.user_id = user_id

    @staticmethod
    def generate_session_token():
        return secrets.token_hex(64)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String(200))
    active = Column(Boolean, default=True)
    role = Column(String(50), default=UserRole.RESEARCHER.name, nullable=False)
    samples = relationship("LabSample", backref="users")
    experiments = relationship("Experiment", backref="users")
    measurements = relationship("Measurement", backref="users")
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=True)


experiment_samples = Table(
    "experiment_samples",
    Base.metadata,
    Column("experiment_id", Integer, ForeignKey("experiments.id"), primary_key=True),
    Column("lab_sample_id", Integer, ForeignKey("lab_samples.id"), primary_key=True),
)


class LabSample(Base):
    __tablename__ = "lab_samples"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    formula = Column(String(50))
    label = Column(String(50))
    format = Column(String(50))
    family = Column(String(50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    measurements = relationship("Measurement", backref="lab_samples")
    experiments = relationship(
        "Experiment", secondary=experiment_samples, back_populates="lab_samples"
    )


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    name = Column(String(50))
    description = Column(String(200))
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lab_samples = relationship(
        "LabSample", secondary=experiment_samples, back_populates="experiments"
    )


class Measurement(Base):
    __tablename__ = "measurements"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    name = Column(String(50))
    variables = Column(JSON)
    data_points = Column(JSON)
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lab_sample_id = Column(Integer, ForeignKey("lab_samples.id"))


# class Method(Base):
#     __tablename__ = "methods"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     name = Column(String(50))
#     description = Column(String(200))
#     step = Column(Integer)
#     experiment_id = Column(Integer, ForeignKey("experiments.id"))


class ContactResponse(Base):
    __tablename__ = "contact_responses"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String(50), index=True)
    email = Column(String(50), index=True)
    message = Column(String(2000))
    created_at = Column(DateTime)


Base.metadata.create_all(bind=engine)

ModelBase = Base
