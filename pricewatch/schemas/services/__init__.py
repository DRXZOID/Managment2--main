"""Optional command DTOs for complex service entrypoints.

Architecture contract
---------------------
- Add DTOs here ONLY when a service entrypoint still accepts loosely structured
  dicts and a typed command object materially improves clarity.
- Keep repositories independent — never import these DTOs from repository code.
- Business logic stays in services.
"""

