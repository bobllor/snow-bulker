from pathlib import Path
import src.support.utils as utils
import random
import os

def test_get_state():
    states: list[str] = ["WI", "TX", "NY", "FL"]
    expected_states: set[str] = {"Wisconsin", "Texas", "New York", "Florida"}

    for state in states:    
        new_state: str = utils.get_us_state(state)

        assert new_state in expected_states

def test_get_path_files(tmp_path: Path):
    files: list[Path] = mk_files(tmp_path)

    assert files[random.randint(0, len(files) - 1)].exists()

    flat_files: list[Path] = utils.get_path_files(files[0].parent)

    assert len(flat_files) == len(files)

def test_find_file(tmp_path: Path):
    # handles nested and normal files
    files: list[Path] = mk_files(tmp_path)
    rand_file: Path = files[random.randint(0, len(files) - 1)]

    file_divider: str = "\\" if os.name == "nt" else "/"
    split_file: list[str] = str(rand_file).split(file_divider)

    file: str = split_file[len(split_file) - 2] + "/" + split_file[-1]
    found_file: Path = utils.get_file(tmp_path, file)

    assert found_file == rand_file

def test_ext_find_file(tmp_path: Path):
    yaml: Path = tmp_path / "config.yaml"
    yaml.touch()

    exts: list[str] = ["yaml", "..yml"]
    
    # yaml ext with no period
    found_file: Path | None = utils.get_file(tmp_path, "config", exts=exts)
    assert found_file is not None and found_file.suffix == ".yaml"

    yaml.unlink()

    yaml = tmp_path / "config.yml"
    yaml.touch()

    # yml with two leading periods
    found_file = utils.get_file(tmp_path, "config", exts=exts)
    assert found_file is not None and found_file.suffix == ".yml"

    # replacement of ext with given exts
    found_file = utils.get_file(tmp_path, "config.somenonsenseextensionhere", exts=exts)
    assert found_file is not None and found_file.suffix == ".yml"

    # failure due to no existing file
    found_file = utils.get_file(tmp_path, "config.yaml")
    assert found_file is None
    # failure due to no exts or given suffix
    found_file = utils.get_file(tmp_path, "config")
    assert found_file is None

def test_no_recurse_find_file(tmp_path: Path):
    file: str = "item.txt"
    path: Path = tmp_path / "folder1" / file

    path.parent.mkdir(exist_ok=True, parents=True)
    path.touch()
    (tmp_path / "sample").touch()

    file_path: Path | None = utils.get_file(tmp_path, file, skip_dir=True)

    assert file_path is None

def mk_files(tmp_path: Path) -> list[Path]:
    '''Creates folders in a given path. The list of Paths used to create the files
    is returned.
    '''
    test_folder: Path = tmp_path / "a folder"
    test_folder.mkdir(parents=True, exist_ok=True)

    test_folder_two: Path = test_folder / "another folder"
    test_folder_two.mkdir(parents=True, exist_ok=True)

    files: list[Path] = [
        test_folder / "file1.txt",
        test_folder / "file2.txt",
        test_folder / "lol.txt",
        test_folder_two / "file1.txt",
        test_folder_two / "file2.txt",
        test_folder_two / "lol.txt",
    ]

    for file in files:
        file.touch(exist_ok=True)
    
    return files