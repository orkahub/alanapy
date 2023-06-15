from setuptools import setup

setup(
    name="alanapy",
    packages=["alanapy"],
    version="0.3",
    license="MIT",
    author = "Orkahub Energy",
	author_email = "orkahub@gmail.com",
	url = "https://github.com/orkahub/alanapy",
    long_description="Script for Alana API connection and functions https://alana.tech/open/accounts/login",
    long_description_content_type = "text/x-rst",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords= ["RESERVOIR", "ENERGY", "OIL", "GAS", "PRODUCTION", "PYTHON","ALANA"],
    install_requires=[
        "requests",
        "matplotlib",
        "numpy",
        "pandas",
		"datetime",
		"os",
		"re"
    ],
)
