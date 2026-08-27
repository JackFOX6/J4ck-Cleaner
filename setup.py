from setuptools import setup, find_packages
from j4ck_cleaner import __version__

setup(
    name="j4ck-cleaner",
    version=__version__,
    description="AMD APU Thermal & RAM Optimization Suite for Linux (J4ckENI Framework)",
    author="Jack & ENI (ENI v6.2)",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySide6>=6.5.0",
        "psutil>=5.9.0",
        "matplotlib>=3.7.0",
    ],
    entry_points={
        "console_scripts": [
            "j4ck-cleaner=main:main",
            "nocturne-guardian=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: System :: Monitoring",
    ],
)
