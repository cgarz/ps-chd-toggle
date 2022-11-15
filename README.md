# ps-chd-toggle

A convenience wrapper script to make it easier to switch PS1 and PS2 images between uncompressed redump format and CHD (compressed hunks of data) format.

chdman has various quirks which can make converting large collections tedious, ps-chd-toggle handles these automatically:
  - A cue file output is expected to be passed even for iso.<br />
       - A temp cue file is written and automatically removed after decompression if the format is iso.
  - It writes unix LF line endings for the cue file, redump uses windows CRLF.<br />
       - If the cue file has LF line endings it will automatically be rewritten with CRLF.

The action to take is based on the input file extension:
  - cue/bin and iso will be compressed to chd.
  - chd will be decompressed to the appropriate format based on output from `chdman dumpmeta`.

### Requirements:
- Python 3.8+
    - Install from your package manager or visit https://www.python.org/
- binmerge
    - Can be found here: (https://github.com/putnam/binmerge). Place the binmerge python file next to ps-chd-toggle.py.
- chdman
    - Part of MAME (https://www.mamedev.org). Some Linux distros also have a package for it. For example Arch has mame-tools. Install it and make sure its in the system path or place it next to ps-chd-toogle.py.

### Usage:
```
ps-chd-toggle.py [-h] [-c | -d] [-r] path [path ...]

positional arguments:
  path                   Path(s) to PS1/PS2 cue/bin/iso/chd disc image(s), or a folder with images to
                         compress or decompress (non recursive by default).
options:
  -h, --help             Show this help message and exit
  -c, --compress-only    Skips any found chd disc images.
  -d, --decompress-only  Skips any found cue/bin or iso disc images.
  -r, --recursive        Find PS1/PS2 disc images recursively if a folder path is specified.
```

### Example usage and output:
```
$ ps-chd-toggle.py -r "/data/Sony - PlayStation"

Searching for images in: /data/Sony - PlayStation
Found 1 disc images (1 to compress, 0 to decompress)
chdman - MAME Compressed Hunks of Data (CHD) manager 0.249 (unknown)
Output CHD:   /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).chd
Input file:   /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).cue
Input tracks: 4
Input length: 44:59:24
Compression:  cdlz (CD LZMA), cdzl (CD Deflate), cdfl (CD FLAC)
Logical size: 495,612,288
Compression complete ... final ratio = 52.3%
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).cue"
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3) (Track 1).bin"
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3) (Track 2).bin"
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3) (Track 3).bin"
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3) (Track 4).bin"


$ ps-chd-toggle.py -r "/data/Sony - PlayStation"

Searching for images in: /data/Sony - PlayStation
Found 1 disc images (0 to compress, 1 to decompress)
chdman - MAME Compressed Hunks of Data (CHD) manager 0.249 (unknown)
Output TOC:   /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).cue
Output Data:  /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).bin
Input CHD:    /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).chd
Extraction complete
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).chd"
Fixed cue file line endings
Restoring multi track format with binmerge
[INFO]  Output directory: /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)
[INFO]  Opening cue: /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)_merged.cue
[INFO]  Splitting files...
[INFO]  Wrote 4 bin files
[INFO]  Wrote new cue: /data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).cue
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)_merged.cue"
Removed: "/data/Sony - PlayStation/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3)/Colin McRae Rally (Europe) (En,Fr,De,Es) (Rev 3).bin"
```


Tested on Linux only. For windows you may have to edit the paths to binmerge and chdman at the top of the script.
