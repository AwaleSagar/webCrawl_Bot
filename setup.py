from setuptools import setup, find_packages

setup(
    name="webcrawl_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "nltk",
        "google-generativeai",
    ],
    python_requires=">=3.8",
    description="A keyword-based web crawler with database integration",
    author="AI Generated",
    author_email="example@example.com",
    url="https://github.com/AwaleSagar/webCrawl_Bot",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 