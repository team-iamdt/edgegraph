from edgegraph.syntax.expression.invoke.base import Argument, InvokeExpression


def expr_len(value: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="len",
        arguments=(value,),
    )


def contains(haystack: Argument, needle: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="contains",
        arguments=(
            haystack,
            needle,
        ),
    )


def find(haystack: Argument, needle: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="find",
        arguments=(
            haystack,
            needle,
        ),
    )
