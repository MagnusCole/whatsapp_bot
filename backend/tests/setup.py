from setuptools import setup, find_packages

setup(
    name="whatsapp_bot_backend_tests",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "httpx",
        "fastapi",
        "sqlalchemy",
        "asyncpg",
    ],
)