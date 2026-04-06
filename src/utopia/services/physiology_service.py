"""PhysiologyService — bounded-context service for WHOOP data and derived features.

WHOOP data is a first-class body-state data source. This service ingests raw
provider payloads and stores derived physiological features that downstream
subsystems (State Estimator, Blocker Classifier) use as physiological priors.

Upsert methods are used for WHOOP objects since the provider may re-send
records with updated scores (e.g. SCORED → PENDING_SCORE → SCORED).
"""

import datetime
import uuid as _uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from utopia.models.physiology import (
    BiomarkerPanel,
    PhysiologyFeature,
    WhoopBodyMeasurement,
    WhoopConnection,
    WhoopCycle,
    WhoopRecovery,
    WhoopSleep,
    WhoopWorkout,
)
from utopia.schemas.physiology import (
    BiomarkerPanelCreate,
    PhysiologyFeatureCreate,
    WhoopBodyMeasurementCreate,
    WhoopConnectionCreate,
    WhoopCycleCreate,
    WhoopRecoveryCreate,
    WhoopSleepCreate,
    WhoopWorkoutCreate,
)


class PhysiologyService:
    """Service for the Physiology bounded context.

    Owns ID generation and write semantics for all physiology tables.
    WHOOP objects use upsert semantics on provider IDs to handle
    re-deliveries and score updates from the WHOOP API.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    # ------------------------------------------------------------------
    # WHOOP Connections
    # ------------------------------------------------------------------

    async def connect_whoop(self, data: WhoopConnectionCreate) -> WhoopConnection:
        conn = WhoopConnection(
            id=uuid7(),
            operator_id=data.operator_id,
            oauth_connection_id=data.oauth_connection_id,
            scope_granted=data.scope_granted,
            last_sync_at=data.last_sync_at,
        )
        self._session.add(conn)
        await self._session.flush()
        return conn

    async def get_whoop_connection(self, connection_id: _uuid.UUID) -> WhoopConnection | None:
        return await self._session.get(WhoopConnection, connection_id)

    # ------------------------------------------------------------------
    # WHOOP Body Measurements
    # ------------------------------------------------------------------

    async def record_body_measurement(
        self, data: WhoopBodyMeasurementCreate
    ) -> WhoopBodyMeasurement:
        measurement = WhoopBodyMeasurement(
            id=uuid7(),
            operator_id=data.operator_id,
            measured_at=data.measured_at,
            height_cm=data.height_cm,
            weight_kg=data.weight_kg,
            max_heart_rate=data.max_heart_rate,
            source_payload=data.source_payload,
        )
        self._session.add(measurement)
        await self._session.flush()
        return measurement

    # ------------------------------------------------------------------
    # WHOOP Cycles
    # ------------------------------------------------------------------

    async def upsert_cycle(self, data: WhoopCycleCreate) -> WhoopCycle:
        """Insert or update a WHOOP cycle on provider_cycle_id conflict."""
        stmt = (
            pg_insert(WhoopCycle)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                provider_cycle_id=data.provider_cycle_id,
                whoop_user_id=data.whoop_user_id,
                cycle_start=data.cycle_start,
                cycle_end=data.cycle_end,
                timezone_offset=data.timezone_offset,
                score_state=data.score_state,
                strain=data.strain,
                kilojoule=data.kilojoule,
                average_heart_rate=data.average_heart_rate,
                max_heart_rate=data.max_heart_rate,
                source_payload=data.source_payload,
            )
            .on_conflict_do_update(
                constraint="uq_whoop_cycles_provider_cycle_id",
                set_={
                    "cycle_end": data.cycle_end,
                    "score_state": data.score_state,
                    "strain": data.strain,
                    "kilojoule": data.kilojoule,
                    "average_heart_rate": data.average_heart_rate,
                    "max_heart_rate": data.max_heart_rate,
                    "source_payload": data.source_payload,
                },
            )
            .returning(WhoopCycle)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    # ------------------------------------------------------------------
    # WHOOP Sleeps
    # ------------------------------------------------------------------

    async def upsert_sleep(self, data: WhoopSleepCreate) -> WhoopSleep:
        """Insert or update a WHOOP sleep record on provider_sleep_id conflict."""
        stmt = (
            pg_insert(WhoopSleep)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                provider_sleep_id=data.provider_sleep_id,
                provider_cycle_id=data.provider_cycle_id,
                sleep_start=data.sleep_start,
                sleep_end=data.sleep_end,
                sleep_performance_pct=data.sleep_performance_pct,
                total_in_bed_ms=data.total_in_bed_ms,
                total_asleep_ms=data.total_asleep_ms,
                slow_wave_ms=data.slow_wave_ms,
                rem_ms=data.rem_ms,
                light_ms=data.light_ms,
                awake_ms=data.awake_ms,
                source_payload=data.source_payload,
            )
            .on_conflict_do_update(
                constraint="uq_whoop_sleeps_provider_sleep_id",
                set_={
                    "sleep_end": data.sleep_end,
                    "sleep_performance_pct": data.sleep_performance_pct,
                    "total_in_bed_ms": data.total_in_bed_ms,
                    "total_asleep_ms": data.total_asleep_ms,
                    "slow_wave_ms": data.slow_wave_ms,
                    "rem_ms": data.rem_ms,
                    "light_ms": data.light_ms,
                    "awake_ms": data.awake_ms,
                    "source_payload": data.source_payload,
                },
            )
            .returning(WhoopSleep)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    # ------------------------------------------------------------------
    # WHOOP Recoveries
    # ------------------------------------------------------------------

    async def upsert_recovery(self, data: WhoopRecoveryCreate) -> WhoopRecovery:
        """Insert or update a WHOOP recovery on (operator_id, cycle_id, sleep_id) conflict."""
        stmt = (
            pg_insert(WhoopRecovery)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                provider_cycle_id=data.provider_cycle_id,
                provider_sleep_id=data.provider_sleep_id,
                whoop_user_id=data.whoop_user_id,
                recorded_at=data.recorded_at,
                updated_at_source=data.updated_at_source,
                score_state=data.score_state,
                recovery_score=data.recovery_score,
                resting_heart_rate=data.resting_heart_rate,
                hrv_rmssd_milli=data.hrv_rmssd_milli,
                spo2_percentage=data.spo2_percentage,
                skin_temp_celsius=data.skin_temp_celsius,
                user_calibrating=data.user_calibrating,
                source_payload=data.source_payload,
            )
            .on_conflict_do_update(
                constraint="uq_whoop_recoveries_operator_cycle_sleep",
                set_={
                    "updated_at_source": data.updated_at_source,
                    "score_state": data.score_state,
                    "recovery_score": data.recovery_score,
                    "resting_heart_rate": data.resting_heart_rate,
                    "hrv_rmssd_milli": data.hrv_rmssd_milli,
                    "spo2_percentage": data.spo2_percentage,
                    "skin_temp_celsius": data.skin_temp_celsius,
                    "user_calibrating": data.user_calibrating,
                    "source_payload": data.source_payload,
                },
            )
            .returning(WhoopRecovery)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    # ------------------------------------------------------------------
    # WHOOP Workouts
    # ------------------------------------------------------------------

    async def upsert_workout(self, data: WhoopWorkoutCreate) -> WhoopWorkout:
        """Insert or update a WHOOP workout on provider_workout_id conflict."""
        stmt = (
            pg_insert(WhoopWorkout)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                provider_workout_id=data.provider_workout_id,
                workout_type=data.workout_type,
                workout_start=data.workout_start,
                workout_end=data.workout_end,
                strain=data.strain,
                average_heart_rate=data.average_heart_rate,
                max_heart_rate=data.max_heart_rate,
                source_payload=data.source_payload,
            )
            .on_conflict_do_update(
                constraint="uq_whoop_workouts_provider_workout_id",
                set_={
                    "workout_end": data.workout_end,
                    "strain": data.strain,
                    "average_heart_rate": data.average_heart_rate,
                    "max_heart_rate": data.max_heart_rate,
                    "source_payload": data.source_payload,
                },
            )
            .returning(WhoopWorkout)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    # ------------------------------------------------------------------
    # Physiology Features
    # ------------------------------------------------------------------

    async def store_physiology_feature(
        self, data: PhysiologyFeatureCreate
    ) -> PhysiologyFeature:
        """Upsert a derived physiological feature for a given date and name."""
        stmt = (
            pg_insert(PhysiologyFeature)
            .values(
                id=uuid7(),
                operator_id=data.operator_id,
                feature_date=data.feature_date,
                feature_name=data.feature_name,
                feature_value=data.feature_value,
                feature_json=data.feature_json,
                confidence=data.confidence,
                computed_at=data.computed_at,
            )
            .on_conflict_do_update(
                constraint="uq_physiology_features_operator_date_name",
                set_={
                    "feature_value": data.feature_value,
                    "feature_json": data.feature_json,
                    "confidence": data.confidence,
                    "computed_at": data.computed_at,
                },
            )
            .returning(PhysiologyFeature)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def get_latest_features(
        self,
        operator_id: _uuid.UUID,
        feature_date: datetime.date | None = None,
    ) -> list[PhysiologyFeature]:
        stmt = select(PhysiologyFeature).where(
            PhysiologyFeature.operator_id == operator_id
        )
        if feature_date is not None:
            stmt = stmt.where(PhysiologyFeature.feature_date == feature_date)
        stmt = stmt.order_by(
            PhysiologyFeature.feature_date.desc(),
            PhysiologyFeature.feature_name,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Biomarker Panels
    # ------------------------------------------------------------------

    async def record_biomarker_panel(
        self, data: BiomarkerPanelCreate
    ) -> BiomarkerPanel:
        panel = BiomarkerPanel(
            id=uuid7(),
            operator_id=data.operator_id,
            panel_date=data.panel_date,
            provider=data.provider,
            panel_type=data.panel_type,
            summary=data.summary,
            source_payload=data.source_payload,
        )
        self._session.add(panel)
        await self._session.flush()
        return panel
