"""Setup configuration for ldap-schema package."""

from setuptools import setup, find_packages

setup(
    name="ldap-schema",
    version="0.1.0",
    description="LDAP schema models and configuration loader",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
)
