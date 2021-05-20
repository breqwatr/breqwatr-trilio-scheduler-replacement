"""Set up btsrworker"""
from setuptools import setup, find_packages

setup(
    name="btsrworker",
    packages=find_packages(),
    version="1.0",
    license="",
    description="Breqwatr Trilio Replacement Scheduler Worker",
    author="Kyle Pericak",
    author_email="kyle.pericak@breqwatr.com",
    python_requires='>=3.0.0',
    install_requires=["redis"],
    entry_points="""
        [console_scripts]
        btsr-worker=btsrworker.main:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
    ]
)
