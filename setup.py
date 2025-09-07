#!/usr/bin/env python3
"""
Setup.py compatibility layer for PromptBin

This file provides compatibility with older pip versions and tools that expect setup.py.
All actual configuration is in pyproject.toml using the modern Python packaging standard.
"""

from setuptools import setup

# All configuration is in pyproject.toml
# This setup.py exists only for compatibility with older tools
if __name__ == "__main__":
    setup()