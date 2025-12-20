from setuptools import setup

setup(
    name="http-replay-proxy",
    version="0.1.0",
    author="Arya Sianati",
    packages=["http_replay_proxy"],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "http-replay-proxy=http_replay_proxy.cli:cli",
        ],
    },
    install_requires=[],  # from requirements.txt
)