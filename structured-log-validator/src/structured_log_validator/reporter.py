from rich.table import Table
from rich.console import Console

class Reporter:
    def __init__(self):
        self.errors = []
        self.console = Console()
    def add(self, path, errs):
        self.errors.extend([{'file': path, **e} for e in errs])
    @property
    def has_errors(self):
        return bool(self.errors)
    def print(self):
        if not self.errors:
            self.console.print('[green]All logs valid.[/green]')
            return
        table = Table(title='Validation Errors')
        table.add_column('File')
        table.add_column('Line')
        table.add_column('Path')
        table.add_column('Message')
        for e in self.errors:
            table.add_row(e['file'], str(e['line']), str(e['path']), e['message'])
        self.console.print(table)