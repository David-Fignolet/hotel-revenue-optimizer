"""
Configuration du package Hotel Revenue Optimizer
"""
from setuptools import setup, find_packages
import os

# Lire le contenu du README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lire les dépendances depuis requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip() 
        for line in f.readlines() 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="hotel-revenue-optimizer",
    version="0.1.0",
    author="David Michel-Larrieux",
    author_email="contact@example.com",
    description="Outil d'optimisation des revenus hôteliers utilisant l'IA pour la prédiction de la demande et la tarification dynamique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.10',  # Compatible with Python 3.10+
    url="https://github.com/votre-username/hotel-revenue-optimizer",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={
        "": ["*.json", "*.csv", "*.pkl", "*.joblib"],
    },
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Hospitality Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    entry_points={
        "console_scripts": [
            "hotel-revenue-optimizer=streamlit_app:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/votre-username/hotel-revenue-optimizer/issues",
        "Source": "https://github.com/votre-username/hotel-revenue-optimizer",
    },
)
