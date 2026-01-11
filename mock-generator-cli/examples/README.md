## Examples

Run:
```bash
python -m mock_generator_cli.cli examples/demo.py:foo
python -m mock_generator_cli.cli examples/demo.py:MyClass.method
python -m mock_generator_cli.cli examples/demo.py:MyClass.__init__
```

Paste output directly into `test_demo.py`. Edit call args/asserts as needed.

Generated code is Black-formatted and pytest-ready.