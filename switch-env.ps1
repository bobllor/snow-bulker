<#
    .DESCRIPTION
    Creates a hard link of the YAML files into the current directory from a path.

    The file names are expected to begin with one of the following: config data html.
    It is also case insensitive.
    The script will search for these files and copy it to the required names
    for the program to run.

    The hard links are created with the first matching file in the given path.
    Any subsequent files will be ignored if a match for one has already been found.

    .PARAMETERS
      - Path <string> 
        The path to the directory containing the YAML files.

    .NOTES
    WARNING: This overwrites the files in the root directory. Ensure there
    are backups for these files if they are needed.
#>

param(
    [string] $Path
)

if($Path.trim() -eq ""){
    echo "No path given, path argument is required"
    exit 1
}elseif(!(test-path "$Path")){
    echo "Path does not exist"
    exit 1
}elseif(test-path "$Path" -pathtype leaf){
    echo "Path must be a directory"
    exit 1
}

$fileNames = "config","data","html"

foreach($FileObj in (get-childitem "$Path")){
    $file = $FileObj.fullname
    $fileName = $FileObj.name
    $removeName = ""

    foreach($Name in $fileNames){
        $regex = "($Name).*\.(yml|yaml)$"

        if((test-path "$file" -pathtype leaf) -and "$fileName" -match "$regex"){
            $hardlink = new-item -itemtype hardlink -path "$Name.yml" -value "$file" -force

            if($hardlink){
                echo "Matched $file, creating hardlink $Name.yml"
            }

            $removeName = "$name"
        }
    }

    # after the loop remove the file name, speeds up
    # the process just a bit faster
    $fileNames = $fileNames | where-object { $_ -ne "$removeName"}
}