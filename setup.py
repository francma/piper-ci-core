from setuptools import setup, find_packages

long_description = ""

setup(
    name='piper_driver',
    version='0.11',
    description='Piper CI LXD Driver',
    long_description=long_description,
    packages=find_packages(),
    package_dir={'piper_driver': 'piper_driver'},
    author='Martin Franc',
    author_email='francma6@fit.cvut.cz',
    keywords='lxd,ci,runner',
    license='Public Domain',
    url='https://github.com/francma/piper-ci-lxd-runner',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'piper_driver = piper_driver.run:run'
        ]
    },
    install_requires=[
        'click',
        'peewee',
        'uwsgi',
        'Flask>=0.12',
        'pyyaml',
        'redis',
        'simpleeval',
        'requests',
        'texttable',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
