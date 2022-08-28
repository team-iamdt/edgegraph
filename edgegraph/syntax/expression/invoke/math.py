from edgegraph.syntax.expression.invoke.base import Argument, InvokeExpression


def fn_mean(value: Argument):
    return InvokeExpression(
        module_name="math",
        function_name="mean",
        arguments=(value,),
    )


def stddev(value: Argument):
    return InvokeExpression(
        module_name="math",
        function_name="stddev",
        arguments=(value,),
    )


def fn_stddev_pop(value: Argument):
    return InvokeExpression(
        module_name="math",
        function_name="stddev_pop",
        arguments=(value,),
    )


def fn_var(value: Argument):
    return InvokeExpression(
        module_name="math",
        function_name="var",
        arguments=(value,),
    )


def fn_var_pop(value: Argument):
    return InvokeExpression(
        module_name="math",
        function_name="var_pop",
        arguments=(value,),
    )
