from setuptools import setup
with open("README.md","r",encoding="utf-8") as fh:
    long_description=fh.read()

setup(
    name="slash_help",
    version="1.0.2",
    description="Slash commands help for discord-interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toricane/SlashHelp",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="MIT",
    packages=["slash_help"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["discord-py-interactions", "discord.py", "dinteractions-Paginator"],
)
