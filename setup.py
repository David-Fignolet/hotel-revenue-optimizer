"""
Configuration du package Hotel Revenue Optimizer
"""
from setuptools import setup, find_packages
import os

# Lire le contenu du README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Dépendances principales
requirements = [
    # Core
    "pandas>=2.1.0",
    "numpy>=1.26.0",
    "python-dateutil>=2.8.2",
    "pytz>=2020.1",
    
    # Data Processing
    "scikit-learn>=1.3.0",
    "joblib>=1.3.0",
    
    # Visualization
    "matplotlib>=3.8.0",
    "seaborn>=0.13.0",
    "plotly>=5.15.0",
    
    # Web App
    "streamlit>=1.32.0",
    "tabula-py>=2.10.0",
    
    # Environment
    "python-dotenv>=1.0.0",
]

setup(
    name="hotel-revenue-optimizer",
    version="0.1.0",
    author="David Michel-Larrieux",
    author_email="contact@example.com",
    description="Outil d'optimisation des revenus hôteliers utilisant l'IA pour la prédiction de la demande et la tarification dynamique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    url="https://github.com/David-Fignolet/hotel-revenue-optimizer",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "": ["*.json", "*.csv", "*.pkl", "*.joblib"],
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hotel-revenue-optimizer=streamlit_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Hospitality Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Bug Reports": "https://github.com/David-Fignolet/hotel-revenue-optimizer/issues",
        "Source": "https://github.com/David-Fignolet/hotel-revenue-optimizer",
    },
)