# `flake8-idom-hooks`

A Flake8 plugin that enforces the ["rules of hooks"](https://reactjs.org/docs/hooks-rules.html) for [IDOM](https://github.com/idom-team/idom).

The implementation is based on React's own ESLint [plugin for hooks](https://github.com/facebook/react/tree/master/packages/eslint-plugin-react-hooks).

# Install

```bash
pip install flake8-idom-hooks
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

`ROH2**` errors can be enabled with the `--exhaustive-hook-deps` flag or setting
`exhaustive_hook_deps = True` in your  `flake8` config.

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
