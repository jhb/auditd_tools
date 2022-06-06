import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auditd-tools",
    version="0.0.1",
    author="Joerg Baach",
    author_email="mail@baach.de",
    description="Python tools to handle auditd events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhb/auditd_tools",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    extras_require = {},
    package_dir={'auditd_tools':'.'},
    packages=['auditd_tools'],
    python_requires=">=3.6",
)