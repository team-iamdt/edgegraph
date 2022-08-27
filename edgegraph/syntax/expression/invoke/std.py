from edgegraph.syntax.expression.invoke.base import Argument, InvokeExpression


def fn_expr_len(value: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="len",
        arguments=(value,),
    )


def fn_contains(haystack: Argument, needle: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="contains",
        arguments=(
            haystack,
            needle,
        ),
    )


def fn_find(haystack: Argument, needle: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="find",
        arguments=(
            haystack,
            needle,
        ),
    )


def fn_assert_distinct(expression: Argument, message: str):
    return InvokeExpression(
        module_name="std",
        function_name="assert_distinct",
        arguments=(
            expression,
            ("str", message),
        ),
    )


def fn_assert_single(expression: Argument, message: str):
    return InvokeExpression(
        module_name="std",
        function_name="assert_single",
        arguments=(
            expression,
            ("str", message),
        ),
    )


def fn_assert_exists(expression: Argument, message: str):
    return InvokeExpression(
        module_name="std",
        function_name="assert_exists",
        arguments=(
            expression,
            ("str", message),
        ),
    )


def fn_count(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="count",
        arguments=(expression,),
    )


def fn_sum(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="sum",
        arguments=(expression,),
    )


def fn_all(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="all",
        arguments=(expression,),
    )


def fn_any(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="any",
        arguments=(expression,),
    )


def fn_enumerate(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="enumerate",
        arguments=(expression,),
    )


def fn_min(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="min",
        arguments=(expression,),
    )


def fn_max(expression: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="max",
        arguments=(expression,),
    )
