#!/bin/sh
set -e

cd "$(dirname "$0")"

git pull

python3 sync_new_posts.py

git add _posts/ images/

if git diff --staged --quiet; then
  echo "No new posts to commit."
else
  git commit -m "Add new Instagram posts"
  git push
  echo "Changes pushed."
fi
