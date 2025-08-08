from setuptools import find_packages, setup

setup(
    name="clean_backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
        "fastapi",
        "pydantic",
    ],
)