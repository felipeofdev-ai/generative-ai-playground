"""Dependency helpers (RBAC/auth placeholders)."""

from collections.abc import Callable


def require_role(_roles: list[str] | tuple[str, ...]) -> Callable:
    async def _checker() -> bool:
        return True

    return _checker
