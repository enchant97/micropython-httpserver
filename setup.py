__version__ = "0.0.0"

from setuptools import setup


def long_description():
    with open("README.md", "r") as fo:
        return fo.read()


setup(
    name="micropython-httpserver",
    version=__version__,
    url="https://github.com/enchant97/micropython-httpserver",
    description="A MicroPython library for providing a asynchronous HTTP server",
    keywords=["micropython", "http"],
    long_description=long_description(),
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    packages=["httpserver"],
    classifiers=[
        "Private :: Do Not Upload",  # TODO remove when stable-ish
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: Implementation :: MicroPython",
        "License :: OSI Approved :: Apache Software License",
    ],
)
