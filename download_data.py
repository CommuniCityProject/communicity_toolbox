import argparse
import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional

import requests

REPO_RUL = "https://github.com/CommuniCityProject/communicity_toolbox"
FILE_PREFIX = "data."


def download(
    repo_url: str,
    output_path: Path,
    tag_name: Optional[str] = None
) -> List[Path]:
    repo_url = repo_url[:-1] if repo_url.endswith("/") else repo_url
    url_split = repo_url.split("/")
    owner = url_split[-2]
    repo = url_split[-1]
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    if tag_name is not None:
        response = requests.get(url)
        response.raise_for_status()
        try:
            release = [r for r in response.json() if r["tag_name"] == tag_name][0]
        except IndexError:
            print("Tag not found!")
            return []
    else:
        response = requests.get(url + "/latest")
        response.raise_for_status()
        release = response.json()

    file_paths = []
    assets = release["assets"]
    for asset in assets:
        if asset["name"].startswith(FILE_PREFIX):
            download_url = asset["browser_download_url"]
            file_path = output_path / asset["name"]
            with open(file_path, "wb") as file:
                print("Downloading", download_url)
                response = requests.get(download_url)
                response.raise_for_status()
                file.write(response.content)
            file_paths.append(file_path)
    return file_paths


def extract(zip_path: Path, out_path: Path):
    print(f"Extracting {zip_path} to {out_path}")
    zip_file = zipfile.ZipFile(zip_path, 'r')
    zip_file.extractall(out_path)


def main(repo_url: str, output_path: Path, tag_name: Optional[str] = None):
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_paths = download(repo_url, Path(tmp_dir), tag_name)
        for file_path in file_paths:
            extract(file_path, output_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Download and extract the Toolbox data from the Github"
                    "repository."
    )
    ap.add_argument(
        "--repo",
        default=REPO_RUL,
        help=f"URL to the Github repo. Defaults to '{REPO_RUL}'"
    )
    ap.add_argument(
        "-t",
        "--tag",
        help="Github tag name to use to download the data. "
             "Defaults to the latest",
    )
    ap.add_argument(
        "-o",
        "--output",
        default=Path("./"),
        help="Output path. Defaults to './'"
    )
    args = ap.parse_args()
    main(args.repo, args.output, args.tag)
