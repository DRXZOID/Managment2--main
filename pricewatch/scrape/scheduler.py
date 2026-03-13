"""pricewatch.scrape.scheduler — Due-job detection and run-enqueue loop.

The scheduler does NOT execute any scraping logic.
It only:
1. discovers enabled, due jobs from the DB,
2. enforces no-overlap,
3. creates queued ScrapeRun records,
4. advances each job's next_run_at.

Intended to be called once per scheduler tick from a background thread or
a CLI command.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from pricewatch.db.repositories import (
    list_due_scrape_jobs,
    has_active_run_for_job,
    enqueue_run,
    set_job_next_run_at,
    get_schedule_for_job,
)
from pricewatch.scrape.schedule import advance_next_run

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SchedulerTick:
    """Result of a single scheduler tick."""

    def __init__(self) -> None:
        self.enqueued: list[int] = []   # run_ids created
        self.skipped_overlap: list[int] = []  # job_ids skipped due to overlap
        self.skipped_no_schedule: list[int] = []  # job_ids with no enabled schedule
        self.errors: list[dict[str, Any]] = []


def run_tick(session: Any, *, now: datetime | None = None, limit: int = 50) -> SchedulerTick:
    """Perform a single scheduler tick.

    Args:
        session:  SQLAlchemy Session (caller must commit on success).
        now:      Reference datetime (UTC).  Defaults to current UTC time.
        limit:    Maximum number of due jobs to process per tick.

    Returns:
        SchedulerTick with summary of actions taken.
    """
    if now is None:
        now = _utcnow()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    tick = SchedulerTick()
    due_jobs = list_due_scrape_jobs(session, now, limit=limit)

    for job in due_jobs:
        try:
            # --- Overlap guard ---
            if not job.allow_overlap and has_active_run_for_job(session, job.id):
                logger.info(
                    "scheduler: skipping job %s (overlap guard, active run exists)", job.id
                )
                tick.skipped_overlap.append(job.id)
                _advance_job_next_run(session, job, now)
                continue

            # --- Retrieve schedule for timing computation ---
            schedule = get_schedule_for_job(session, job.id)
            if schedule is None:
                logger.warning(
                    "scheduler: job %s has no enabled schedule — skipping", job.id
                )
                tick.skipped_no_schedule.append(job.id)
                continue

            # --- Enqueue run ---
            run = enqueue_run(
                session,
                job_id=job.id,
                store_id=None,
                run_type=job.runner_type,
                trigger_type="scheduled",
                metadata_json={"source_key": job.source_key},
            )
            tick.enqueued.append(run.id)
            logger.info("scheduler: enqueued run %s for job %s", run.id, job.id)

            # --- Advance next_run_at ---
            next_run_at = advance_next_run(
                schedule.schedule_type,  # type: ignore[arg-type]
                current_next_run_at=job.next_run_at or now,
                now=now,
                cron_expr=schedule.cron_expr,
                interval_sec=schedule.interval_sec,
                tz_name=schedule.timezone or "UTC",
                jitter_sec=schedule.jitter_sec or 0,
                misfire_policy=schedule.misfire_policy or "skip",
            )
            set_job_next_run_at(session, job.id, next_run_at, last_run_at=now)

        except Exception as exc:
            logger.exception("scheduler: error processing job %s: %s", job.id, exc)
            tick.errors.append({"job_id": job.id, "error": str(exc)})

    return tick


def _advance_job_next_run(session: Any, job: Any, now: datetime) -> None:
    """Advance next_run_at for a job that was skipped (overlap)."""
    schedule = get_schedule_for_job(session, job.id)
    if schedule is None:
        return
    try:
        next_run_at = advance_next_run(
            schedule.schedule_type,  # type: ignore[arg-type]
            current_next_run_at=job.next_run_at or now,
            now=now,
            cron_expr=schedule.cron_expr,
            interval_sec=schedule.interval_sec,
            tz_name=schedule.timezone or "UTC",
            jitter_sec=0,
            misfire_policy="skip",
        )
        set_job_next_run_at(session, job.id, next_run_at)
    except Exception as exc:
        logger.warning("scheduler: could not advance next_run_at for job %s: %s", job.id, exc)

