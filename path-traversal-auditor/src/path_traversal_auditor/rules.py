TAINT_SOURCES = {"request.args", "request.form", "input", "sys.argv"}
TAINT_SINKS = {"open", "os.path.join", "Path", "send_file"}
SANITIZERS = {"os.path.abspath", "secure_filename"}