# -*- coding: utf-8 -*-

import datetime
from datetime import date

from sqlmodel import Field, SQLModel

from database import engine


class Appl_user(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    company_email: str = Field(nullable=False)
    position: str = Field(nullable=False)
    department: str = Field(nullable=False)
    access_level: str = Field(nullable=False)  # superuser, admin, employee
    status: str  # current, former
    start_date: date = Field(default_factory=date.today, nullable=False)  # current
    end_date: date | None = None


class Users(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    surname: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    telegram: str = Field(nullable=False)
    company_email: str = Field(nullable=False)
    valid_time: str = Field(default_factory=datetime.datetime.now, nullable=True)
    vert_menu: int = Field(nullable=False)
    delay_set: int = Field(nullable=False)
    hashed_pass: str = Field(nullable=False)

class Contact(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    long_name: str = Field(nullable=False)
    position: str = Field(nullable=False)
    department: str = Field(nullable=False)
    phone: str = Field(nullable=True)
    cellphone: str = Field(nullable=True)
    home_phone: str = Field(nullable=True)
    email: str = Field(nullable=True)
    birthday: str = Field(nullable=True)
    expat: str = Field(nullable=True)
    office: str = Field(nullable=True)

class Visit_log(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    company_email: str = Field(nullable=False)
    login_time: str = Field(default_factory=datetime.datetime.now, nullable=True)


class Project(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    short_name: str = Field(nullable=False)
    full_name: str = Field(nullable=True)
    client: str = Field(nullable=True)
    manager: str = Field(nullable=True)
    responsible_el: str = Field(nullable=True)
    status: str = Field(nullable=False)
    assignments: str = Field(nullable=True)
    tech_conditions: str = Field(nullable=True)
    surveys: str = Field(nullable=True)
    mdr: str = Field(nullable=False)
    notes: str = Field(nullable=True)


class Assignment(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    project: str = Field(nullable=False)
    set_draw: str = Field(nullable=False)
    stage: str = Field(nullable=False)
    in_out: str = Field(nullable=False)
    speciality: str = Field(nullable=False)
    date: str = Field(default_factory=date.today, nullable=False)
    description: str = Field(nullable=False)
    link: str = Field(nullable=False)
    backup_copy: str = Field(nullable=False)
    source: str = Field(nullable=False)
    log: str = Field(nullable=False)
    comments: str = Field(nullable=False)
    added_by: str = Field(nullable=False)


class Set_draw(SQLModel, table=True):
    __table_args__ = {'extend_existing': True}
    id: int | None = Field(default=None, primary_key=True)
    project: str = Field(nullable=False)
    set_name: str = Field(nullable=False)
    coordinator: str = Field(nullable=True)
    performer: str = Field(nullable=True)
    stage: str = Field(nullable=False)
    revision: str = Field(nullable=False)
    start_date: str = Field(default_factory=date.today, nullable=True)
    current_status: str = Field(nullable=False)
    request_date: str = Field(default_factory=date.today, nullable=True)
    trans_num: str = Field(nullable=True)
    trans_date: str = Field(default_factory=date.today, nullable=True)
    notes: str = Field(nullable=True)
    aux: str = Field(nullable=False)


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"
#
# engine = create_engine(sqlite_url, echo=True)

SQLModel.metadata.create_all(engine)



