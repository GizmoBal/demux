# demux

## Description

High quality remuxes come with a large number of tracks (sometimes more than 100) and tags. If you want to encode, then demuxing properly can be quite a time-consuming task. This script aims at making it a breeze. It will extract all the files with appropriate names, create the corresponding tag files and even store in a separate file, the `mkvmerge` command (including all the titles and delays) to mux it back.

## Requirements

`mkvtoolnix`, `mediainfo`, `ffmpeg`, `dovi_tool` and `hdr10plus_tool` must be on path.


## Usage

```
python3 path/to/demux.py -r Madagascar.2005.test.2160p.UHD.Blu-ray.Remux.DV.HDR.HEVC.TrueHD.Atmos.7.1-CiNEPHiLES.mkv
```
will extract all the files necessary to mux it back and store the corresponding `mkvmerge` command in a `remux.py` file.

```
python3 path/to/demux.py Madagascar.2005.test.2160p.UHD.Blu-ray.Remux.DV.HDR.HEVC.TrueHD.Atmos.7.1-CiNEPHiLES.mkv
```
is intended for the encoder. It will not extract the video file, but instead the DoVi and HDR10+ metadata and process them for encoding.


