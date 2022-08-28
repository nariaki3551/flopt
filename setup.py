from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flopt",
    packages=find_packages() + ["datasets"],
    include_package_data=True,
    package_data={
        "datasets": [
            "tspLib/atsp/*.atsp",
            "tspLib/hcp/*.hcp",
            "tspLib/tsp/*.tsp",
            "tspLib/vrp/*.vrp",
            "tspLib/sop/*.sop",
            "funcLib/*",
            "mipLib/*",
        ]
    },
    version="0.5.4",
    license="MIT",
    install_requires=[
        "numpy",
        "sympy",
        "matplotlib==3.5.2",
        "pulp",
        "optuna==2.10.1",
        "hyperopt",
        "cvxopt",
        "amplify",
        "pytest",
        "scipy",
    ],
    author="nariaki tateiwa",
    author_email="nariaki3551@gmail.com",
    url="https://flopt.readthedocs.io/en/latest/index.html",
    description="A python Non-Linear Programming API with Heuristic approach",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="optimization nonliear search heuristics algorithm",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
