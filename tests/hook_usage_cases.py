def HookInIf():
    if True:
        # error: Hook 'use_state' used inside if statement.
        use_state


def HookInElif():
    if False:
        pass
    elif True:
        # error: Hook 'use_state' used inside if statement.
        use_state


def HookInElse():
    if False:
        pass
    else:
        # error: Hook 'use_state' used inside if statement.
        use_state


def HookInIfExp():
    (
        # error: Hook 'use_state' used inside inline if expression.
        use_state
        if True
        else None
    )


def HookInElseOfIfExp():
    (
        None
        if True
        else
        # error: Hook 'use_state' used inside inline if expression.
        use_state
    )


def HookInTry():
    try:
        # error: Hook 'use_state' used inside try statement.
        use_state
    except:
        pass


def HookInExcept():
    try:
        raise ValueError()
    except:
        # error: Hook 'use_state' used inside try statement.
        use_state


def HookInFinally():
    try:
        pass
    finally:
        # error: Hook 'use_state' used inside try statement.
        use_state


def HookInForLoop():
    for i in range(3):
        # error: Hook 'use_state' used inside for loop.
        use_state


def HookInWhileLoop():
    while True:
        # error: Hook 'use_state' used inside while loop.
        use_state


def outer_function():
    # error: Hook 'use_state' defined inside another function.
    def use_state():
        ...


def generic_function():
    # error: Hook 'use_state' used outside element or hook definition.
    use_state


def use_state():
    use_other


def Element():
    use_state


# ok since 'use_state' is not the last attribute
module.use_state.other

# error: Hook 'use_state' used outside element or hook definition.
module.use_state
