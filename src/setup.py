from setuptools import setup, find_packages

setup(
    name="mev-resistant-dex",
    version="1.0.0",
    description="MEV-Resistant DEX Backtester with Slippage Protection",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "matplotlib>=3.5.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
