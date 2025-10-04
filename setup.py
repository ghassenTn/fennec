from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fennec",
    version="0.3.0",
    author="Ghassen",
    author_email="ghassen.xr@gmail.com",
    description="🦊 Fennec - A lightweight, fast, and agile Python backend framework built in Tunisia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ghassenTn/fennec",
    project_urls={
        "Bug Tracker": "https://github.com/ghassenTn/fennec/issues",
        "Documentation": "https://github.com/ghassenTn/fennec#readme",
        "Source Code": "https://github.com/ghassenTn/fennec",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    keywords="web framework api rest async asgi websocket graphql microservices",
    python_requires=">=3.8",
    install_requires=[
        "uvicorn>=0.20.0",  # ASGI server
    ],
    extras_require={
        "full": [
            # v0.2.0 features
            "bcrypt>=4.0.0",  # Password hashing
            "websockets>=10.0",  # WebSocket support
            
            # v0.3.0 features
            "redis>=4.5.0",  # Caching
            "prometheus-client>=0.16.0",  # Metrics
            "psutil>=5.9.0",  # System monitoring
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fennec=fennec.cli.commands:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
