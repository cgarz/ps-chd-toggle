#!/usr/bin/env python3

import os
import re
import subprocess
from shutil import which, move
from pathlib import Path
from argparse import ArgumentParser

# Looks for binmerge next to this script. Same with chdman, unless chdman in path, then use that.
BINMERGE_PATH = Path(__file__).resolve().parent / 'binmerge'
CHDMAN_PATH = Path(which('chdman')) if which('chdman') else Path(__file__).resolve().parent / 'chdman'

SEARCH_TYPE_CUEBIN = b'TRACK:1 TYPE:MODE2_RAW '
SEARCH_TYPE_CUEBIN2 = b'TRACK:1 TYPE:MODE1_RAW '  # 2022/11, 3 ps1 games, GameGenius v5, PS Programmer Tool v2.6 & v3.0
SEARCH_TYPE_ISO = b'TRACK:1 TYPE:MODE1 '
FILE_EXTENSIONS = ('.CUE', '.ISO', '.CHD')
CUE_BIN_FILES_REGEX = re.compile(r'^(FILE ")(?P<bin_file>.*\.bin)(" BINARY)$', re.IGNORECASE)


def check_dependency_paths():
    paths = {'binmerge': BINMERGE_PATH,
             'chdman': CHDMAN_PATH}

    for name, path in paths.items():
        if not path.exists():
            print(f'ERROR: {name} not found at specified path. Edit {name.upper()}_PATH at the top of this file.\n'
                  'Example:\n'
                  f'    {name.upper()}_PATH = Path("/home/username/{name}")')
            exit(1)
        if not os.access(path, os.R_OK):
            print(f'ERROR: {name} found but not readable.')
            exit(1)
        if not os.access(path, os.X_OK):
            print(f'ERROR: {name} found but not executable.')
            exit(1)


