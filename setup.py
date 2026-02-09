from setuptools import setup, find_packages

setup(
    name="resend-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["click>=8.0", "requests>=2.28", "rich>=13.0"],
    extras_require={"dev": ["pytest>=7.0", "pytest-cov"]},
    entry_points={"console_scripts": ["resend-cli=resend_cli.cli:main"]},
    python_requires=">=3.10",
)
