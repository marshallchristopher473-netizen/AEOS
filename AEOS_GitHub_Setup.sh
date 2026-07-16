#!/bin/bash

# ============================================================
# AEOS_GitHub_Setup.sh
# AI Education Operations System (AEOS)
# GitHub Repository Initialization + First Deployment Setup
# ============================================================

set -e

echo "=========================================="
echo " AEOS GitHub Setup"
echo " AI Education Operations System"
echo "=========================================="

# Check Git installation
if ! command -v git &> /dev/null
then
    echo "Git is not installed. Install Git first."
    exit 1
fi

echo "✓ Git detected"

# Initialize repository if needed
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
else
    echo "✓ Existing Git repository detected"
fi

# Create .gitignore
echo "Creating .gitignore..."

cat > .gitignore <<EOF
# Dependencies
node_modules/
.pnpm-store/

# Environment Variables
.env
.env.local
.env.production

# Builds
dist/
build/
.next/

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Database
*.sqlite
*.db

# AI / ML Files
models/
embeddings/
vector_cache/

# Temporary
tmp/
temp/

# Testing
coverage/
EOF

echo "✓ .gitignore created"


# Create AEOS project documentation structure

echo "Creating AEOS documentation folders..."

mkdir -p docs
mkdir -p docs/architecture
mkdir -p docs/product
mkdir -p docs/research
mkdir -p docs/pilots

mkdir -p backend
mkdir -p frontend
mkdir -p agents
mkdir -p database


# Create README

echo "Creating README.md..."

cat > README.md <<EOF
# AEOS - AI Education Operations System

## Mission

AEOS is an AI-powered education operations platform designed to improve:

- Teacher productivity
- Student learning outcomes
- Parent engagement
- Assessment intelligence
- Special education workflows

## Core Systems

### 1. AI Assessment Engine
- Diagnostic assessments
- Rubric generation
- Standards alignment
- Feedback generation

### 2. Learning Intelligence Layer
- Student profiles
- Learning pathways
- Intervention recommendations

### 3. Education Operations Dashboard
- Teacher analytics
- Parent communication
- Progress monitoring

## Technology Stack

Frontend:
- React / Next.js

Backend:
- FastAPI

Database:
- PostgreSQL + pgvector

AI:
- Claude API
- RAG pipelines
- AI agents

## Development Status

Current Phase:
MVP Development

Priority:
Pilot → Validation → Revenue

EOF


# Create initial folders README files

touch backend/.gitkeep
touch frontend/.gitkeep
touch agents/.gitkeep
touch database/.gitkeep


# Initial commit

echo "Creating initial commit..."

git add .

git commit -m "Initial AEOS platform setup" || echo "Nothing new to commit"


echo ""
echo "=========================================="
echo " AEOS GitHub Setup Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create GitHub repository:"
echo "   https://github.com/new"
echo ""
echo "2. Connect repository:"
echo ""
echo "git remote add origin YOUR_GITHUB_REPO_URL"
echo ""
echo "3. Push AEOS:"
echo ""
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "=========================================="
