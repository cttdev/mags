from setuptools import setup, find_packages


setup(
    name="mags",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask",
        "Flask-SocketIO",
        "libsass",
        "chess",
        "stockfish",
        "cairosvg",
        "pybind11[global]"
    ],
)