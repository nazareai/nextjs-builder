from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="nextjs-builder",
    version="0.1.0",
    author="0xroyce369",
    author_email="nazareaicom@gmail.com",
    description="A module for building Next.js websites with Tailwind CSS using LangChain and OpenRouter from NazareAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nazareai/nextjs-builder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.5.1",
            "pre-commit>=3.3.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "nextjs-builder=nextjs_builder.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nextjs_builder": ["prompts/*.txt", "prompts/*/*.txt", "templates/*/*.json"],
    },
)