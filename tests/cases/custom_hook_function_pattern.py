@component
def check():
    if True:
        # this get's ignored because of custom pattern
        use_ignore_this()
        # error: REACTPY102 hook 'use_state' used inside if statement
        use_state()
