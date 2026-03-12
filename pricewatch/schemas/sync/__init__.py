"""Sync/import ingestion DTOs for PriceWatch.

Architecture contract
---------------------
- All classes here extend LooseBaseModel (permissive, extra=ignore).
- Normalization rules: field aliases, empty→None, URL trimming, safe numeric coercion.
- Business decisions (what to do with normalized data) live in services.
- These DTOs are never imported from repositories.
"""

