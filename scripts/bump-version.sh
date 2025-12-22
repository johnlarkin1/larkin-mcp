#!/usr/bin/env bash
# NOTE: This is ai-generated
# so.... probably don't need to care about it
# 
# Here's the prompt I used:
#  Can you give me a script (and a Make) command so that I can bump the version
#  automatically? This should be a local script that uses the @.github/pr-labeler.yml
#  We should just have a single Make command and script using the branch name that
#  we're currently on.
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
COMMIT=false
DRY_RUN=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Bump version based on current branch name (per .github/pr-labeler.yml)"
    echo ""
    echo "Branch mapping:"
    echo "  major:  release/*, breaking/*"
    echo "  minor:  feature/*, feat/*"
    echo "  patch:  fix/*, hotfix/*, bugfix/*, chore/*, docs/*, refactor/*"
    echo ""
    echo "Options:"
    echo "  -c, --commit       Create a git commit with the version bump"
    echo "  -d, --dry-run      Show what would happen without making changes"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Bump version based on current branch"
    echo "  $0 -c              # Bump and commit"
    echo "  $0 -d              # Dry run"
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

# Get current version from Python (source of truth)
get_current_version() {
    grep -E '^version = ' "$ROOT_DIR/py/pyproject.toml" | sed 's/version = "\(.*\)"/\1/'
}

# Get current git branch
get_current_branch() {
    git rev-parse --abbrev-ref HEAD
}

# Determine bump type from branch name (matches .github/pr-labeler.yml)
get_bump_type() {
    local branch="$1"
    local prefix="${branch%%/*}"

    case "$prefix" in
        release|breaking)
            echo "major"
            ;;
        feature|feat)
            echo "minor"
            ;;
        fix|hotfix|bugfix|chore|docs|refactor)
            echo "patch"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Calculate new version based on bump type
calculate_new_version() {
    local current="$1"
    local bump_type="$2"

    IFS='.' read -r major minor patch <<< "$current"

    case "$bump_type" in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "$major.$((minor + 1)).0"
            ;;
        patch)
            echo "$major.$minor.$((patch + 1))"
            ;;
    esac
}

# Update Python version in pyproject.toml
update_py_version() {
    local version="$1"
    local file="$ROOT_DIR/py/pyproject.toml"

    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' "s/^version = \".*\"/version = \"$version\"/" "$file"
    else
        sed -i "s/^version = \".*\"/version = \"$version\"/" "$file"
    fi
    log_info "Updated py/pyproject.toml -> $version"
}

# Update TypeScript version in package.json
update_ts_version() {
    local version="$1"
    local file="$ROOT_DIR/tsx/package.json"

    if [[ -f "$file" ]]; then
        if [[ "$(uname)" == "Darwin" ]]; then
            sed -i '' "s/\"version\": \".*\"/\"version\": \"$version\"/" "$file"
        else
            sed -i "s/\"version\": \".*\"/\"version\": \"$version\"/" "$file"
        fi
        log_info "Updated tsx/package.json -> $version"
    else
        log_warn "tsx/package.json not found, skipping TypeScript"
    fi
}

# Update Rust version in Cargo.toml
update_rs_version() {
    local version="$1"
    local file="$ROOT_DIR/rs/Cargo.toml"

    if [[ -f "$file" ]]; then
        # Only update the package version (line starts with version =)
        # Dependency versions are inline like { version = "x" } so won't match
        if [[ "$(uname)" == "Darwin" ]]; then
            sed -i '' "s/^version = \".*\"/version = \"$version\"/" "$file"
        else
            sed -i "s/^version = \".*\"/version = \"$version\"/" "$file"
        fi
        log_info "Updated rs/Cargo.toml -> $version"
    else
        log_warn "rs/Cargo.toml not found, skipping Rust"
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--commit)
            COMMIT=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
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

cd "$ROOT_DIR"

# Get current branch and determine bump type
BRANCH=$(get_current_branch)
log_info "Current branch: $BRANCH"

BUMP_TYPE=$(get_bump_type "$BRANCH")

if [[ -z "$BUMP_TYPE" ]]; then
    log_error "Cannot determine bump type from branch: $BRANCH"
    echo ""
    echo "Branch must start with one of:"
    echo "  major:  release/, breaking/"
    echo "  minor:  feature/, feat/"
    echo "  patch:  fix/, hotfix/, bugfix/, chore/, docs/, refactor/"
    exit 1
fi

log_info "Bump type: $BUMP_TYPE"

# Get current and calculate new version
CURRENT_VERSION=$(get_current_version)
NEW_VERSION=$(calculate_new_version "$CURRENT_VERSION" "$BUMP_TYPE")

log_info "Current version: $CURRENT_VERSION"
log_info "New version: $NEW_VERSION"

if [[ "$DRY_RUN" == true ]]; then
    echo ""
    log_info "DRY RUN - Would update:"
    echo "  - py/pyproject.toml"
    echo "  - tsx/package.json"
    echo "  - rs/Cargo.toml"
    if [[ "$COMMIT" == true ]]; then
        echo "  - Create git commit: chore: bump version to $NEW_VERSION"
    fi
    exit 0
fi

# Update all files
update_py_version "$NEW_VERSION"
update_ts_version "$NEW_VERSION"
update_rs_version "$NEW_VERSION"

log_success "Version bumped to $NEW_VERSION"

# Optionally commit
if [[ "$COMMIT" == true ]]; then
    log_info "Creating git commit..."
    git add py/pyproject.toml tsx/package.json rs/Cargo.toml 2>/dev/null || true
    git commit -m "chore: bump version to $NEW_VERSION"
    log_success "Created commit for version $NEW_VERSION"
fi

echo ""
log_success "Done! Version is now $NEW_VERSION"
