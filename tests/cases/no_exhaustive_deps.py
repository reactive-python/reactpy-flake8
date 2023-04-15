# confirm that we're still checking for other errors
def generic_function():
    # error: REACTPY101 hook 'use_state' used outside component or hook definition
    use_state()


@component
def check_dependency_checks_are_ignored():
    x = 1
    y = 2

    use_effect(
        lambda: x + y,
        [y],
    )

    use_effect(lambda: x)

    use_effect(
        lambda: x.y,
        [x.y],
    )

    module.use_effect(
        lambda: x,
        [],
    )

    use_effect(
        lambda: x,
        args=[],
    )

    use_effect(
        function=lambda: x,
        args=[],
    )

    @use_effect(args=[x])
    def my_effect():
        x

    @use_effect(args=[])
    def my_effect():
        x

    @use_effect(args=[])
    @some_other_deco_that_adds_args_to_func_somehow
    def my_effect(*args, **kwargs):
        args
        kwargs

    @module.use_effect(args=[])
    def my_effect():
        x

    @not_a_decorator_we_care_about
    def some_func():
        ...

    @not_a_decorator_we_care_about()
    def some_func():
        ...

    use_effect(
        lambda: None,
        not_a_list_or_tuple,
    )
