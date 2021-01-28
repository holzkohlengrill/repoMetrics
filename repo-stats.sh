#!/bin/bash

# Dependencies for this script:
# * curl
# * python3 (for python script dependencies see 

REPO_URL=''
# REPO_URL for GitLab projects normally has the form (or similar)
# https://gitlab.com/api/v4/projects/<project-id>/?statistics=true&private_token=<personal-private-token>&per_page=99999"

if [[ "$#" -ge 1 ]]; then
    REPO_URL=$1
fi

if [[ ${REPO_URL} == "" ]]; then
    printf "Neither repository URL given nor default value set in script. Exiting...\n\n"
else
    curl ${REPO_URL} > ./proj-stats-tmp.json
     
    python -m json.tool ./proj-stats-tmp.json > ./proj-stats.json
    rm proj-stats-tmp.json
    python repoStats.py
fi
