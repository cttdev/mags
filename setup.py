from setuptools import setup

setup(
    name="mags",
    packages=["mags"],
    include_package_data=True,
    install_requires=[
        "Flask",
        "Flask-SocketIO",
        "libsass",
        "chess",
        "stockfish",
        "pybind11"
    ],
)