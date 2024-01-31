#!/bin/bash

DIR=./readme_old
if [ -d "$DIR" ];
then
    echo "$DIR and readme.old are exists..."
else
    mkdir readme_old
    mv README.md readme_old/README.md
    git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
    git config --local user.name "github-actions[bot]"
    git add ./readme_old/*
    git commit -m "[Automatic] Update readme.old files" || echo "Nothing to update"
    

fi
