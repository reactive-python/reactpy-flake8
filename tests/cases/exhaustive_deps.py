# error: REACTPY101 hook 'use_effect' used outside component or hook definition
use_effect(lambda: x)  # no need to check deps outside component/hook


@component
def check_effects():
    x = 1
    y = 2

    # check that use_state is not treated as having dependencies.
    use_state(lambda: x)

    use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
            + y
        ),
        [y],
    )

    use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        )
    )

    use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x.y
        ),
        [
            # error: REACTPY200 dependency arg of 'use_effect' is not destructured - dependencies should be refered to directly, not via an attribute or key of an object
            x.y
        ],
    )

    module.use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        [],
    )

    module.submodule.use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        [],
    )

    use_effect(
        lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        args=[],
    )

    use_effect(
        function=lambda: (
            # error: REACTPY202 dependency 'x' of function 'lambda' is not specified in declaration of 'use_effect'
            x
        ),
        args=[],
    )

    @use_effect(args=[x])
    def my_effect():
        x

    @use_effect(args=[])
    def my_effect():
        # error: REACTPY202 dependency 'x' of function 'my_effect' is not specified in declaration of 'use_effect'
        x

    @use_effect(args=[])
    @some_other_deco_that_adds_args_to_func_somehow
    def my_effect(*args, **kwargs):
        args
        kwargs

    @module.use_effect(args=[])
    def my_effect():
        # error: REACTPY202 dependency 'x' of function 'my_effect' is not specified in declaration of 'use_effect'
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
        # error: REACTPY201 dependency args of 'use_effect' should be a literal list, tuple, or None - not expression type 'Name'
        not_a_list_or_tuple,
    )

    use_effect(
        lambda: None,
        args=None,  # Ok, to explicitely set None
    )
