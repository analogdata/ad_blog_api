---
trigger: glob
globs: *.py, *.sql, *.toml, *.yml,
---

You are an expert in Python Programming, FastAPI, SQLModel, Alembic, Pytest, Docker and related Python Techniques

Code Style and Structure
- Write clean, efficient, and well-documented Python code with accurate FastAPI examples
- Follow PEP8 style guide for Python code
- Use type hints consistently throughout the codebase
- Optimize for readability over premature optimization
- Use descriptive function and variable names following snake_case convention
- Structure FastAPI applications: routers, services, models, schemas, configurations
- Majority of the time I'll keep running my fastapi server on the backend.
- Always use ``cd {current_working_directory} && uv run` to run Python commands, make sure that you've changed to current working directory before you run for example `cd {current_working_directory} && uv run

Dependencies
- FastAPI
- Pydantic v2
- SQLModel

FastAPI Specifics
- Implement RESTful API design patterns when creating web services
- Use Pydantic models for request/response validation
- Implement proper exception handling using FastAPI's HTTPException
- Use dependency injection for services and database connections
- Utilize FastAPI's auto-documentation features effectively

Database and ORM
- Use SQLModel for database operations
- Use Alembic for database migrations
- Implement proper database connection pooling
- Use Sync database operations
- Majorly we use AWS RDS for Production
- For Development/Testing we use PostgreSQL Running on Docker

Testing and Quality Assurance
- Use Pytest for testing
- Only Write Unit Tests when asked for it.
- Write unit tests for all service functions
- Write integration tests for API endpoints
- Implement proper mocking for external services

Deployment and Infrastructure
- Use Docker for containerization
- Use environment variables for configuration
- Implement proper logging for debugging and monitoring
- Use async/await for I/O operations to improve performance
- Always use ``cd {current_working_directory} && uv run` to run Python commands