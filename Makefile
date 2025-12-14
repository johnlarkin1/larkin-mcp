.PHONY: help setup setup-py setup-ts setup-rs \
        run-py run-ts run-rs \
        dev-py dev-ts dev-rs \
        lint lint-py lint-ts lint-rs \
        format format-py format-ts format-rs \
        check check-py check-ts check-rs \
        clean clean-py clean-ts clean-rs

# Default target
help:
	@echo "larkin-mcp Makefile"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Setup all language implementations"
	@echo "  make setup-py       - Setup Python (uv sync)"
	@echo "  make setup-ts       - Setup TypeScript (bun install)"
	@echo "  make setup-rs       - Setup Rust (cargo build)"
	@echo ""
	@echo "Run Commands (production):"
	@echo "  make run-py         - Run Python MCP server"
	@echo "  make run-ts         - Run TypeScript MCP server"
	@echo "  make run-rs         - Run Rust MCP server"
	@echo ""
	@echo "Dev Commands (with inspector):"
	@echo "  make dev-py         - Run Python MCP server in dev mode"
	@echo "  make dev-ts         - Run TypeScript MCP server in dev mode"
	@echo "  make dev-rs         - Run Rust MCP server in dev mode"
	@echo ""
	@echo "Lint/Format Commands:"
	@echo "  make lint           - Lint all implementations"
	@echo "  make format         - Format all implementations"
	@echo "  make check          - Check formatting (no changes)"
	@echo ""
	@echo "Clean Commands:"
	@echo "  make clean          - Clean all build artifacts"

# =============================================================================
# Setup Commands
# =============================================================================

setup: setup-py setup-ts setup-rs
	@echo "All implementations set up successfully!"

setup-py:
	@echo "Setting up Python..."
	cd py && uv sync

setup-ts:
	@echo "Setting up TypeScript..."
	cd tsx && bun install

setup-rs:
	@echo "Setting up Rust..."
	cd rs && cargo build

# =============================================================================
# Run Commands (Production - stdio transport)
# =============================================================================

run-py:
	@echo "Running Python MCP server..."
	cd py && uv run mcp run src/main.py

run-ts:
	@echo "Running TypeScript MCP server..."
	cd tsx && bun run src/index.ts

run-rs:
	@echo "Running Rust MCP server..."
	cd rs && cargo run --release

# =============================================================================
# Dev Commands (with MCP Inspector)
# =============================================================================

dev-py:
	@echo "Running Python MCP server in dev mode..."
	cd py && uv run mcp dev src/main.py

dev-ts:
	@echo "Running TypeScript MCP server in dev mode..."
	cd tsx && bunx @anthropic/mcp-inspector bun run src/index.ts

dev-rs:
	@echo "Running Rust MCP server in dev mode..."
	cd rs && cargo run

# =============================================================================
# Lint Commands
# =============================================================================

lint: lint-py lint-ts lint-rs
	@echo "All linting complete!"

lint-py:
	@echo "Linting Python with ruff..."
	cd py && uv run ruff check .

lint-ts:
	@echo "Linting TypeScript with prettier..."
	npx prettier --check "tsx/**/*.{ts,tsx,js,jsx,json}"

lint-rs:
	@echo "Checking Rust formatting..."
	cd rs && cargo fmt --check

# =============================================================================
# Format Commands
# =============================================================================

format: format-py format-ts format-rs
	@echo "All formatting complete!"

format-py:
	@echo "Formatting Python with ruff..."
	cd py && uv run ruff check --fix . && uv run ruff format .

format-ts:
	@echo "Formatting TypeScript with prettier..."
	npx prettier --write "tsx/**/*.{ts,tsx,js,jsx,json}"

format-rs:
	@echo "Formatting Rust with cargo fmt..."
	cd rs && cargo fmt

# =============================================================================
# Check Commands (verify formatting without changes)
# =============================================================================

check: check-py check-ts check-rs
	@echo "All checks complete!"

check-py:
	@echo "Checking Python formatting..."
	cd py && uv run ruff check . && uv run ruff format --check .

check-ts:
	@echo "Checking TypeScript formatting..."
	npx prettier --check "tsx/**/*.{ts,tsx,js,jsx,json}"

check-rs:
	@echo "Checking Rust formatting..."
	cd rs && cargo fmt --check

# =============================================================================
# Clean Commands
# =============================================================================

clean: clean-py clean-ts clean-rs
	@echo "All clean!"

clean-py:
	@echo "Cleaning Python..."
	cd py && rm -rf .venv __pycache__ .ruff_cache .pytest_cache
	find py -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find py -type f -name "*.pyc" -delete 2>/dev/null || true

clean-ts:
	@echo "Cleaning TypeScript..."
	cd tsx && rm -rf node_modules dist .bun

clean-rs:
	@echo "Cleaning Rust..."
	cd rs && cargo clean
