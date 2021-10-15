from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flopt',
    packages=find_packages()+['datasets'],
    include_package_data=True,
    package_data={
        "datasets": [
            "tspLib/atsp/*.atsp",
            "tspLib/hcp/*.hcp",
            "tspLib/tsp/*.tsp",
            "tspLib/vrp/*.vrp",
            "tspLib/sop/*.sop"
        ]
    },
    version='0.5',
    license='MIT',
    install_requires=[
        'numpy',
        'sympy',
        'matplotlib',
        'pulp',
        'optuna',
        'hyperopt',
        'cvxopt',
        'amplify',
        'sphinx',
        'sphinx-autobuild',
        'sphinx_rtd_theme',
        'sphinxcontrib-mermaid',
        'recommonmark',
        'pytest'
    ],
    author='nariaki tateiwa',
    author_email='nariaki3551@gmail.com',
    url='https://flopt.readthedocs.io/en/latest/index.html',
    description='A python Non-Linear Programming API with Heuristic approach',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='optimization nonliear search heuristics algorithm',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
