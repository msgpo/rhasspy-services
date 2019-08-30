import os
import setuptools

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="fsticuffs",
    version="0.1",
    author="Michael Hansen",
    author_email="hansen.mike@gmail.com",
    url="https://github.com/synesthesiam/rhasspy-services",
    packages=setuptools.find_packages(),
    package_data={"fsticuffs": ["py.typed"]},
    install_requires=["jsonlines", "pyyaml", "pydash", "openfst==1.6.9"],
    classifiers=["Programming Language :: Python :: 3"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["fsticuffs-cli=fsticuffs.__main__:main"]}
)
