import os
import sys

from setuptools import setup, find_packages

root_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_path, 'README.md')) as f:
    README = f.read()
with open(os.path.join(root_path, 'CHANGES.md')) as f:
    CHANGES = f.read()

sys.path.insert(0, os.path.join(root_path, 'src'))

version = __import__('configfactory').__version__

requires = [
    'django==2.1.5',
    'django-filter==2.0.0',
    'django-guardian==1.4.9',
    'django-crispy-forms==1.7.2',
    'django-debug-toolbar==1.11',
    'djangorestframework==3.9.1',
    'dj-static==0.0.6',
    'dj-database-url==0.5.0',
    'dataclasses==0.6',
    'cryptography==2.3.1',
    'click==7.0',
    'pytz==2018.7',
    'jsonschema==2.6.0',
    'gunicorn==19.9.0',
    'apscheduler==3.5.3',
    'packaging==17.1',
    'appdirs==1.4.3',
    'arrow==0.13.0',
    'colorlog==4.0.2',
    'dictdiffer==0.7.1',
    'faker==1.0.1',
    'factory-boy==2.9.2'
]

setup(
    name='configfactory',
    version=version,
    description='Distributed configurations manager',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages('src', exclude=['tests']),
    package_dir={
        '': 'src',
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'pytest-django',
        ],
        'mysql': [
            'mysqlclient==1.3.12',
        ]
    },
    entry_points={
        'console_scripts': [
            'configfactory = configfactory.cli:main',
        ],
    },
)
