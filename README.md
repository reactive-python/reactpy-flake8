# `flake8-idom`

A Flake8 plugin for [IDOM](https://github.com/idom-team/idom) that enforces:

- the ["rules of hooks"](https://reactjs.org/docs/hooks-rules.html).

The implementation is based on React's own ESLint [plugin for hooks](https://github.com/facebook/react/tree/master/packages/eslint-plugin-react-hooks).

# Install

```bash
pip install flake8-idom
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
