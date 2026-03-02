#!/usr/bin/env bash

output_folder="output"
folders=("data" "logs" "cache")

root_folders=("$output_folder" "configs")

for file in "${root_folders[@]}"; do
    if [[ ! -d "$file" ]]; then
        echo "Creating '$file' folder"
        mkdir "$file"
    fi
done

for file in "${folders[@]}"; do
    data_folder="$output_folder/$file"

    if [[ ! -d "$data_folder" ]]; then
        echo "Creating '$data_folder' folder"
        mkdir "$data_folder"
    fi
done

env_path=$(printenv PATH | awk '{ print tolower($0) }')
if [[ $env_path =~ "python/python" ]]; then
    if [[ ! -d ".venv" ]]; then
        echo "Creating virual environment"

        py -m venv .venv
        source ./.venv/scripts/activate
        pip install -r requirements.txt
    fi
else
    echo "Python executable not found in PATH"
    exit 1
fi