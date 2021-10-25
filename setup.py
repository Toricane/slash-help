from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="slash_help",
    version="2.0.5",
    description="discord-py-interactions slash command help",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toricane/slash-help",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="GNU",
    packages=["slash_help"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "discord-py-interactions",
        "discord.py",
        "dinteractions-Paginator",
        "thefuzz",
        "Levenshtein",
    ],
)
