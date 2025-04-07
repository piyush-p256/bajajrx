from setuptools import setup, find_packages
from typing import List


def get_requirements() -> List[str]:

    requirement_list:List[str] = []

    return requirement_list

setup(
    name="shl",
    version="0.0.1",
    author="Dhananjay",
    author_email="dhananjayaggarwal6561@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)


