from setuptools import setup, find_packages

setup(
    name="hlc",
    version="0.1.0",
    author="Ruzzel Maestro",
    author_email="rocketturtles.creative@gmail.com",
    description="Hierarchical Lexical Compression for LLM context optimization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Lezzur/hlc",
    packages=find_packages(),
    package_data={
        "hlc": ["codebooks/*.json"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "wordfreq>=3.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
)
