#!/bin/bash

echo "Running yapf against branch $TRAVIS_BRANCH with commit $TRAVIS_COMMIT."
echo

git diff --name-only $TRAVIS_COMMIT
COMMIT_FILES=$(git diff --name-only $TRAVIS_COMMIT $TRAVIS_COMMIT^ | grep -i .py)
if [ -z "$COMMIT_FILES" ]; then
    echo "No files changed with postfix .py."
    exit 0
fi
echo "Changed files with postfix .py:"
for FILE in $COMMIT_FILES; do
    echo $FILE
done
echo

echo "Yapf diff on changed files:"
yapf --diff $COMMIT_FILES
RESULT_OUTPUT=$(yapf --diff $COMMIT_FILES)
echo

if [ -z "$RESULT_OUTPUT" ]; then
    echo "Yapf did not apply any formatting."
    exit 0
fi
echo "Please fix the formatting using the diff shown above."
exit 1
