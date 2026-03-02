$outputFolder = "output"
$folders = "data","logs","cache"

$rootFolders = "$outputFolder","configs"

foreach($file in $rootFolders){
    if(!(test-path $file)){
        echo "Creating '$file' folder"
        mkdir "$file" | out-null
    }
}

foreach($file in $folders){
    $path = "./$outputFolder/$file"

    if(!(test-path $path)){
        echo "Creating '$file' folder"
        mkdir "$path" | out-null
    }
}

if(!(test-path ".venv")){
    $foundPython = $false
    foreach($path in ($env:path).split(";")){
        if("$path" -match "python\\python"){
            $foundPython = $true
            break
        }
    }

    if($foundPython){
        if(!(test-path ".venv")){
            echo "Creating virual environment"

            python3 -m venv .venv
            & .\.venv\activate.ps1
            pip install -r requirements.txt
        }
    }else{
        write-error "Python executable not found in PATH"
    }
}