@component
def example():
    match something:
        case int:
            # error: REACTPY102 hook 'use_state' used inside match statement
            use_state()
