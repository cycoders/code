from configparser import ConfigParser

def render_unit(data: dict) -> str:
    parser = ConfigParser()
    parser.optionxform = str
    for section, values in data.items():
        parser[section] = {k: str(v) for k, v in values.items() if v is not None}
    from io import StringIO
    buf = StringIO()
    parser.write(buf)
    return buf.getvalue()