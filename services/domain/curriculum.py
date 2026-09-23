"""Curriculum catalog foundation. No invented academic outcome mapping."""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from services.database import Base


class Level(Base):
    __tablename__ = "levels"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    level_id: Mapped[UUID] = mapped_column(ForeignKey("levels.id"))
    name: Mapped[str] = mapped_column(String(80), unique=True)


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"))
    name: Mapped[str] = mapped_column(String(160), unique=True)


class Concept(Base):
    __tablename__ = "concepts"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("topics.id"))
    name: Mapped[str] = mapped_column(String(200))
    syllabus_reference: Mapped[str]
    synthetic: Mapped[bool]


class Competency(Base):
    __tablename__ = "competencies"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
