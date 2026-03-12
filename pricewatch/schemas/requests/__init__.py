"""HTTP request body DTOs for PriceWatch API routes.

Architecture contract
---------------------
- All classes here extend PricewatchBaseModel (strict, extra=forbid).
- Fields validate *shape and primitive type* only — no business logic.
- Business rules (e.g. "reference store must not equal target store") live in services.
- These DTOs are never imported from repositories.
"""

