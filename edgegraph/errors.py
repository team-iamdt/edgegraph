import typing as t
from dataclasses import dataclass


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
        return f"Condition Error in {self.condition} Context. Message: {self.message}"


class QueryContextMissmatchError(Exception):
    builder: t.Union[t.Type, str]
    expression: t.Optional[t.Union[t.Type, str]]
    message: str

    def __init__(
        self,
        builder: t.Union[t.Type, str],
        expression: t.Optional[t.Union[t.Type, str]] = None,
    ):
        self.builder = builder
        self.expression = expression
        self.message = (
            f"Type Missmatched: EdgeQL Builder {builder} / Expression {expression}"
        )

    def __str__(self):
        return self.message


class ExpressionError(Exception):
    context: str
    message: str

    def __init__(self, context: str, message: str):
        self.context = context
        self.message = message

    def __str__(self):
        return f"Expression Error in {self.context} context: {self.message}"


class FieldNotFoundError(Exception):
    field: str

    def __init__(self, field: str):
        self.field = field

    def __str__(self):
        return f"Failed to found field: {self.field}"


class CandidateTypeError(TypeError):
    pass
