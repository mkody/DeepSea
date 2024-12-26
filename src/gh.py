import logging
import pathlib
import re
import urllib.request

from github import Github


class GH:
    def __init__(self, gh_token):
        self.token = gh_token
        self.github = Github(self.token)

    def download_release_assets(self, module):
        found_module = False

        try:
            gh_repo = self.github.get_repo(module["repo"])
        except:  # noqa: E722
            logging.exception(f"Unable to get: {module['repo']}")
            return None

        releases = gh_repo.get_releases()
        if releases.totalCount == 0:
            logging.warning(f"No available release for: {module['repo']}")
            return None
        gh_latest_release = releases[0]

        for pattern in module["regex"]:
            for asset in gh_latest_release.get_assets():
                if re.search(pattern, asset.name):
                    logging.info(
                        f"[{module['repo']}] Downloading: {asset.name}",
                    )
                    fpath = f"./base/{module['repo']}/"
                    pathlib.Path(fpath).mkdir(parents=True, exist_ok=True)
                    urllib.request.urlretrieve(
                        asset.browser_download_url, f"{fpath}{asset.name}",
                    )
                    found_module = True

        return found_module
