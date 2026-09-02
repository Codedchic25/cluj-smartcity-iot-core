# migrations/versions/001_initial_cluj_schema.py
"""Initial Smart City Cluj database schema."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the initial Smart City Cluj database schema matching the object-relational mapping specs."""

    # ------------------------------------------------------------------
    # Sensors
    # ------------------------------------------------------------------
    op.create_table(
        "sensors",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.Text(),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "latitude",
            sa.REAL(),
            nullable=True,
        ),
        sa.Column(
            "longitude",
            sa.REAL(),
            nullable=True,
        ),
    )

    # ------------------------------------------------------------------
    # City telemetry
    # ------------------------------------------------------------------
    op.create_table(
        "city_stats",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "sensor_id",
            sa.Integer(),
            sa.ForeignKey("sensors.id"),
            nullable=False,
        ),
        sa.Column(
            "temperature",
            sa.REAL(),
            nullable=True,
        ),
        sa.Column(
            "noise_level",
            sa.REAL(),
            nullable=True,
        ),
        sa.Column(
            "traffic_load",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "air_quality",
            sa.REAL(),
            nullable=True,
        ),
        sa.Column(
            "soil_moisture",
            sa.REAL(),
            nullable=True,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(),  # Corectat de la sa.sa.DateTime()
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Index optimizat pentru accelerarea interogărilor analitice
    op.create_index(
        "idx_city_stats_sensor_timestamp",
        "city_stats",
        ["sensor_id", "timestamp"],
    )

    # ------------------------------------------------------------------
    # Alert settings
    # ------------------------------------------------------------------
    op.create_table(
        "settings",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "temp_limit",
            sa.REAL(),
            nullable=False,
            server_default=sa.text("32.0"),
        ),
        sa.Column(
            "noise_limit",
            sa.REAL(),
            nullable=False,
            server_default=sa.text("75.0"),
        ),
        sa.Column(
            "air_limit",
            sa.REAL(),
            nullable=False,
            server_default=sa.text("80.0"),
        ),
        sa.Column(
            "soil_limit",
            sa.REAL(),
            nullable=False,
            server_default=sa.text("35.0"),
        ),
    )

    # ------------------------------------------------------------------
    # Application users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "username",
            sa.Text(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "password",
            sa.Text(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop the initial Smart City Cluj database schema."""
    op.drop_index(
        "idx_city_stats_sensor_timestamp",
        table_name="city_stats",
    )
    op.drop_table("users")
    op.drop_table("settings")
    op.drop_table("city_stats")
    op.drop_table("sensors")
