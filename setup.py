from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

classifiers = [
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
]  # TODO: Update this

_ = setup(
    name="mcl",  # TODO: Need to find a better name
    version="0.0.2",
    description="Control your micropython based MCU's with this library.",  # TODO: Change this too
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/semitov/SemiTOV-MCL",
    author="SemiTO-V",
    license="MIT",  # TODO: Change maybe
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=["pyserial"],
)
