import os
import shutil
import click
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog
from imagededup.methods import DHash, CNN
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

def find_and_move_duplicates_dhash(input_dir, threshold):
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

def find_and_move_duplicates_cnn(input_dir, threshold):
    cnn = CNN()
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
    encodings = cnn.encode_images(image_dir=input_dir)
    duplicates = cnn.find_duplicates_to_remove(
        encoding_map=encodings, min_similarity_threshold=threshold
    )

    total_duplicates = len(duplicates)
    logger.info(f"Total number of found duplicates: {total_duplicates}")

    # Move duplicates to the duplicates directory
    for file in tqdm(duplicates, desc="Moving duplicates"):
        src_file = os.path.join(input_dir, file)
        dest_file = os.path.join(duplicates_dir, os.path.basename(file))
        if os.path.exists(src_file):
            shutil.move(src_file, dest_file)

    return total_images, total_duplicates

@click.command()
@click.option(
    "--threshold",
    default=10,  # Default threshold for DHash method
    type=float,
    help="Threshold for duplicate detection. For DHash (default: 10, min: 0, max: 64). For CNN (default: 0.99, range: 0.5-0.99)",
)
@click.option(
    "--algo",
    default="dhash",  # Default algorithm is DHash
    type=click.Choice(["dhash", "cnn"], case_sensitive=False),
    help="Algorithm to use for duplicate detection: 'dhash' or 'cnn' (default: dhash)",
)
def main(threshold, algo):
    start_time = time()

    if algo == "cnn":
        if threshold == 10:
            threshold = 0.99  # Default threshold for CNN
        else:
            threshold = max(0.5, min(0.99, threshold))  # Ensure threshold is within valid range
    else:
        threshold = int(threshold)  # Convert to integer for DHash

    input_dir = select_directory()
    if not input_dir:
        logger.info("No directory selected. Exiting.")
        return
    logger.info(f"Selected directory: {input_dir}")
    logger.info(f"Finding duplicates with threshold: {threshold} using {algo.upper()} algorithm")

    if algo == "dhash":
        total_images, total_duplicates = find_and_move_duplicates_dhash(input_dir, threshold)
    else:
        total_images, total_duplicates = find_and_move_duplicates_cnn(input_dir, threshold)

    end_time = time()
    total_time = end_time - start_time

    logger.info(f"Total runtime: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()