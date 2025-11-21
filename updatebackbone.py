#!/usr/bin/env python3

import os
import requests
import zipfile
import io
import datetime
from tqdm import tqdm  # progress bar
from utils.printutils import *

GBIF_URL = "https://hosted-datasets.gbif.org/datasets/backbone/current/backbone.zip"
DATA_DIR = os.path.join(os.path.dirname(__file__), "GBIF", "backbone")
META_FILE = os.path.join(DATA_DIR, "last_updated.txt")
MAX_AGE_DAYS = 30

# Check if the downloaded dataset is outdated
def is_outdated() -> bool:
    if not os.path.exists(META_FILE):
        return True
    try:
        with open(META_FILE) as f:
            last = datetime.datetime.fromisoformat(f.read().strip())
        age = (datetime.datetime.now() - last).days
        return age > MAX_AGE_DAYS
    except Exception:
        return True
# Downloads the dataset
def download_backbone() -> None:
    """Download the GBIF Backbone ZIP with progress bar and extract it."""
    os.makedirs(DATA_DIR, exist_ok=True)
    status("Downloading latest GBIF Backbone dataset...")

    with requests.get(GBIF_URL, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        chunk_size = 8192  # 8 KB
        data = io.BytesIO()
        # Just a funky progress bar
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading", ncols=80) as pbar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    data.write(chunk)
                    pbar.update(len(chunk))

    status("Extracting files...")
    data.seek(0)
    with zipfile.ZipFile(data) as zf:
        zf.extractall(DATA_DIR)

    with open(META_FILE, "w") as f:
        f.write(datetime.datetime.now().isoformat())

    success("GBIF Backbone dataset updated successfully.")

# Checks if the data should be updated and if so, updates the data
def main() -> None:
    if is_outdated():
        download_backbone()
    else:
        info("GBIF backbone is up-to-date.")

if __name__ == "__main__":
    main()
