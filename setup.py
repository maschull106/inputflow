from setuptools import setup, find_packages
import pathlib


PACKAGE_NAME = "inputflow"
VERSION = "0.1.0" 
DESCRIPTION = "Cross-platform input event handling for different devices (gamepads, keyboards, mice, etc)"
here = pathlib.Path(__file__).parent.resolve()
LONG_DESCRIPTION = (here / "README.md").read_text(encoding="utf-8")

setup(
        name=PACKAGE_NAME, 
        version=VERSION,
        author="Matthias Schuller",
        author_email="matthiasshuller92@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url="https://github.com/yourusername/inputflow",
        packages=find_packages(),
        python_requires=">=3.9",
        install_requires=[
                "pynput",
        ],
        include_package_data=True,
        package_data={
        },
        keywords=["python, input, event, gamepad, keyboard, mouse"],
)