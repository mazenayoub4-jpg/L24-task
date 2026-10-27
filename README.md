# L24 Task - FastAPI Agent Service

This repository contains a FastAPI web application designed to handle Arabic query answering with source attribution and conversation history tracking.

## Project Structure
- `app.py`: Main FastAPI application entry point.
- `AGENTS.md`: Agent instruction setup and guidelines for AI assistant workflows.
- `requirements.txt`: Project Python dependencies.
- `L24-check.py`: Test checker script for validating endpoint responses locally or remotely.

## Execution
To run the server locally:
```bash
uvicorn app:app --reload --port 8099
