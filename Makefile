.PHONY: help install lint format test test-cov clean dev setup check all

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies with uv"
	@echo "  lint        - Run flake8 linting"
	@echo "  format      - Format code with black"
	@echo "  format-check- Check code formatting with black"
	@echo "  test        - Run tests"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  clean       - Clean up cache files"
	@echo "  dev         - Run development server"
	@echo "  setup       - Run setup checker"
	@echo "  check       - Run all checks (lint, format-check, test)"
	@echo "  all         - Install, format, lint, and test"

# Install dependencies
install:
	uv sync

# Linting with flake8
lint:
	@echo "🔍 Running flake8 linting..."
	uv run flake8 src/ --statistics

# Format code with black
format:
	@echo "🎨 Formatting code with black..."
	uv run black src/ tests/

# Check formatting with black (no changes)
format-check:
	@echo "🎨 Checking code formatting..."
	uv run black --check --diff src/ tests/

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	uv run pytest tests/ \
		--cov=src/promptbin \
		--cov-report=term-missing \
		--cov-report=xml \
		--cov-fail-under=18 \
		-v \
		--tb=short

# Clean up cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -f coverage.xml 2>/dev/null || true

# Run development server
dev:
	@echo "🚀 Starting development server..."
	uv run promptbin

# Run setup checker
setup:
	@echo "⚙️  Running setup checker..."
	uv run promptbin-setup

# Run all checks (used by CI)
check: format-check lint test

# Complete workflow: install, format, lint, test
all: install format lint test-cov

# Development shortcuts
mcp:
	@echo "🔌 Starting MCP server only..."
	uv run promptbin --mcp

web:
	@echo "🌐 Starting web interface only..."
	uv run promptbin --web

# Install dev tunnels CLI
install-tunnel:
	@echo "🌐 Installing Dev Tunnels CLI..."
	uv run promptbin-install-tunnel