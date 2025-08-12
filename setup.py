"""
Setup script for the AI Personal Assistant.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="ai-personal-assistant",
    version="0.1.0",
    author="AI Assistant Developer",
    author_email="developer@example.com",
    description="An intelligent AI personal assistant with long-term memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-personal-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-groq>=0.0.1",
        "langgraph>=0.0.20",
        "langchain-community>=0.0.10",
        "groq>=0.4.2",
        "chromadb>=0.4.22",
        "sentence-transformers>=2.2.2",
        "streamlit>=1.29.0",
        "streamlit-chat>=0.1.1",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-assistant=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="ai, assistant, chatbot, memory, langchain, langgraph, groq",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-personal-assistant/issues",
        "Source": "https://github.com/yourusername/ai-personal-assistant",
        "Documentation": "https://github.com/yourusername/ai-personal-assistant#readme",
    },
)
