# grpc-reflection-cli

## Why this exists
Most gRPC services expose reflection in production, yet engineers still rely on brittle proto files or manual grpcurl invocations. This tool discovers every service, method, and message shape at runtime, then produces immediately usable artifacts and a safe REPL for exploration.

## Features
- Automatic service discovery via gRPC reflection
- Export OpenAPI 3.1 + Markdown docs for any reflected API
- Generate ready-to-use Python or TypeScript clients from live schemas
- Interactive REPL with request validation, streaming support, and timing
- Rich table/JSON output, progress bars, and structured logging
- Zero protobuf compilation step required

## Installation
```bash
pip install grpc-reflection-cli
```

## Usage
```bash
grpc-reflection-cli inspect localhost:50051 --format openapi > api.json
grpc-reflection-cli call localhost:50051 helloworld.Greeter/SayHello --data '{"name":"Ada"}'
```

## Architecture
Thin wrapper around grpcio-reflection with rich metadata extraction, jsonschema translation, and pluggable output renderers. All network calls are instrumented with deadlines and retry policies.

## Benchmarks
Typical 200-method service: full inspection + OpenAPI export completes in <800 ms on a laptop.

## Alternatives considered
grpcurl (no docs/clients), protoc (requires source), buf (build-time only).