"""SQLAlchemy ORM models for the Smart City Cluj-Napoca IoT platform."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import REAL, TEXT, DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


class Sensor(Base):
    """Urban IoT sensor location descriptor mapping core geometry metadata."""

    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    latitude: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    telemetry: Mapped[list["CityStat"]] = relationship(
        back_populates="sensor",
        cascade="all, delete-orphan",
    )


class CityStat(Base):
    """Telemetry metrics persistent layer collected from active urban nodes."""

    __tablename__ = "city_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    sensor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sensors.id"),
        nullable=False,
        index=True,
    )

    temperature: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    noise_level: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    traffic_load: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    air_quality: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    soil_moisture: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    sensor: Mapped["Sensor"] = relationship(
        back_populates="telemetry",
    )

    __table_args__ = (
        Index(
            "idx_city_stats_sensor_timestamp",
            "sensor_id",
            "timestamp",
        ),
    )


class Setting(Base):
    """Configurable alert thresholds database persistent blueprint mapping metrics constants."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    temp_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=32.0,
    )

    noise_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=75.0,
    )

    air_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=80.0,
    )

    soil_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=35.0,
    )


class User(Base):
    """Application identities used specifically by the secure bcrypt entry authenticator threads."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        TEXT,
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    password: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
