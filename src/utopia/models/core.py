"""core.operators and core.devices ORM models.

Matches: Utopia Formal Architecture DB etc.md section 5.
"""

import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base


class Operator(Base):
    __tablename__ = "operators"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    timezone: Mapped[str] = mapped_column(Text, nullable=False)
    locale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    devices: Mapped[list["Device"]] = relationship(back_populates="operator")


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("core.operators.id"), nullable=False)
    device_name: Mapped[str] = mapped_column(Text, nullable=False)
    device_type: Mapped[str] = mapped_column(Text, nullable=False)
    public_key_fingerprint: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_seen_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    operator: Mapped["Operator"] = relationship(back_populates="devices")
