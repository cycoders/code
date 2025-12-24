# Examples

Run:
```bash
coverage-merger merge report1.xml report2.xml --html-report out.html --output merged.xml
```

Expected:
- `file.py`: 75.0% lines (3/4), 100.0% branches (1/1)
- `out.html`: Viewable table

Use `report1.xml` as `--prev` for deltas.
