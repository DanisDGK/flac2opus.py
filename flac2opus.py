#!/usr/bin/env python3
import os
import argparse
import concurrent.futures
import subprocess
import multiprocessing
from tqdm import tqdm

class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'

def transcode_flac_to_opus(input_file, output_file, bitrate):
    command = ['opusenc', '--quiet', '--music', '--bitrate', f'{bitrate}', input_file, output_file]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def transcode_and_remove(args):
    flac_file, bitrate, progress_bar = args
    flac_path = flac_file
    output_path = os.path.splitext(flac_path)[0] + '.opus'
    transcode_flac_to_opus(flac_path, output_path, bitrate)
    os.remove(flac_path)
    progress_bar.update(1)

def process_directory(input_directory, bitrate, max_threads):
    flac_files = [os.path.join(root, f) for root, _, files in os.walk(input_directory) for f in files if f.lower().endswith('.flac')]
    
    if not flac_files:
        print(f"{Colors.RED}No FLAC files found in the specified directory.{Colors.RESET}")
        return

    total_files = len(flac_files)
    format_str = f"{Colors.GREEN}{'{desc}: {percentage:.0f}% {bar} {n}/{total}'}{Colors.RESET}"
    max_workers = min(total_files, max_threads)

    with tqdm(total=total_files, unit='file', unit_scale=True, desc=f'{Colors.YELLOW}Transcoding using {max_workers} threads{Colors.RESET}', bar_format=format_str) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            args_generator = ((flac_file, bitrate, progress_bar) for flac_file in flac_files)
            executor.map(transcode_and_remove, args_generator)

    print(f"{Colors.GREEN}Transcoding completed.{Colors.RESET}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transcode FLAC files to Opus format.')
    parser.add_argument('input_directory', help='Path to the input directory containing FLAC files.')
    parser.add_argument('--bitrate', type=int, default=192, help='Bitrate for Opus encoding in kbps (default: 192)')
    parser.add_argument('--threads', type=int, default=multiprocessing.cpu_count(), help='Number of threads for parallel transcoding (default: number of available CPU cores)')
    args = parser.parse_args()

    input_directory = args.input_directory
    bitrate = args.bitrate
    max_threads = args.threads
    
    process_directory(input_directory, bitrate, max_threads)