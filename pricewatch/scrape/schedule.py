"""pricewatch.scrape.schedule — Schedule timing / next-run computation.

All interaction with the ``croniter`` library is encapsulated here.
The rest of the codebase MUST NOT import croniter directly.

Supports two schedule types:
  - "interval"  — fixed number of seconds between runs
  - "cron"      — cron expression (evaluated via croniter)

Misfire policy (MVP):
  If a job is overdue, scheduler enqueues at most one run per tick and
  advances next_run_at once (no backlog explosion).
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Literal

# croniter is a hard runtime dep — installed via requirements.txt / pip
try:
    from croniter import croniter  # type: ignore[import]
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "croniter is required for cron schedule support. "
        "Install it with: pip install croniter"
    ) from exc

ScheduleType = Literal["interval", "cron"]


def compute_next_run(
    schedule_type: ScheduleType,
    *,
    from_dt: datetime,
    cron_expr: str | None = None,
    interval_sec: int | None = None,
    tz_name: str = "UTC",
    jitter_sec: int = 0,
) -> datetime:
    """Return the next scheduled datetime after *from_dt*.

    Args:
        schedule_type: "interval" or "cron".
        from_dt:       Reference datetime (timezone-aware; use UTC).
        cron_expr:     Cron expression (required when type == "cron").
        interval_sec:  Interval in seconds (required when type == "interval").
        tz_name:       Timezone name for cron evaluation (default "UTC").
        jitter_sec:    Optional random jitter to add (0 = no jitter).

    Returns:
        timezone-aware datetime of the next scheduled run.
    """
    if from_dt.tzinfo is None:
        from_dt = from_dt.replace(tzinfo=timezone.utc)

    if schedule_type == "interval":
        if interval_sec is None or interval_sec <= 0:
            raise ValueError("interval_sec must be a positive integer for interval schedules")
        base = from_dt + timedelta(seconds=interval_sec)

    elif schedule_type == "cron":
        if not cron_expr:
            raise ValueError("cron_expr is required for cron schedules")
        # croniter works best with a naive datetime as base; convert back after
        naive_from = from_dt.astimezone(timezone.utc).replace(tzinfo=None)
        it = croniter(cron_expr, start_time=naive_from)
        next_naive: datetime = it.get_next(datetime)
        base = next_naive.replace(tzinfo=timezone.utc)

    else:
        raise ValueError(f"Unknown schedule_type: {schedule_type!r}")

    if jitter_sec > 0:
        base = base + timedelta(seconds=random.randint(0, jitter_sec))

    return base


def advance_next_run(
    schedule_type: ScheduleType,
    *,
    current_next_run_at: datetime,
    now: datetime,
    cron_expr: str | None = None,
    interval_sec: int | None = None,
    tz_name: str = "UTC",
    jitter_sec: int = 0,
    misfire_policy: str = "skip",
) -> datetime:
    """Compute the new next_run_at after a run has fired.

    Misfire policy "skip" (MVP):
      Advance by exactly one step from *current_next_run_at*.
      If the result is still in the past, keep advancing until it is
      in the future (prevents backlog explosion; at most one extra pass).
    """
    next_dt = compute_next_run(
        schedule_type,
        from_dt=current_next_run_at,
        cron_expr=cron_expr,
        interval_sec=interval_sec,
        tz_name=tz_name,
        jitter_sec=jitter_sec,
    )
    # If the computed next is still in the past (overdue), advance once more
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    if next_dt <= now:
        next_dt = compute_next_run(
            schedule_type,
            from_dt=now,
            cron_expr=cron_expr,
            interval_sec=interval_sec,
            tz_name=tz_name,
            jitter_sec=0,  # no jitter on catch-up
        )
    return next_dt

