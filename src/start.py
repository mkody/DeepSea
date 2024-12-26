import argparse
import json
import logging
import shutil
from pathlib import Path

from fs import FS
from gh import GH

logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Team Neptune's DeepSea build script.",
    )
    required_named = parser.add_argument_group(
        "Options required to build a release candidate",
    )
    required_named.add_argument(
        "-gt", "--githubToken", help="Github Token", required=True,
    )
    args = parser.parse_args()

    sdcard = FS()
    github = GH(args.githubToken)
    with Path("./settings.json").open("r") as f:
        settings = json.load(f)

    needed_modules = []
    for package in settings["packages"]:
        if package["active"]:
            for module in package["modules"]:
                if module not in needed_modules:
                    needed_modules.append(module)

    for i in needed_modules:
        module = settings["moduleList"][i]
        module_found = github.download_release_assets(module)
        if not module_found:
            logging.error(f"Failed to download: {module['repo']}")

    for package in settings["packages"]:
        if package["active"]:
            logging.info(f"[{package['name']}] Creating package")
            sdcard.create_sd_env()

            for i in package["modules"]:
                module = settings["moduleList"][i]
                logging.info(
                    f"[{package['name']}][{module['repo']}] " +
                    "Creating module env",
                )
                sdcard.create_module_env(module)
                for step in module["steps"]:
                    logging.info(
                        f"[{package['name']}][{module['repo']}] " +
                        f"Executing step: {step['name']}",
                    )
                    sdcard.execute_step(step)

                logging.info(
                    f"[{package['name']}][{module['repo']}] Moving MENV to SD",
                )
                sdcard.finish_module()

            logging.info(f"[{package['name']}] All modules processed.")
            logging.info(f"[{package['name']}] Creating ZIP")
            shutil.make_archive(
                f"deepsea-{package['name']}_v{settings['releaseVersion']}",
                "zip",
                "./sd",
            )
