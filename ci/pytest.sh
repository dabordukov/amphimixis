#!/bin/bash
BLUE='\e[34m'
NC='\e[0m'

echo -e "${BLUE}Running PyTest...${NC}"
root=$(git rev-parse --show-toplevel)
PYTHONPATH=$root uv run pytest "$root"
