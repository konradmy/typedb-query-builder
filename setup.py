import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="typedb_query_builder",
    version="0.0.4",
    author="Konrad Mysliwiec",
    author_email="konradmy@gmail.com",
    description="A lightweight package for building TypeDB queries.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konradmy/typedb-query-builder",
    project_urls={
        "Bug Tracker":
            "https://github.com/konradmy/typedb-query-builder/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "typedb_query_builder"},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)
