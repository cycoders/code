import pyarrow as pa

class ParquetEmitter:
    def write(self, rows, path):
        table = pa.Table.from_pylist(rows)
        pa.parquet.write_table(table, path)