# Examples

Run `class-diagram-cli examples/` to see output.

- `simple.py`: Basic inheritance, methods, attrs, static/classmethod.

Expected `ex.mmd`:

```mermaid
classDiagram
    direction TB
    class `Animal` {
        +age : int
        +__init__(age)
        +speak()
    }
    class `Mammal` {
        +fur_color
        +from_birth()
    }
    class `Dog` {
        +bark()
        #is_friendly()
    }
    `Mammal` <|-- `Animal`
    `Dog` <|-- `Mammal`
```

Paste into mermaid.live for interactive view!