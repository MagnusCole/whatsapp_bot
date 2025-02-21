from setuptools import setup, find_packages

setup(
    name="whatsapp_bot_backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0,<0.69.0",
        "uvicorn>=0.15.0,<0.16.0",
        "pydantic>=1.8.0,<2.0.0",
        "psycopg2-binary>=2.9.1,<3.0.0",
        "websockets>=10.0,<11.0",
        "python-dotenv>=0.19.0,<0.20.0",
        "pytest>=8.2.0",
        "requests>=2.26.0,<3.0.0",
        "sqlalchemy>=2.0.0",
        "asyncpg>=0.28.0",
        "pytest-asyncio>=0.25.0",
        "pytest-cov>=4.1.0",
        "httpx>=0.25.0"
    ],
)