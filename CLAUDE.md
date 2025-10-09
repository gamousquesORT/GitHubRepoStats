# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GitHubTracker - A Python-based project (currently in initial setup phase).

## Project Structure

- **`src/`**: All source code goes under the `src/` folder

## Development Setup

This project uses Python with virtual environments. Set up your environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate

pip install -r requirements.txt  # once created
```

## Environment Configuration

This project uses environment variables stored in `.env` files (gitignored). Check for a `.env.example` or similar template when added.

## Code Style and Conventions

- **Use type hints**: Always use Python type hints for function parameters, return values, and class attributes. Use `typing` module types when needed (e.g., `List`, `Dict`, `Optional`, `Union`).
- **Object-Oriented Programming**: Prefer OOP patterns. Use classes to encapsulate related data and behavior. Follow SOLID principles where applicable.

## Testing and Commits

**Always run unit tests before committing.** Ensure all tests pass before creating commits.

## Current Status

The repository is in initial setup phase on branch `feat/get_repos`. The project structure and architecture will be documented here as development progresses.