# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application

```bash
# Install dependencies (if not already done)
uv sync

# Run the FastAPI server locally
uv run mirror-med-api

# Alternative: run with uvicorn directly
uv run uvicorn mirror_med.app:app --reload
```

### Code Formatting and Linting

```bash
# Format and lint code (uses ruff)
uv run format
```

### Building and Deployment

```bash
# Build Docker image
docker build -t mirror-med .

# Deploy to Fly.io
fly deploy

# Check deployment status
fly status
```

## A2A Web Resources

Use a web fetch and web search tool like exa to index and gather information from these websites.

- https://a2aproject.github.io/A2A/latest/topics/what-is-a2a/
- https://a2aproject.github.io/A2A/latest/topics/key-concepts/
- https://a2aproject.github.io/A2A/latest/topics/a2a-and-mcp/
- https://a2aproject.github.io/A2A/latest/topics/agent-discovery/
- https://a2aproject.github.io/A2A/latest/topics/streaming-and-async/
- https://a2aproject.github.io/A2A/latest/topics/life-of-a-task/
- [SDK Reference](https://a2aproject.github.io/A2A/latest/sdk/python/)

## Architecture Overview

### Core Application Structure

The project is a FastAPI-based web service with Agent-to-Agent (A2A) protocol capabilities:

**Main API Service** (`src/mirror_med/`)

- `app.py`: FastAPI application with health endpoints and CORS configuration
- `settings.py`: Environment-based configuration using Pydantic settings
- `logging.py`: Structured logging setup with request filtering
- Uses `structlog` for JSON-formatted logs with health check filtering

**Deployment Configuration** (`fly.toml`)

- Fly.io deployment with auto-scaling (min 1 instance)
- Health check endpoint at `/health`
- Uses multi-stage Docker build with uv for efficient images

### A2A Integration Architecture

The `a2a-samples/` directory contains extensive Agent-to-Agent protocol examples:

1. **Host-Remote Agent Pattern**

   - Host agents orchestrate requests to remote agents
   - Remote agents expose capabilities via AgentCards
   - Communication happens over A2A protocol using JSON-RPC

2. **Key A2A Components**

   - `AgentCard`: Describes agent capabilities and endpoints
   - `Message`: Standard communication format between agents
   - `Task`: Async task tracking for long-running operations
   - Uses `a2a-sdk` for protocol implementation

3. **Multi-Agent Orchestration**
   - Host agents can dynamically discover and add remote agents
   - Supports complex workflows with multiple agent interactions
   - Event tracking and task management for observability

### Integration Points

1. **AI/ML Services**

   - OpenAI integration for LLM capabilities
   - Weave integration for observability/tracing
   - Support for both Google AI Studio and Vertex AI

2. **Authentication & Configuration**
   - API key management through environment variables
   - Support for multiple auth methods (OAuth2 examples in samples)
   - Settings management via `.env` files

### Development Workflow

1. **Dependency Management**

   - Uses `uv` for fast Python dependency management
   - Use `uv add <package-name>` to add packages
   - Use `uv remove <package-name>` to remove packages
   - `pyproject.toml` defines all dependencies and scripts

## Key Implementation Notes

- CORS is configured to allow frontend applications (default: http://localhost:3000)
- The project uses Python 3.13+ features and modern async/await patterns
- The A2A samples demonstrate various agent frameworks (LangGraph, CrewAI, AutoGen, etc.)
