@component
def example():
    match something:
        case int:
            # error: ROH102 hook 'use_state' used inside match statement
            use_state()
