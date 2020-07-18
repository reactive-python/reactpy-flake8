import idom


@idom.element
async def HookIsInConditional():
    if True:
        state, set_state = idom.hooks.use_state(None)
    return idom.html.div(state)
