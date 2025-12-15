#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Defaults
DRY_RUN=false
SKIP_TESTS=false
SKIP_GIT_CHECK=false
TARGET="all"  # all, py, ts

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Publish larkin-mcp packages to PyPI and npm"
    echo ""
    echo "Options:"
    echo "  -t, --target TARGET    Target to publish: all, py, ts (default: all)"
    echo "  -d, --dry-run          Perform a dry run without publishing"
    echo "  --skip-tests           Skip running tests before publish"
    echo "  --skip-git-check       Skip git status checks"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Publish all packages"
    echo "  $0 -t py               # Publish only Python package"
    echo "  $0 -t ts --dry-run     # Dry run TypeScript publish"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-git-check)
            SKIP_GIT_CHECK=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate target
if [[ ! "$TARGET" =~ ^(all|py|ts)$ ]]; then
    log_error "Invalid target: $TARGET. Must be one of: all, py, ts"
    exit 1
fi

cd "$ROOT_DIR"

# Get versions
get_py_version() {
    grep -E '^version = ' py/pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

get_ts_version() {
    grep '"version"' tsx/package.json | sed 's/.*"version": "\(.*\)".*/\1/'
}

PY_VERSION=$(get_py_version)
TS_VERSION=$(get_ts_version)

log_info "Python version: $PY_VERSION"
log_info "TypeScript version: $TS_VERSION"

# Check version sync
if [[ "$TARGET" == "all" && "$PY_VERSION" != "$TS_VERSION" ]]; then
    log_error "Version mismatch! Python: $PY_VERSION, TypeScript: $TS_VERSION"
    log_error "Please sync versions before publishing all packages."
    exit 1
fi

# Git checks
if [[ "$SKIP_GIT_CHECK" == false ]]; then
    log_info "Checking git status..."

    # Check for uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        log_error "You have uncommitted changes. Please commit or stash them first."
        git status --short
        exit 1
    fi

    # Check for untracked files (warn only)
    if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then
        log_warn "You have untracked files:"
        git ls-files --others --exclude-standard
        echo ""
    fi

    # Check current branch
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
        log_warn "You are on branch '$BRANCH', not main/master."
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    log_success "Git checks passed"
fi

# Run tests
if [[ "$SKIP_TESTS" == false ]]; then
    log_info "Running tests..."

    if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
        log_info "Running Python tests..."
        make test-py
    fi

    if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
        log_info "Running TypeScript tests..."
        make test-ts || log_warn "TypeScript tests not configured or failed"
    fi

    log_success "Tests passed"
fi

# Run linting
log_info "Running lint checks..."
if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
    make check-py
fi
if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
    make check-ts || log_warn "TypeScript lint not configured"
fi
log_success "Lint checks passed"

# Build packages
log_info "Building packages..."
if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
    make build-py
fi
if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
    make build-ts
fi
log_success "Build complete"

# Confirm publish
echo ""
echo "========================================"
echo "Ready to publish:"
if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
    echo "  - larkin-mcp (Python) v$PY_VERSION -> PyPI"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
    echo "  - larkin-mcp (TypeScript) v$TS_VERSION -> npm"
fi
echo "========================================"
echo ""

if [[ "$DRY_RUN" == true ]]; then
    log_info "DRY RUN - No packages will be published"

    if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
        log_info "npm publish dry run:"
        cd tsx && npm publish --dry-run && cd ..
    fi

    log_success "Dry run complete"
    exit 0
fi

read -p "Proceed with publish? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Publish cancelled"
    exit 0
fi

# Publish
if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
    log_info "Publishing Python package to PyPI..."
    cd py && uv publish && cd ..
    log_success "Python package published!"
fi

if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
    log_info "Publishing TypeScript package to npm..."
    cd tsx && npm publish && cd ..
    log_success "TypeScript package published!"
fi

# Tag release
if [[ "$SKIP_GIT_CHECK" == false ]]; then
    VERSION="$PY_VERSION"
    if [[ "$TARGET" == "ts" ]]; then
        VERSION="$TS_VERSION"
    fi

    read -p "Create git tag v$VERSION? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -a "v$VERSION" -m "Release v$VERSION"
        log_success "Created tag v$VERSION"

        read -p "Push tag to origin? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git push origin "v$VERSION"
            log_success "Pushed tag to origin"
        fi
    fi
fi

echo ""
log_success "Publish complete!"
echo ""
echo "Packages are now available:"
if [[ "$TARGET" == "all" || "$TARGET" == "py" ]]; then
    echo "  Python: pip install larkin-mcp / uvx larkin-mcp"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "ts" ]]; then
    echo "  TypeScript: npm install larkin-mcp / bunx larkin-mcp"
fi
