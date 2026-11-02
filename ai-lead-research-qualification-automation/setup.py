from setuptools import setup, find_packages

setup(
    name="leadpilot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # runtime dependencies are listed in requirements.txt; they will be installed separately
    ],
    entry_points={
        "console_scripts": [
            "run-dashboard=app.dashboard:main",
        ],
    },
)

