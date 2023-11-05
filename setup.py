from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="alanapy",
    version="1.3.1",
    license="MIT",
    packages=find_packages(),
    package_data={
        'alanapy': ['config.yaml'],  # Specify the path to your required files
    },
    author = "Orkahub Energy",
	author_email = "orkahub@gmail.com",
	url = "https://github.com/orkahub/alanapy",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type = "text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords= ["RESERVOIR", "ENERGY", "OIL", "GAS", "PRODUCTION", "PYTHON", "ALANA"],
    install_requires=[
        "requests",
        "matplotlib",
        "numpy",
        "pandas",
        "folium",
        "bokeh",

    ],
)
