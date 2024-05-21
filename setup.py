from setuptools import setup, find_packages

setup(
    name="imagededup-cli",  # Package name
    version="1.0.0",  # Initial version
    author="Tadeas Fort",
    author_email="taddy.fort@gmail.com",
    description="A tool to remove duplicate jpg images",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tadeasf/imagededup-cli",  # Project URL
    packages=find_packages(),
    install_requires=[
        "click",
        "tk",
        "tqdm",
        "loguru",
        "imagededup",
    ],
    entry_points={
        "console_scripts": [
            "imagededup-cli = imagededup_cli.imagededup_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
