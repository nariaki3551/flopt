import os
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flopt",
    packages=find_packages(),
    package_data={
        "flopt": ["flopt.config"],
    },
    include_package_data=True,
    version="0.5.6",
    license="MIT",
    install_requires=[
        "numpy",
        "sympy",
        "matplotlib",
        "pulp",
        "optuna",
        "hyperopt",
        "cvxopt",
        "amplify",
        "pytest",
        "scipy",
        "scikit-learn",
        "dill",
        "pooch",
        "timeout_decorator",
        "colorlog",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
