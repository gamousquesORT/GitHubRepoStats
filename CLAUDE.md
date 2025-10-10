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

- **Use Environment Variables for Configuration**: All configuration that can be done using environment variables MUST be done that way. Never hardcode configuration values.
- **Required Environment Variables**: Use `.env` files (gitignored) to store environment-specific configuration.
- **Provide `.env.example`**: Always provide a `.env.example` file as a template showing required environment variables (without actual secrets).
- **Configuration Priority**:
  1. Environment variables (highest priority)
  2. `.env` file
  3. Default values (if safe to have defaults)
- **Examples of what should be environment variables**:
  - API keys and tokens (GitHub token, etc.)
  - API endpoints and URLs
  - Database connection strings
  - Feature flags
  - Service timeouts and retry limits
  - Any value that differs between environments (dev/staging/prod)

## Code Style and Conventions

- **Use type hints**: Always use Python type hints for function parameters, return values, and class attributes. Use `typing` module types when needed (e.g., `List`, `Dict`, `Optional`, `Union`).
- **Object-Oriented Programming**: Prefer OOP patterns. Use classes to encapsulate related data and behavior. Follow SOLID principles where applicable.

## Testing and Commits

- **Test-Driven Development (TDD)**: Follow classic Chicago-style TDD for all new classes and functionality:
  1. **Red**: Write a failing test first that defines the desired behavior
  2. **Green**: Write the minimal code needed to make the test pass
  3. **Refactor**: Improve the code while keeping tests green
  - Write tests before implementation code
  - Focus on state verification (not interaction testing)
  - Tests should verify the output/state of the system under test
- **Unit Tests Required**: Every class must have comprehensive unit tests. Test files should be created in the `tests/` directory mirroring the source structure.
- **Run Tests Before Committing**: Always run unit tests before committing. Ensure all tests pass before creating commits.
- **Test Coverage**: Aim for comprehensive test coverage including:
  - Happy path scenarios
  - Edge cases and boundary conditions
  - Error handling and exceptions
  - Input validation

## Current Status

The repository is in initial setup phase on branch `feat/get_repos`. The project structure and architecture will be documented here as development progresses.