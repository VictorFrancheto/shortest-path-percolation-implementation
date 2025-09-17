from setuptools import setup, find_packages

setup(
    name="quantum-network-simulator",
    version="0.1.0",
    description="🌐 Quantum Photonic Network Simulator using Waxman graphs",
    author="Seu Nome",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "networkx"
    ],
    entry_points={
        "console_scripts": [
            "qnet=quantum_network.cli:main"
        ]
    },
    python_requires=">=3.9",
)
