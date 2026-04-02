"""integration.oauth_connections, integration.permissions, integration.webhook_receipts.

Matches: Utopia Formal Architecture DB etc.md sections 5 and 8.
"""

import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, LargeBinary, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from utopia.db import Base
from utopia.enums import OAuthStatus, ProcessingStatus


class OAuthConnection(Base):
    __tablename__ = "oauth_connections"
    __table_args__ = {"schema": "integration"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("core.operators.id"), nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    provider_user_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")
    status: Mapped[OAuthStatus] = mapped_column(
        Enum(OAuthStatus, name="oauth_status", schema="core", create_type=False),
        nullable=False,
    )
    encrypted_access_token: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    encrypted_refresh_token: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    token_expires_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, server_default="{}")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    operator: Mapped["Operator"] = relationship(  # noqa: F821
        "Operator", foreign_keys=[operator_id]
    )


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "integration"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    operator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("core.operators.id"), nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    permission_key: Mapped[str] = mapped_column(Text, nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    granted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    operator: Mapped["Operator"] = relationship(  # noqa: F821
        "Operator", foreign_keys=[operator_id]
    )


class WebhookReceipt(Base):
    __tablename__ = "webhook_receipts"
    __table_args__ = {"schema": "integration"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    provider_user_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_object_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    signature_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    headers: Mapped[dict] = mapped_column(JSONB, nullable=False)
    raw_body: Mapped[dict] = mapped_column(JSONB, nullable=False)
    processed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status", schema="core", create_type=False),
        nullable=False,
        server_default="pending",
    )
