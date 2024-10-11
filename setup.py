from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Input Manager'
LONG_DESCRIPTION = 'AAAAAAAAA'
PACKAGE_NAME = "input_manager"

setup(
        name=PACKAGE_NAME, 
        version=VERSION,
        author="Matthias Schuller",
        author_email="<matthiasshuller92@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        include_package_data=True,
        package_data={
        },
        keywords=['python'],
)