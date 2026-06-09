# Architecture

TaintAnalyzer performs a single AST pass tracking assignment of tainted identifiers and their propagation into known sinks. Future versions will add interprocedural analysis via astroid.