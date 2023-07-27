import setuptools

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name="wokelib",
    version="0.0.1",
    author="Kyle Hegeman",
    description="Collection of utilities for using woke",
    long_description="An opionated collection of decorators and functions I use for fuzz testing smart contracts with Woke.",
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=requirements,
)