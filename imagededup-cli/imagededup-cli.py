import os
import shutil
import click
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from imagededup.methods import DHash
from loguru import logger
from time import time
import sys
from datetime import datetime

# Configure loguru
current_time = datetime.now().strftime("%Y-%m-%d")
logger.add(
    f"{current_time}.log",
    rotation="100 MB",
    colorize=True,
    format="<green>{time}</green> <level>{message}</level>",
)
logger.add(
    sys.stderr, format="<green>{time}</green> <level>{message}</level>", colorize=True
)


def select_directory():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory()
    return folder_selected


def find_and_move_duplicates(input_dir, threshold):
    dhash = DHash()
    duplicates_dir = os.path.join(input_dir, "duplicates")
    if not os.path.exists(duplicates_dir):
        os.makedirs(duplicates_dir)

    # Find all JPG files recursively
    jpg_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(".jpg"):
                jpg_files.append(os.path.join(root, file))

    total_images = len(jpg_files)
    logger.info(f"Total number of input images: {total_images}")

    # Create encodings and find duplicates
    encodings = dhash.encode_images(image_dir=input_dir)
    duplicates = dhash.find_duplicates(
        encoding_map=encodings, max_distance_threshold=threshold
    )

    # Flatten the list of duplicates
    duplicates_to_remove = {item for sublist in duplicates.values() for item in sublist}

    total_duplicates = len(duplicates_to_remove)
    logger.info(f"Total number of found duplicates: {total_duplicates}")

    # Move duplicates to the duplicates directory
    for file in tqdm(duplicates_to_remove, desc="Moving duplicates"):
        src_file = os.path.join(input_dir, file)
        dest_file = os.path.join(duplicates_dir, os.path.basename(file))
        if os.path.exists(src_file):
            shutil.move(src_file, dest_file)

    return total_images, total_duplicates


@click.command()
@click.option(
    "--threshold",
    default=10,  # Adjusted threshold for DHash method (default: 10)
    help="Threshold for duplicate detection (default: 10, min: 0, max: 64, lower is more strict)",
)
def main(threshold):
    start_time = time()

    input_dir = select_directory()
    if not input_dir:
        click.echo("No directory selected. Exiting.")
        logger.info("No directory selected. Exiting.")
        return

    click.echo(f"Selected directory: {input_dir}")
    click.echo(f"Finding duplicates with threshold: {threshold}")
    logger.info(f"Selected directory: {input_dir}")
    logger.info(f"Finding duplicates with threshold: {threshold}")

    total_images, total_duplicates = find_and_move_duplicates(input_dir, threshold)

    end_time = time()
    total_time = end_time - start_time

    time_per_1000_images = (total_time / total_images) * 1000 if total_images else 0
    time_per_1000_duplicates = (
        (total_time / total_duplicates) * 1000 if total_duplicates else 0
    )

    logger.info(f"Total runtime: {total_time:.2f} seconds")
    logger.info(f"Seconds per 1000 input files: {time_per_1000_images:.2f}")
    logger.info(f"Seconds per 1000 duplicates: {time_per_1000_duplicates:.2f}")

    click.echo("Duplicate finding and moving completed.")
    logger.info("Duplicate finding and moving completed.")


if __name__ == "__main__":
    main()
