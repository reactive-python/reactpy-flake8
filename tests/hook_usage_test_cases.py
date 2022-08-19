import idom
from idom import component


@component
def HookInIf():
    if True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state


@component
def HookInElif():
    if False:
        pass
    elif True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state


@component
def HookInElse():
    if False:
        pass
    else:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state


@component
def HookInIfExp():
    (
        # error: ROH102 hook 'use_state' used inside inline if expression
        use_state
        if True
        else None
    )


@component
def HookInElseOfIfExp():
    (
        None
        if True
        else
        # error: ROH102 hook 'use_state' used inside inline if expression
        use_state
    )


@component
def HookInTry():
    try:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state
    except:
        pass


@component
def HookInExcept():
    try:
        raise ValueError()
    except:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state


@component
def HookInFinally():
    try:
        pass
    finally:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state


@component
def HookInForLoop():
    for i in range(3):
        # error: ROH102 hook 'use_state' used inside for loop
        use_state


@component
def HookInWhileLoop():
    while True:
        # error: ROH102 hook 'use_state' used inside while loop
        use_state


def outer_function():
    # error: ROH100 hook 'use_state' defined as closure in function 'outer_function'
    def use_state():
        ...


def generic_function():

    # error: ROH101 hook 'use_state' used outside component or hook definition
    use_state


@component
def use_state():
    use_other


@component
def Component():
    use_state


@idom.component
def IdomLongImportComponent():
    use_state


@component
def use_custom_hook():
    use_state


# ok since 'use_state' is not the last attribute
module.use_state.other

# error: ROH101 hook 'use_effect' used outside component or hook definition
module.use_effect()


def not_hook_or_component():
    # error: ROH101 hook 'use_state' used outside component or hook definition
    use_state


@component
def CheckEffects():
    x = 1
    y = 2

    use_effect(
        lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
            + y
        ),
        [y],
    )

    use_effect(
        lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        )
    )

    use_effect(
        lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x.y
        ),
        [
            # error: ROH201 dependency arg of 'use_effect' is not destructured - dependencies should be refered to directly, not via an attribute or key of an object
            x.y
        ],
    )

    module.use_effect(
        lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        [],
    )

    use_effect(
        lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        args=[],
    )

    use_effect(
        function=lambda: (
            # error: ROH203 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        args=[],
    )

    @use_effect(args=[x])
    def my_effect():
        x

    @use_effect(args=[])
    def my_effect():
        # error: ROH203 dependency 'x' of function 'my_effect' is not specified in declaration of 'use_effect'
        x

    @use_effect(args=[])
    @some_other_deco_that_adds_args_to_func_somehow
    def my_effect(*args, **kwargs):
        args
        kwargs

    @module.use_effect(args=[])
    def my_effect():
        # error: ROH203 dependency 'x' of function 'my_effect' is not specified in declaration of 'use_effect'
        x

    @not_a_decorator_we_care_about
    def some_func():
        ...

    @not_a_decorator_we_care_about()
    def some_func():
        ...

    @use_effect
    def impropper_usage_of_effect_as_decorator():
        # ignored because bad useage
        x

    use_effect(
        lambda: None,
        # error: ROH202 dependency args of 'use_effect' should be a literal list or tuple - not expression type 'Name'
        not_a_list_or_tuple,
    )


@component
def make_component():
    # nested component definitions are ok.
    @component
    def NestedComponent():
        use_state


some_global_variable


@component
def Component():
    # referencing a global variable is OK
    use_effect(lambda: some_global_variable, [])


if True:

    @component
    def Component():
        # this is ok since the conditional is outside the component
        use_state

    @component
    def use_other():
        use_state
