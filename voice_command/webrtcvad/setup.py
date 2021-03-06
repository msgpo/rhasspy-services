import os
import setuptools

this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md"), "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name="webrtcvad_rhasspy",
    version="0.1",
    author="Michael Hansen",
    author_email="hansen.mike@gmail.com",
    url="https://github.com/synesthesiam/rhasspy-services",
    packages=setuptools.find_packages(),
    package_data={"webrtcvad_rhasspy": ["py.typed"]},
    install_requires=["jsonlines", "pyyaml", "pydash", "webrtcvad"],
    classifiers=["Programming Language :: Python :: 3"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["webrtcvad-cli=webrtcvad_rhasspy.__main__:main"]}
)
