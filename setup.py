from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in diamondpharma/__init__.py
from diamondpharma import __version__ as version

setup(
	name="diamondpharma",
	version=version,
	description="diamondpharma customizations",
	author="oaktc",
	author_email="waelhammoudi71@gmain.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
