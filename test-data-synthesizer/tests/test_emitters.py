from test_data_synthesizer.emitters import ParquetEmitter

def test_parquet_roundtrip(tmp_path):
    e = ParquetEmitter()
    e.write([{'id':1}], tmp_path/'t.parquet')