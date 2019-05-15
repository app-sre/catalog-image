from setuptools import find_packages
from setuptools import setup

setup(
    name="catalog-image",
    version="0.1.0",
    license="BSD",

    author="Red Hat App-SRE Team",
    author_email="sd-app-sre@redhat.com",

    description="Tools to create OLM catalog images",

    packages=find_packages(exclude=('tests',)),

    install_requires=[
        "Click==7.0",
        "PyYAML>=3.10",
        "GitPython==2.1.11",
    ],

    test_suite="tests",

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'catalog-image=catalog_image.cli:run',
        ],
    },
)
