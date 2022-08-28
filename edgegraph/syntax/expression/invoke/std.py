import typing as t

from edgegraph.syntax.expression.invoke.base import Argument, InvokeExpression


def fn_len(value: Argument):
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


def fn_str_lower(string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_lower",
        arguments=(string,),
    )


def fn_str_upper(string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_upper",
        arguments=(string,),
    )


def fn_str_title(string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_title",
        arguments=(string,),
    )


def fn_str_pad_start(string: Argument, n: Argument, fill: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_pad_start",
        arguments=(
            string,
            n,
            fill,
        ),
    )


def fn_str_pad_end(string: Argument, n: Argument, fill: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_pad_end",
        arguments=(
            string,
            n,
            fill,
        ),
    )


def fn_str_trim_start(string: Argument, trim: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_trim_start",
        arguments=(
            string,
            trim,
        ),
    )


def fn_str_trim_end(string: Argument, trim: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_trim_end",
        arguments=(
            string,
            trim,
        ),
    )


def fn_str_trim(string: Argument, trim: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_trim",
        arguments=(
            string,
            trim,
        ),
    )


def fn_str_repeat(string: Argument, n: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_repeat",
        arguments=(
            string,
            n,
        ),
    )


def fn_str_replace(string: Argument, old: Argument, new: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_replace",
        arguments=(
            string,
            old,
            new,
        ),
    )


def fn_str_reverse(string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_reverse",
        arguments=(string,),
    )


def fn_str_split(string: Argument, delimiter: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="str_split",
        arguments=(
            string,
            delimiter,
        ),
    )


def fn_re_match(pattern: Argument, string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="re_match",
        arguments=(
            pattern,
            string,
        ),
    )


def fn_re_match_all(pattern: Argument, string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="re_match_all",
        arguments=(pattern, string),
    )


# TODO(Hazealign): Need to be implement named argument
def fn_re_replace(pattern: Argument, sub: Argument, string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="re_match",
        arguments=(
            pattern,
            sub,
            string,
        ),
    )


def fn_re_test(pattern: Argument, string: Argument):
    return InvokeExpression(
        module_name="std",
        function_name="re_test",
        arguments=(pattern, string),
    )


def fn_to_str(val: Argument, fmt: t.Optional[Argument] = None):
    return InvokeExpression(
        module_name="std",
        function_name="to_str",
        arguments=(
            val,
            fmt,
        )
        if fmt is not None
        else (val,),
    )
