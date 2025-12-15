import ast

from env_schema_gen.visitor import EnvVarVisitor


class TestEnvVarVisitor:
    def test_os_getenv_simple(self):
        source = "os.getenv('TEST_VAR')"
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert 'TEST_VAR' in visitor.vars

    def test_os_getenv_with_default(self):
        source = "os.getenv('TEST', 'default')"
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert visitor.type_hints['TEST'] == 'str'

    def test_os_getenv_int_default(self):
        source = "os.getenv('PORT', 8080)")
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert visitor.type_hints['PORT'] == 'int'

    def test_os_environ_get(self):
        source = "os.environ.get('KEY')"
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert 'KEY' in visitor.vars

    def test_os_environ_subscript(self):
        source = "host = os.environ['DB_HOST']"
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert 'DB_HOST' in visitor.vars

    def test_inside_lambda(self):
        source = "Field(default_factory=lambda: os.getenv('SECRET'))"
        tree = ast.parse(source)
        visitor = EnvVarVisitor('test.py')
        visitor.visit(tree)
        assert 'SECRET' in visitor.vars