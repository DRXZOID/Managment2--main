from __future__ import annotations

from typing import Mapping

from sqlalchemy.orm import Session

from pricewatch.db.models import ScrapeRun, utcnow


DEFAULT_STATUS_RUNNING = "running"
DEFAULT_STATUS_FINISHED = "finished"
DEFAULT_STATUS_FAILED = "failed"


def start_run(
    session: Session,
    *,
    store_id: int | None,
    run_type: str | None = None,
    metadata_json: Mapping | None = None,
) -> ScrapeRun:
    run = ScrapeRun(
        store_id=store_id,
        run_type=run_type,
        status=DEFAULT_STATUS_RUNNING,
        started_at=utcnow(),
        metadata_json=dict(metadata_json) if metadata_json else None,
    )
    session.add(run)
    session.flush()
    return run


def finish_run(session: Session, run_id: int) -> ScrapeRun:
    run = session.get(ScrapeRun, run_id)
    if not run:
        raise ValueError(f"ScrapeRun {run_id} not found")
    run.status = DEFAULT_STATUS_FINISHED
    run.finished_at = utcnow()
    session.flush()
    return run


def fail_run(session: Session, run_id: int, error_message: str) -> ScrapeRun:
    run = session.get(ScrapeRun, run_id)
    if not run:
        raise ValueError(f"ScrapeRun {run_id} not found")
    run.status = DEFAULT_STATUS_FAILED
    run.error_message = error_message
    run.finished_at = utcnow()
    session.flush()
    return run


def increment_counters(
    session: Session,
    run_id: int,
    *,
    categories_processed: int = 0,
    products_processed: int = 0,
    products_created: int = 0,
    products_updated: int = 0,
    price_changes_detected: int = 0,
) -> ScrapeRun:
    run = session.get(ScrapeRun, run_id)
    if not run:
        raise ValueError(f"ScrapeRun {run_id} not found")
    run.categories_processed += categories_processed
    run.products_processed += products_processed
    run.products_created += products_created
    run.products_updated += products_updated
    run.price_changes_detected += price_changes_detected
    session.flush()
    return run

