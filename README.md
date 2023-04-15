# `reactpy-flake8`

A Flake8 plugin that enforces the ["rules of hooks"](https://reactjs.org/docs/hooks-rules.html) for [ReactPy](https://github.com/reactive-python/reactpy).

The implementation is based on React's own ESLint [plugin for hooks](https://github.com/facebook/react/tree/master/packages/eslint-plugin-react-hooks).

# Install

```bash
pip install reactpy-flake8
```

# Developer Installation

```bash
pip install -r requirements.txt
pip install -e .
```

Run the tests

```bash
tox
```

# Errors

<table>
    <tr>
        <th>Code</th>
        <th>Message</th>
    </tr>
    <tr>
        <td>ROH100</td>
        <td>Hook is defined as a closure</td>
    </tr>
    <tr>
        <td>ROH101</td>
        <td>Hook was used outside component or hook definition</td>
    </tr>
    <tr>
        <td>ROH102</td>
        <td>Hook was used inside a conditional or loop statement</td>
    </tr>
    <tr>
        <td>ROH103</td>
        <td>Hook was used after an early return</td>
    </tr>
    <tr>
        <td>ROH200</td>
        <td>
            A hook's dependency is not destructured - dependencies should be refered to
            directly, not via an attribute or key of an object
        </td>
    </tr>
    <tr>
        <td>ROH201</td>
        <td>Hook dependency args should be a literal list, tuple or None</td>
    </tr>
    <tr>
        <td>ROH202</td>
        <td>
            Hook dependency is not specified
        </td>
    </tr>
</table>

# Options

All options my be used as CLI flags where `_` characters are replaced with `-`. For
example, `exhaustive_hook_deps` would become `--exhaustive-hook-deps`.

<table>
    <tr>
        <th>Option</th>
        <th>Type</th>
        <th>Default</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>exhaustive_hook_deps</code></td>
        <td>Boolean</td>
        <td><code>False</code></td>
        <td>Enable <code>ROH2**</code> errors (recommended)</td>
    </tr>
    <tr>
        <td><code>component_decorator_pattern</code></td>
        <td>Regex</td>
        <td><code>^(component|[\w\.]+\.component)$</code></td>
        <td>
            The pattern which should match the component decorators. Useful if
            you import the <code>@component</code> decorator under an alias.
        </td>
    </tr>
    <tr>
        <td><code>hook_function_pattern</code></td>
        <td>Regex</td>
        <td><code>^_*use_\w+$</code></td>
        <td>
            The pattern which should match the name of hook functions. Best used if you
            have existing functions with <code>use_*</code> names that are not hooks.
        </td>
    </tr>
</table>
