# HDRplot

## Description

High quality remuxes such as CiNEPHiLES or ZQ remuxes come with a large number of tracks (sometimes more than 100) and tags. If you want to encode, demuxing properly can be quite a time-consuming task. This script aims at making it a breeze. It will extract all the files with appropriate names, create the corresponding tag files and even store the mkvmerge command to mux it back in a separate file.

## Requirements

`mkvtoolnix`, `mediainfo`, `ffmpeg`, `dovi_tool` and `hdr10plus_tool` must be on path.


## Usage

```
demux -r Madagascar.2005.test.2160p.UHD.Blu-ray.Remux.DV.HDR.HEVC.TrueHD.Atmos.7.1-CiNEPHiLES.mkv
```
will extract all the files necessary to mux it back and store the corresponding `mkvmerge` command in a `remux.py` file.

```
demux Madagascar.2005.test.2160p.UHD.Blu-ray.Remux.DV.HDR.HEVC.TrueHD.Atmos.7.1-CiNEPHiLES.mkv
```
is intended for the encoder. It will not extract the video file, but instead the DoVi and HDR10+ metadata and process them for encoding.


