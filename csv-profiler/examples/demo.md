# Demo Usage

```bash
curl -O https://example.com/large.csv
csv-profiler profile large.csv --max-rows 100000 --output html > report.html
open report.html
```

Explore `tests/data/sample.csv` for tests.