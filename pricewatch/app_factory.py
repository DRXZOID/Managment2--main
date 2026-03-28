"""pricewatch.app_factory — Side-effect-free application factory.

This module defines the Flask application factory without creating a
global app instance as a module-level side effect.

Design rules
------------
- This module MUST NOT contain ``app = create_app()`` or any equivalent
  top-level call that creates an app or starts background threads.
- Dedicated runtime entrypoints (scheduler, worker) MUST import
  ``create_app`` from here, NOT from ``app.py``.
- The web entry-point (``app.py``) imports this factory, calls it, and
  then wires the embedded scheduler autostart separately.

Compatibility
-------------
- Gunicorn target: ``app.py`` (unchanged).
- Dev server: ``python app.py`` (unchanged).
- Scheduler: ``python -m pricewatch.scrape.run_scheduler``.
- Worker:    ``python -m pricewatch.scrape.run_worker``.
"""
from __future__ import annotations

import logging
import os

from flask import Flask
from flask_cors import CORS

from pricewatch.core.registry import get_registry
from pricewatch.db import Base, init_engine, init_db, get_session_factory, get_scoped_session
from pricewatch.services.store_service import StoreService
from pricewatch.web import register_blueprints
from pricewatch.web.assets import register_asset_helpers

logger = logging.getLogger(__name__)

# Resolve the project root once at import time.
# pricewatch/app_factory.py  →  pricewatch/  →  project root
_PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Frontend / Vite asset integration defaults
#
# These keys configure the Flask ↔ Vite asset helper (pricewatch.web.assets).
# All keys are optional — the app boots normally even when no frontend build
# exists yet.  Override any key via config_override or environment-driven
# config.
#
#   VITE_USE_DEV_SERVER   — True  → emit tags pointing at the Vite dev server
#                           False → emit hashed production tags from manifest
#   VITE_DEV_SERVER_URL   — Base URL of the local Vite dev server
#   VITE_MANIFEST_PATH    — Absolute path to the Vite manifest.json produced
#                           by  npm run build  inside frontend/.
#                           Vite 5 writes it at  <outDir>/.vite/manifest.json;
#                           once vite.config.ts outDir is set to
#                           '../static/dist' this resolves to the path below.
#   FRONTEND_DIST_URL_PREFIX — URL prefix prepended to hashed asset filenames
#                              when building <script>/<link> tags.
# ---------------------------------------------------------------------------
_VITE_MANIFEST_DEFAULT = os.path.join(
    _PROJECT_ROOT, "static", "dist", ".vite", "manifest.json"
)


def create_app(config_override=None) -> Flask:
    """Application factory — pure construction, no background threads.

    Parameters
    ----------
    config_override:
        Optional dict of Flask/app config values applied *before* DB
        initialisation.  Pass ``{"DATABASE_URL": "sqlite:///:memory:",
        "TESTING": True}`` to point the app at a test database.

    Returns
    -------
    Flask
        A fully configured Flask application instance with its own DB
        wiring.  No scheduler or worker threads are started here.

    Note
    ----
    Embedded scheduler autostart is NOT called from this factory.
    It is the responsibility of the **web entry-point** (``app.py``) to
    call ``start_scheduler_if_enabled(app)`` after construction.
    Dedicated runtime processes bypass that call entirely.
    """
    flask_app = Flask(
        "app",
        root_path=_PROJECT_ROOT,
        template_folder=os.path.join(_PROJECT_ROOT, "templates"),
        static_folder=os.path.join(_PROJECT_ROOT, "static"),
    )
    CORS(flask_app)
    flask_app.config.setdefault("ENABLE_ADMIN_SYNC", True)
    flask_app.json.ensure_ascii = False

    # --- Frontend / Vite asset integration defaults ---
    flask_app.config.setdefault("VITE_USE_DEV_SERVER", False)
    flask_app.config.setdefault("VITE_DEV_SERVER_URL", "http://localhost:5173")
    flask_app.config.setdefault("VITE_MANIFEST_PATH", _VITE_MANIFEST_DEFAULT)
    flask_app.config.setdefault("FRONTEND_DIST_URL_PREFIX", "/static/dist")

    if config_override:
        flask_app.config.update(config_override)

    # --- DB wiring (per-app instance, not global) ---
    _engine = init_engine(flask_app.config)
    _factory = get_session_factory(_engine)
    _scoped = get_scoped_session(_factory)
    init_db(_engine, base=Base, app_config=flask_app.config)

    flask_app.extensions["db_engine"] = _engine
    flask_app.extensions["db_session_factory"] = _factory
    flask_app.extensions["db_scoped_session"] = _scoped

    @flask_app.teardown_appcontext
    def shutdown_session(exception=None):  # noqa: F811
        flask_app.extensions["db_scoped_session"].remove()

    # Bootstrap store registry only in non-test mode
    if not flask_app.config.get("TESTING"):
        _reg = get_registry()
        with flask_app.app_context():
            _sess = _scoped()
            _svc = StoreService(_sess)
            try:
                _svc.sync_with_registry(_reg)
                _sess.commit()
            except Exception as exc:  # pragma: no cover
                _sess.rollback()
                logger.exception("Failed to bootstrap stores: %s", exc)
            finally:
                _scoped.remove()

    # --- App-level after_request hook ---
    @flask_app.after_request
    def set_response_charset(response):
        """Ensure responses include charset=utf-8 in Content-Type."""
        try:
            content_type = response.headers.get("Content-Type", "")
            if "charset" not in content_type.lower():
                mimetype = response.mimetype or ""
                if mimetype in ("application/json", "text/html", "application/javascript"):
                    response.headers["Content-Type"] = f"{mimetype}; charset=utf-8"
        except Exception:
            logger.exception("set_response_charset failed")
        return response

    # --- Blueprint registration ---
    register_blueprints(flask_app)

    # --- Frontend / Vite asset helper registration ---
    # Adds vite_asset_tags() as a Jinja global.  No filesystem I/O here.
    register_asset_helpers(flask_app)

    # NOTE: start_scheduler_if_enabled is intentionally NOT called here.
    # The web entry-point (app.py) calls it separately after create_app().
    # Dedicated runtime processes (run_scheduler, run_worker) enter their
    # own loops directly without going through embedded autostart.

    return flask_app

