"""Set up btsrlib"""
from setuptools import setup, find_packages

setup(
    name="btsrlib",
    packages=find_packages(),
    version="1.0",
    license="",
    description="Breqwatr Trilio Replacement Scheduler Lib",
    author="Kyle Pericak",
    author_email="kyle.pericak@breqwatr.com",
    python_requires='>=3.0.0',
    install_requires=[
      "redis",
      "python-openstackclient",
      "storops"
    ],
    entry_points="""
        [console_scripts]
        btsr-lib=btsrlib.main:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
    ]
)
