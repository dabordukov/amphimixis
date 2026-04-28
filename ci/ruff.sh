#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'

echo -e "${BLUE}Running linter Ruff...${NC}"
mapfile -t files < <(git ls-files ':/*.py' ':!:tests/')
uv run ruff check "${files[@]}"
