


# Requirements for migration management:
- For the migration name, use the project version(X.X.X);
- Optionally, after the project version, you can specify a short name with a hyphen;
- Don't create a lot of small migrations, group changes by project version.


# Auto-generate migration example

    alembic revision --autogenerate -m "0.1.0"


# Make migrations

    alembic upgrade head

# Downgrade migrations

    alembic downgrade -N

N - number of migrations

Example

    alembic downgrade -1

    