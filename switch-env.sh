#!/usr/bin/env bash

# Creates a hard link of the YAML files into the current directory from a path.
# The files must start with one of the following names: config data html
# It is also case insensitive.
# The script will search for these files and copy it to their expected names
# for the program to run.
# 
# The hard links are created with the first matching file in the given path.
# Any subsequent files will be ignored if a match for one has already been found.
#
# WARNING: This overwrites the files in the root directory. Ensure there
# are backups for these files if they are needed.
#
# Arguments:
#   $1: The path to the directory containing the YAML files

if [[ -z $1 ]]; then
    echo "No path given, path argument is required"
    exit 1
elif [[ ! -e $1 ]]; then
    echo "Path does not exist"
    exit 1
elif [[ ! -d $1 ]]; then
    echo "Path must be a directory"
    exit 1
fi

path=$1
file_names=("config" "data" "html")

for file in "$1"/*; do
    removeName=""
    file=$(awk '{ print tolower($0) }' <<< $file)

    for name in ${file_names[@]}; do
        regex=".*/$name.*\.(yml|yaml)$"

        if [[ ! -d "$file" && "$file" =~ $regex ]]; then
            ln -f "$file" "./$name.yml" && echo "Matched $file, creating hardlink $name.yml"

            removeName="$name"
            break
        fi
    done


    # after the loop remove the file name, speeds up
    # the process just a bit faster
    file_names=( "${file_names[@]/$removeName}" )
done