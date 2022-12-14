import typing as t
from enum import Enum


class QueryResult(t.NamedTuple):
    query: str
    kwargs: t.Dict[str, t.Any]


class PrimitiveTypes(Enum):
    STR = "str"
    STRING = "str"
    BOOL = "bool"
    BOOLEAN = "bool"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    BIGINT = "bigint"
    DECIMAL = "decimal"
    JSON = "json"
    UUID = "uuid"
    BYTES = "bytes"
    DATETIME = "datetime"
    DURATION = "duration"
    LOCAL_DATETIME = "cal::local_datetime"
    LOCAL_DATE = "cal::local_date"
    LOCAL_TIME = "cal::local_time"
    RELATIVE_DURATION = "cal::relative_duration"
    SEQUENCE = "sequence"