def get_chd_format(disc_image):
    args = (CHDMAN_PATH, 'dumpmeta', '-i', disc_image, '-t', 'CHT2', '-ix', '0')
    try:
        meta = subprocess.check_output(args)
    except subprocess.CalledProcessError:
        print('Error getting metadata for\n'
              f'    {disc_image}\n')
        return

    if SEARCH_TYPE_CUEBIN in meta or SEARCH_TYPE_CUEBIN2 in meta:
        args = (CHDMAN_PATH, 'dumpmeta', '-i', disc_image, '-t', 'CHT2', '-ix', '1')
        try:
            subprocess.run(args, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError:
            return {'type': 'CUEBIN', 'multi_track': False}
        else:
            return {'type': 'CUEBIN', 'multi_track': True}

    if SEARCH_TYPE_ISO in meta:
        return {'type': 'ISO', 'multi_track': False}

    return


def main():
    parser = ArgumentParser(description='Converts PS1/PS2 images between chd compressed and uncompressed'
                                        ' Redump format using chdman and binmerge.')
    mutx = parser.add_mutually_exclusive_group()
    mutx.add_argument('-c', '--compress-only', action='store_true', help='Skips any found chd disc images.')
    mutx.add_argument('-d', '--decompress-only', action='store_true', help='Skips any found cue/bin or iso disc images.')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Find PS1/PS2 disc images recursively if a folder path is specified.')
    parser.add_argument('paths', nargs='+', type=Path, metavar='path',
                        help='Path(s) to PS1/PS2 cue/bin/iso/chd disc image(s), or a folder with'
                             ' images to compress or decompress (non recursive by default).')
    args = parser.parse_args()
    check_dependency_paths()

    for path in args.paths:
        if not path.exists():
            parser.error(f'The specified file or folder does not exist:\n'
                         f'    "{path}"')

    file_glob = '**/*.*' if args.recursive else '*.*'
    compress_count = decompress_count = 0
    disc_images = []
    for path in args.paths:
        if path.is_file():
            disc_images.append(path)
        elif path.is_dir():
            print('Searching for images in:', path)
            for file in path.glob(file_glob):
                if file.suffix.upper() in FILE_EXTENSIONS:
                    disc_images.append(file)
                    if file.suffix.upper() in ('.CUE', '.ISO') and not args.decompress_only:
                        compress_count += 1
                    if file.suffix.upper() == '.CHD' and not args.compress_only:
                        decompress_count += 1
    disc_images.sort()

    print(f'Found {len(disc_images)} disc images ({compress_count} to compress, {decompress_count} to decompress)')
    for disc_image in disc_images:
        remove_files_success = [disc_image]
        outputs = []
        proc_args = ()

        if disc_image.suffix.upper() == '.ISO' and not args.decompress_only:
            chd_path = disc_image.with_suffix('.chd')
            outputs = [chd_path]
            proc_args = (CHDMAN_PATH, 'createcd', '-i', disc_image, '-o', chd_path)

        elif disc_image.suffix.upper() == '.CUE' and not args.decompress_only:
            chd_path = disc_image.with_suffix('.chd')
            outputs = [chd_path]

            with open(disc_image) as cue_file:
                for line in cue_file:
                    if match := CUE_BIN_FILES_REGEX.search(line):
                        remove_files_success.append(Path(disc_image.parent / match.group('bin_file')))

            proc_args = (CHDMAN_PATH, 'createcd', '-i', disc_image, '-o', chd_path)

        elif disc_image.suffix.upper() == '.CHD' and not args.compress_only:
            format = get_chd_format(disc_image)
            if not format:
                print('Unable to establish CHD format, skipping:\n'
                      f'    "{disc_image}"\n')
                continue

            proc_args = (CHDMAN_PATH, 'extractcd', '-i', disc_image)
            if format['type'] == 'CUEBIN':
                cue_path = disc_image.with_suffix('.cue')
                bin_path = disc_image.with_suffix('.bin')
                outputs = [cue_path, bin_path]
                proc_args += ('-o', cue_path, '-ob', bin_path)
            elif format['type'] == 'ISO':
                temp_path = disc_image.with_suffix('.temp')
                iso_path = disc_image.with_suffix('.iso')
                remove_files_success.append(temp_path)
                outputs = [temp_path, iso_path]
                proc_args += ('-o', temp_path, '-ob', iso_path)

        if not proc_args:
            continue

        try:
            subprocess.run(proc_args, check=True)
        except (subprocess.CalledProcessError, KeyboardInterrupt) as e:
            if type(e) is KeyboardInterrupt:
                print()
            for f in outputs:
                if f.exists():
                    os.remove(f)
                    print(f'Removed unfinished file: "{f}"')
            if type(e) is KeyboardInterrupt:
                raise e
        else:
            for f in remove_files_success:
                if f.exists():
                    os.remove(f)
                    print(f'Removed: "{f}"')

        if disc_image.suffix.upper() == '.CHD' and format['type'] == 'CUEBIN':
            with open(cue_path) as cue_file:
                cue_data = cue_file.read()
                cue_file_newlines = cue_file.newlines
            if cue_file_newlines != '\r\n':
                fixed_cue_path = cue_path.with_suffix('.cue.fixed')
                with open(fixed_cue_path, 'w', newline='\r\n') as fixed_cue_file:
                    fixed_cue_file.write(cue_data)
                fixed_cue_path.replace(cue_path)
                print('Fixed cue file line endings')

        if disc_image.suffix.upper() == '.CHD' and format['type'] == 'CUEBIN' and format['multi_track']:
            print('Restoring multi track format with binmerge')
            merged_cue_path = cue_path.replace(cue_path.with_name(f'{cue_path.stem}_merged{cue_path.suffix}'))
            proc_args = (BINMERGE_PATH, '-s', merged_cue_path, cue_path.stem)

            try:
                subprocess.run(proc_args, check=True)
            except (subprocess.CalledProcessError, KeyboardInterrupt) as e:
                # TODO: cleanup outputs on cancel, test by adding sleep to binmerge or something
                if type(e) is KeyboardInterrupt:
                    raise e
            else:
                for f in (merged_cue_path, bin_path):
                    if f.exists():
                        os.remove(f)
                        print(f'Removed: "{f}"')

        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nGot KbdInterrupt, quitting.')
