"""
Project setup configuration file.

Permite instalar el paquete con: pip install -e .
O instalar con dependencias de desarrollo: pip install -e ".[dev]"
"""

from setuptools import setup, find_packages

setup(
    name="technical_test",
    version="1.0.0",
    description="Prueba técnica Proteccion: Cientifico de Datos",
    author="Beatriz Valentina Gomez Valencia",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "pandasql>=0.7.3",
        "matplotlib>=3.5.0",
        "folium>=0.12.0",
        "geopandas>=0.10.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "black>=21.0",
            "pylint>=2.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "technical_test=technical_test.answers.01_top_products:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
