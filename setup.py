from setuptools import setup, find_packages


setup(
    name="mags",
    packages=find_packages(
        where="mags/python",
    ),
    package_dir={"": "mags/python"},
    include_package_data=True,
    install_requires=[
        "matplotlib",
        "numpy",
        "Flask",
        "Flask-SocketIO",
        "libsass",
        "chess",
        "stockfish",
        "cairosvg",
        "jsonrpc",
        "simple-websocket",
        "gpiozero",
        "pybind11[global]"
    ],
)