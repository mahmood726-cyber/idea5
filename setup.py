"""
Setup script for Publication Bias Assessment Dashboard.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='publication-bias-dashboard',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Multi-Method Publication Bias Assessment Dashboard',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/publication-bias-dashboard',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'black>=23.0',
            'flake8>=6.0',
            'mypy>=1.0'
        ],
        'docs': [
            'sphinx>=7.0',
            'sphinx-rtd-theme>=1.2'
        ]
    },
    entry_points={
        'console_scripts': [
            'pub-bias-dashboard=src.dashboard.app:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['data/examples/*.csv'],
    },
    zip_safe=False,
)
