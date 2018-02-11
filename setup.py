from setuptools import setup, find_packages

long_description = ""

setup(
    name='piper_core',
    version='0.11',
    description='Piper CI Core',
    long_description=long_description,
    packages=find_packages(),
    package_dir={'piper_core': 'piper_core'},
    author='Martin Franc',
    author_email='francma6@fit.cvut.cz',
    keywords='ci,github',
    license='Public Domain',
    url='https://github.com/francma/piper-ci-core',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'piper-core = piper_core.run:main',
            'piper-shell = piper_core.shell:main',
        ]
    },
    install_requires=[
        'peewee>=3',
        'Flask>=0.12',
        'pyyaml>=3',
        'redis>=2',
        'simpleeval>=0.9',
        'jsonschema>=2.6',
        'requests>=2.18',
    ],
    extras_require={
        'dev': [
            # type checking
            'mypy',
            'tox',
            'coveralls',
            'pytest>=3',
            'pytest-cov',
        ],
    },
)
