from dataclasses import dataclass

__all__ = ["AccountRoutine"]


@dataclass(slots=True)
class AccountRoutine:
    id: str
    name: str
    mark: str
