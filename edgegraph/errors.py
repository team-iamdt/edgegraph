from dataclasses import dataclass
import typing as t


@dataclass(frozen=True)
class ValidatedErrorValue:
    error_message: str
    module: t.Optional[str] = None
    type: t.Optional[str] = None
    property: t.Optional[str] = None


class ValidationError(Exception):
    errors: t.List[ValidatedErrorValue]
    message: t.Optional[str]

    def __init__(
        self, errors: t.List[ValidatedErrorValue], message: t.Optional[str] = None
    ):
        self.errors = errors
        self.message = message

    def __str__(self):
        return f"{len(self.errors)} Errors in validation. Message: {self.message}"


class ConditionValidationError(Exception):
    condition: str
    message: t.Optional[str]

    def __init__(self, condition: str, message: t.Optional[str] = None):
        self.condition = condition
        self.message = message

    def __str__(self):
        return f"{self.condition} already exists. Message: {self.message}"


class QueryContextMissmatchingError(Exception):
    builder: t.Type
    expression: t.Type
    message: str

    def __init__(self, builder: t.Type, expression: t.Type):
        self.builder = builder
        self.expression = expression
        self.message = (
            f"Type Missmatched: EdgeQL Builder {builder} / Expression {expression}"
        )

    def __str__(self):
        return self.message
