#!/bin/sh
set -e

if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable is required"
  exit 1
fi

GITHUB_REPO="${GITHUB_REPO:-kiwiidb/zij.was.eens}"
REPO_URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git"

echo "Cloning repository..."
git clone "$REPO_URL" /repo
cd /repo

echo "Running sync..."
python sync_new_posts.py

echo "Committing changes..."
git config user.name "docker-scraper"
git config user.email "docker-scraper@zijwaseens.be"
git add _posts/ images/

if git diff --staged --quiet; then
  echo "No new posts to commit."
else
  git commit -m "Add new Instagram posts"
  git push
  echo "Changes pushed."
fi
