import black
from mock_generator_cli.writer import generate_test_code


class TestGenerateTestCode:
    def test_function_no_calls(self):
        code = generate_test_code('mymod', 'foo', set(), False)
        assert 'def test_foo(mocker):' in code
        assert 'pass' in code

    def test_function_with_calls(self):
        calls = {'os.path.join', 'json.loads'}
        code = generate_test_code('mymod', 'foo', calls, False)
        assert "mocker.patch('json.loads'" in code
        assert "mocker.patch('os.path.join'" in code
        assert 'foo()' in code
        assert black.format_str(code, mode=black.FileMode()) == code  # idempotent

    def test_method(self):
        code = generate_test_code('mymod', 'method', {'os.makedir'}, True, 'MyClass')
        assert 'def test_MyClass_method(mocker):' in code
        assert 'instance = MyClass()' in code
        assert 'instance.method()' in code

    def test_init_method(self):
        code = generate_test_code('mymod', '__init__', set(), True, 'MyClass')
        assert 'instance = MyClass()  # Calls __init__' in code