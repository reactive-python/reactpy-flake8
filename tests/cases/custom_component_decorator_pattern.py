@component
def check_normal_pattern():
    if True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state()


@custom_component
def check_custom_pattern():
    if True:
        # error: ROH102 hook 'use_state' used inside if statement
        use_state()
