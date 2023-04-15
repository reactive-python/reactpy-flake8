import reactpy
from reactpy import component


@component
def HookInIfNoCall():
    if True:
        # Ok, hook was not called
        use_state
        # Also ok, hook itself was not called
        func(use_state)


@component
def HookInIf():
    if True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state()


@component
def HookInIfInExpression():
    if True:
        (
            None
            or
            # error: ROH102 hook 'use_state' used inside if statement
            use_state
        )()


@component
def HookInElif():
    if False:
        pass
    elif True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state()


@component
def HookInElse():
    if False:
        pass
    else:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state()


@component
def HookInIfExp():
    (
        # error: ROH102 hook 'use_state' used inside inline if expression
        use_state()
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
        use_state()
    )


@component
def HookInTry():
    try:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state()
    except:
        pass


@component
def HookInExcept():
    try:
        raise ValueError()
    except:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state()


@component
def HookInFinally():
    try:
        pass
    finally:
        # error: ROH102 hook 'use_state' used inside try statement
        use_state()


@component
def HookInForLoop():
    for i in range(3):
        # error: ROH102 hook 'use_state' used inside for loop
        use_state()


@component
def HookInWhileLoop():
    while True:
        # error: ROH102 hook 'use_state' used inside while loop
        use_state()


def outer_function():
    # error: ROH100 hook 'use_state' defined as closure in function 'outer_function'
    def use_state():
        ...


def generic_function():
    # error: ROH101 hook 'use_state' used outside component or hook definition
    use_state()


@component
def use_state():
    use_other()


@component
def Component():
    use_state()


@reactpy.component
def IdomLongImportComponent():
    use_state()


@component
def use_custom_hook():
    use_state()


# ok since 'use_state' is not the last attribute
module.use_state.other

# ok since use state is not called
module.use_effect

# error: ROH101 hook 'use_effect' used outside component or hook definition
module.use_effect()


def not_hook_or_component():
    # error: ROH101 hook 'use_state' used outside component or hook definition
    use_state()


@component
def make_component():
    # nested component definitions are ok.
    @component
    def NestedComponent():
        use_state()


some_global_variable


@component
def Component():
    # referencing a global variable is OK
    use_effect(lambda: some_global_variable, [])


if True:

    @component
    def Component():
        # this is ok since the conditional is outside the component
        use_state()

    @component
    def use_other():
        use_state()


@component
def example():
    if True:
        return None
    # error: ROH103 hook 'use_state' used after an early return on line 190
    use_state()


@component
def example():
    def closure():
        # this return is ok since it's not in the same function
        return None

    # Ok: no early return error
    use_state()


@component
def example():
    @use_effect
    def some_effect():
        # this return is ok since it's not in the same function
        return None

    # Ok: no early return error
    use_state()


@reactpy.component
def regression_check():
    @use_effect
    def effect():
        # this return caused false passitive early return error in use_effect usage
        return cleanup

    @use_effect
    async def effect():
        # this return caused false passitive early return error in use_effect usage
        return cleanup
