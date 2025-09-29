import re
import shutil
import zipfile
from pathlib import Path


class FS:
    def __init__(self):
        shutil.rmtree("./base", ignore_errors=True)
        shutil.rmtree("./menv", ignore_errors=True)
        shutil.rmtree("./sd", ignore_errors=True)
        for elements in Path().glob("*.zip"):
            elements.unlink()

    def create_sd_env(self):
        shutil.rmtree("./sd", ignore_errors=True)
        Path("./sd").mkdir(parents=True, exist_ok=True)

    def create_module_env(self, module):
        shutil.rmtree("./menv", ignore_errors=True)
        Path("./menv").mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            f"./base/{module['repo']}",
            "./menv/",
            dirs_exist_ok=True,
        )

    def execute_step(self, step):
        if step["name"] == "extract":
            self.__extract(step["arguments"][0])

        if step["name"] == "create_dir":
            self.__create_dir(step["arguments"][0])

        if step["name"] == "create_file":
            self.__create_file(step["arguments"][0], step["arguments"][1])

        if step["name"] == "replace_content":
            self.__replace_file_content(
                step["arguments"][0],
                step["arguments"][1],
                step["arguments"][2],
            )

        if step["name"] == "delete":
            self.__delete(step["arguments"][0])

        if step["name"] == "copy":
            self.__copy(step["arguments"][0], step["arguments"][1])

        if step["name"] == "move":
            self.__copy(step["arguments"][0], step["arguments"][1])
            self.__delete(step["arguments"][0])

    def finish_module(self):
        self.__copy_to_sd()
        shutil.rmtree("./menv", ignore_errors=True)

    def __extract(self, source):
        path = "./menv/"
        for filename in Path(path).iterdir():
            if re.search(source, filename.name):
                asset_path = f"./menv/{filename.name}"
                with zipfile.ZipFile(asset_path, "r") as zip_ref:
                    zip_ref.extractall(path)
                self.__delete(filename.name)

    def __delete(self, source):
        source_path = Path(f"./menv/{source}")
        if not source_path.is_dir() and source_path.exists():
            source_path.unlink()
        else:
            shutil.rmtree(f"./menv/{source}", ignore_errors=True)

    def __copy(self, source, dest):
        for elements in Path("./menv").glob(source):
            if not elements.is_dir():
                if elements.exists():
                    shutil.copy(f"{elements}", f"./menv/{dest}")
                    break
            else:
                shutil.copytree(
                    f"{elements}",
                    f"./menv/{dest}",
                    dirs_exist_ok=True,
                )
                break

    def __create_dir(self, source):
        Path(f"./menv/{source}").mkdir(parents=True, exist_ok=True)

    def __create_file(self, source, content):
        with Path(f"./menv/{source}").open("w") as f:
            f.write(content)

    def __replace_file_content(self, source, search, replace):
        with Path(f"./menv/{source}").open("rt") as fin:
            data = fin.read()
            data = data.replace(search, replace)
        with Path(f"./menv/{source}").open("wt") as fin:
            fin.write(data)

    def __copy_to_sd(self):
        shutil.copytree("./menv", "./sd/", dirs_exist_ok=True)
