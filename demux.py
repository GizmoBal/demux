#!/usr/bin/env python3

import os
import subprocess
import sys
import re
import argparse
from pathlib import Path
from pymediainfo import MediaInfo
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

WEB_TAGS = {'itunes': 'itunes', \
            'netflix': 'nf', \
            'amazon': 'amzn', \
            'disney': 'dsnp', \
            'max': 'hmax', \
            'anywhere': 'ma', \
            'skyshowtime': 'skst', \
            'filmin': 'flmn', \
            'mubi': 'mubi', \
            'criterion': 'cc', \
            'peacock': 'pcock', \
            'cineasterna': 'cnast', \
            'starzplay': 'stzp', \
            'crunchyroll': 'croll' \
            }

WEB_NAMES = {'itunes': 'iTunes WEB-DL', \
             'nf': 'Netflix WEB-DL', \
             'amzn': 'Amazon Prime WEB-DL', \
             'dsnp': 'Disney+ WEB-DL', \
             'hmax': 'HBO Max WEB-DL', \
             'ma': 'Movies Anywhere WEB-DL', \
             'skst': 'SkyShowtime WEB-DL', \
             'flmn': 'Filmin WEB-DL', \
             'mubi': 'MUBI WEB-DL', \
             'cc': 'Criterion Channel WEB-DL', \
             'pcock': 'Peacock WEB-DL', \
             'cnast': 'Cineasterna WEB-DL', \
             'stzp': 'StarzPlay WEB-DL', \
             'croll': 'Crunchyroll WEB-DL' \
             }

AUDIO_CODECS = {'A_TRUEHD': 'thd', 'A_DTS': 'dtsma', 'A_FLAC': 'flac', 'A_AC3': 'ac3'}

SUB_CODECS = {'S_HDMV/PGS': 'sup', \
              'S_TEXT/UTF8': 'srt' \
              }

def findDuplicate(dictionary):
    """Look for duplicates in the values of dictionary.
    In case, of duplicates, the values are numbered 
    and an updated dictionary is returned."""
    occurDict = {}
    for tags in dictionary.values():
        occurDict.update({tags: 0})
        for src in dictionary.keys():
            if dictionary[src] == tags:
                occurDict[tags] += 1
    for tags in occurDict.keys():
        if occurDict[tags] > 1:
            count = 1
            for src in dictionary.keys():
                if dictionary[src] == tags:
                    dictionary[src] = dictionary[src] + str(count)
                    count += 1
    return dictionary

colorama_init()
templateDir = os.path.dirname(__file__)
localDir = os.path.dirname(os.path.dirname(templateDir))
localDir = os.path.join(localDir, 'Template')
templateDir = os.path.join(templateDir, 'Template')
if os.path.isdir(localDir):
    local = True
else:
    local = False

parser = argparse.ArgumentParser( \
    description='This script demuxes a remux.)')

parser.add_argument('mkv', type=str, help='absolute or relative path to mkv video file')
parser.add_argument('-r', '--remux', action='store_true', help='demux in view of remuxing')

args = parser.parse_args()

mkvFile = os.path.abspath(args.mkv)
if not os.path.exists(mkvFile):
        sys.exit(Fore.RED + "File not found." + Style.RESET_ALL)

media_info = MediaInfo.parse(mkvFile)

summaryTags = f"{Style.BRIGHT}{Fore.BLUE}Tags{Style.RESET_ALL}\n"

cmd = 'mkvextract ' + mkvFile + ' chapters chapters.xml'
subprocess.run(cmd, shell=True)
summaryTags += f"File {Fore.BLUE}chapters.xml{Style.RESET_ALL} created.\n"

if media_info.general_tracks[0].imdb is not None and media_info.general_tracks[0].tmdb is not None:
    imdbTagFile = os.path.join(templateDir, 'imdb.tag.xml')
    tag = open(imdbTagFile, 'r')
    tagText = tag.read()
    tag.close()

    oldIMDB = re.search(r"<String>tt[\d]+</String>",tagText).group()
    oldTMDB = re.search(r"<String>movie/[\d]+</String>",tagText).group()
    newIMDB = "<String>" + media_info.general_tracks[0].imdb + "</String>"
    newTMDB = "<String>" + media_info.general_tracks[0].tmdb + "</String>"

    imdbTagFile = Path('imdb.tag.xml')
    imdbTagFile.write_text(tagText.replace(oldIMDB,newIMDB).replace(oldTMDB,newTMDB))
    summaryTags += f"File {Fore.BLUE}imdb.tag.xml{Style.RESET_ALL} created.\n"
else:
    summaryTags += f"Could not update file {Fore.RED}imdb.tag.xml{Style.RESET_ALL}.\n"

discTags = {}
for track in media_info.tracks:
    source = track.source
    if source is not None and "web" not in source.lower() and source not in discTags:
        if "uhd" in source.lower():
            newItem = {source: 'uhd'}
            discTags.update(newItem)
        elif "dvd" in source.lower():
            newItem = {source: 'dvd'}
            discTags.update(newItem)
        elif "laserdisc" in source.lower():
            newItem = {source: 'ld'}
            discTags.update(newItem)
        elif "ray" in source.lower():
            code = re.search(r" [A-Z][A-Z][A-Z] ",source).group().strip().lower()
            newItem = {source: code}
            discTags.update(newItem)
        else:
            summaryTags += f"A source was {Fore.RED}not{Style.RESET_ALL} identified.\n"

discTags = findDuplicate(discTags)
sourceTags = {**discTags, **WEB_TAGS}

totoTagFile = os.path.join(templateDir, 'toto.disc.tag.xml')
tag = open(totoTagFile, 'r')
tagText = tag.read()
tag.close()
for src in discTags.keys():
    fileName = discTags[src] + '.disc.tag.xml'
    tagFile = Path(fileName)
    tagFile.write_text(tagText.replace('Plaion Pictures ITA Blu-ray (2023)',src))
    summaryTags += f"File {Fore.BLUE}{fileName}{Style.RESET_ALL} created.\n"

summary = '\n'

videoCodec = media_info.video_tracks[0].format
if videoCodec == "HEVC":
    encoder = "x265"
elif videoCodec == "AVC":
    encoder = "x264"
else:
    print(f"{Fore.RED}Unknown video format.{Style.RESET_ALL}")
    sys.exit()
hdrFormat = media_info.video_tracks[0].hdr_format
if hdrFormat is None:
    video = "SDR"
elif "Dolby Vision" not in hdrFormat:
    if "SMPTE ST 2086" in hdrFormat:
        video = "HDR10"
    else:
        video = "HDR10+"
else:
    if "SMPTE ST 2086" in hdrFormat:
        video = "Dolby Vision and HDR10"
    else:
        video = "Dolby Vision and HDR10+"

summary += f"{Style.BRIGHT}{Fore.BLUE}Video{Style.RESET_ALL}: {video}\n"
if not args.remux:
    if "Dolby Vision" in video:
        cmd = 'ffmpeg -i ' + mkvFile + ' -c:v copy -bsf:v hevc_mp4toannexb -f hevc - | dovi_tool extract-rpu -o RPU-orig.bin -'
        subprocess.run(cmd, shell=True)
    if "HDR10+" in video:
        cmd = 'ffmpeg -i ' + mkvFile + ' -c:v copy -bsf:v hevc_mp4toannexb -f hevc - | hdr10plus_tool extract -o HDR10plus-orig.json -'
        subprocess.run(cmd, shell=True)
    if "Dolby Vision" in video:
        summary += f"File {Fore.BLUE}RPU-orig.bin{Style.RESET_ALL} created.\n"
    if "HDR10+" in video:
        summary += f"File {Fore.BLUE}HDR10plus-orig.json{Style.RESET_ALL} created.\n"
    if "Dolby Vision" in video:
        result = subprocess.run('dovi_tool info -s RPU-orig.bin', stdout=subprocess.PIPE, shell=True)
        doviSummary = [x.strip() for x in result.stdout.decode().split('\n')]
        profile = None
        version = None
        for line in doviSummary:
            if 'Profile' in line:
                profile = line
            if 'DM version' in line:
                version = line
        if profile is not None and version is not None:
            profile = re.sub(":", "", profile)
            version = re.sub(r'.*\(', '', version)
            version = re.sub(r'\)', '', version)
            subTitleDV1 = 'Dolby Vision ' + profile + ', ' + version
            summary += f"{subTitleDV1}\n"
            if re.search(r"\(FEL\)", subTitleDV1) is None:
                FEL = False
            else:
                FEL= True
            if FEL:
                cmd = 'ffmpeg -i ' + mkvFile + ' -c:v copy -bsf:v hevc_mp4toannexb -f hevc - | dovi_tool demux --el-only -'
                subprocess.run(cmd, shell=True)
                subprocess.run('mkvmerge -v -o EL.mkv EL.hevc', shell=True)
                subprocess.run('dovi_tool -c -m 2 extract-rpu -o RPU.bin EL.hevc', shell=True)
                summary += f"File {Fore.BLUE}EL.mkv{Style.RESET_ALL} created.\n"
            else:
                cmd = 'ffmpeg -i ' + mkvFile + ' -c:v copy -bsf:v hevc_mp4toannexb -f hevc - | dovi_tool -c -m 2 extract-rpu -o RPU.bin -'
                subprocess.run(cmd, shell=True)
            summary += f"File {Fore.BLUE}RPU.bin{Style.RESET_ALL} created.\n"
else:
    videoSource = 'Unknown'
    for src in sourceTags.keys():
        if src == media_info.video_tracks[0].source or src in media_info.video_tracks[0].source.lower():
            videoSource = sourceTags[src]
            break
    videoFilename = videoSource + '.video.' + videoCodec.lower()
    cmd = 'mkvextract ' + mkvFile + ' tracks'
    cmd += ' ' + str(int(media_info.video_tracks[0].track_id)-1) + ':' + videoFilename
    subprocess.run(cmd, shell=True)
    summary += f"File {Fore.BLUE}{videoFilename}{Style.RESET_ALL} created.\n"
    if videoCodec == "HEVC" and local:
        destFile = 'RPU.edits.json'
        sourceFile = os.path.join(localDir, destFile)
        with open(sourceFile, 'rb') as f, open(destFile, 'wb') as g:
            while True:
                block = f.read(16*1024*1024)  # work by blocks of 16 MB
                if not block:  # end of file
                    break
                g.write(block)
        summary += f"File {Fore.BLUE}{destFile}{Style.RESET_ALL} created.\n"
        destFile = 'HDR10+.edits.json'
        SourceFile = os.path.join(localDir, destFile)
        with open(sourceFile, 'rb') as f, open(destFile, 'wb') as g:
            while True:
                block = f.read(16*1024*1024)  # work by blocks of 16 MB
                if not block:  # end of file
                    break
                g.write(block)
        summary += f"File {Fore.BLUE}{destFile}{Style.RESET_ALL} created.\n"

summary += '\n'

audioCodec = {}
audioType = {}
audioSource = {}
audioDelay = {}
audioFilename = {}
for track in media_info.tracks:
    if track.track_type == "Audio":
        if track.delay_relative_to_video is not None:
            audioDelay.update({track.track_id: track.delay_relative_to_video})
        audioCodec.update({track.track_id: AUDIO_CODECS[track.codec_id]})
        for src in sourceTags.keys():
            if src == track.source or src in track.source.lower():
                audioSource.update({track.track_id: sourceTags[src]})
                break
        if audioSource[track.track_id] is None:
            audioSource[track.track_id] = 'Unknown'
        if "commentary" in track.title.lower():
            audioType.update({track.track_id: 'commentary'})
        elif "compatibility" in track.title.lower():
            audioType.update({track.track_id: 'compatibility'})
        elif "score" in track.title.lower():
            audioType.update({track.track_id: 'score'})
        elif "dub" in track.title.lower():
            audioType.update({track.track_id: 'dub'})
        else:
            audioType.update({track.track_id: 'main'})

audioType = findDuplicate(audioType)
for ind in audioSource.keys():
    audioFilename.update({ind: audioSource[ind] + '.' + audioType[ind] + '.' + audioCodec[ind]})


summary += f"{Style.BRIGHT}{Fore.BLUE}Audio{Style.RESET_ALL}: {Fore.BLUE}{len(audioCodec)}{Style.RESET_ALL} tracks in remux.\n"
cmd = 'mkvextract ' + mkvFile + ' tracks'
for ind in audioFilename.keys():
    cmd += ' ' + str(int(ind)-1) + ':' + audioFilename[ind]
for ind in audioFilename.keys():
    summary += f"File {Fore.BLUE}{audioFilename[ind]}{Style.RESET_ALL} created.\n"

summary += '\n'

subCodec = {}
subType = {}
subSource = {}
subLang = {}
subFilename = {}
for track in media_info.tracks:
    if track.track_type == "Text":
        subCodec.update({track.track_id: SUB_CODECS[track.codec_id]})
        for src in sourceTags.keys():
            if src == track.source or src in track.source.lower():
                subSource.update({track.track_id: sourceTags[src]})
                break
        if subSource[track.track_id] is None:
                subSource[track.track_id] = 'Unknown'
        if track.title is not None:
            if "forced" in track.title.lower():
                subType.update({track.track_id: 'forced'})
            elif "sdh" in track.title.lower():
                subType.update({track.track_id: 'sdh'})
            elif "trivia" in track.title.lower():
                subType.update({track.track_id: 'trivia'})
            elif "commentary" in track.title.lower():
                subType.update({track.track_id: 'commentary'})
            elif "alternate" in track.title.lower():
                subType.update({track.track_id: 'alternate'})
            else:
                subType.update({track.track_id: None})
        else:
            subType.update({track.track_id: None})
        if track.other_language[0] == 'Cantonese (Hant)':
            language = 'yue-Hant'
        elif track.other_language[0] == 'Cantonese (Hans)':
            language = 'yue-Hans'
        elif track.other_language[0] == 'Mandarin (Hant)':
            language = 'cmn-Hant'
        elif track.other_language[0] == 'Mandarin (Hans)':
            language = 'cmn-Hans'
        elif track.other_language[0] == 'Filipino':
            language = 'fil'
        elif len(track.other_language[4]) > 3:
            language = track.other_language[4]
            if language == 'zh-Hant':
                language = 'cmn-Hant'
            if language == 'zh-Hans':
                language = 'cmn-Hans'
        else:
            language = track.other_language[3]
            if language == 'ces':
                language = 'cze'
            if language == 'deu':
                language = 'ger'
            if language == 'ron':
                language = 'rum'
            if language == 'scc':
                language = 'srp'
            if language == 'slk':
                language = 'slo'
        subLang.update({track.track_id: language})

for ind in subCodec.keys():
    if subType[ind] is not None:
        filename = subSource[ind] + '.' + subType[ind] + '.' + subLang[ind] + '.' + subCodec[ind]
    else:
        filename = subSource[ind] + '.' + subLang[ind] + '.' + subCodec[ind]
    subFilename.update({ind: filename})

totoTagFile = os.path.join(templateDir, 'toto.tag.xml')
tag = open(totoTagFile, 'r')
tagText = tag.read()
tag.close()
for web in WEB_TAGS.values():
    if web in subSource.values():
        fileName = web + '.tag.xml'
        tagFile = Path(fileName)
        tagFile.write_text(tagText.replace('iTunes WEB-DL',WEB_NAMES[web]))
        summaryTags += f"File {Fore.BLUE}{fileName}{Style.RESET_ALL} created.\n"

occurDict = {}
for name in subFilename.values():
    occurDict.update({name: 0})
    for ind in subFilename.keys():
        if subFilename[ind] == name:
            occurDict[name] += 1
for name in occurDict.keys():
    if occurDict[name] > 1:
        count = 1
        for ind in subFilename.keys():
            if subFilename[ind] == name:
                if subType[ind] is not None:
                    subType[ind] = subType[ind] + str(count)
                else:
                    subType[ind] = str(count)
                count += 1

for ind in subCodec.keys():
    if subType[ind] is not None:
        filename = subSource[ind] + '.' + subType[ind] + '.' + subLang[ind] + '.' + subCodec[ind]
    else:
        filename = subSource[ind] + '.' + subLang[ind] + '.' + subCodec[ind]
    subFilename.update({ind: filename})

summary += f"{Style.BRIGHT}{Fore.BLUE}Subtitles{Style.RESET_ALL}: {Fore.BLUE}{len(subCodec)}{Style.RESET_ALL} tracks in remux.\n"
for ind in subFilename.keys():
    cmd += ' ' + str(int(ind)-1) + ':' + subFilename[ind]
subprocess.run(cmd, shell=True)
for ind in subFilename.keys():
    summary += f"File {Fore.BLUE}{subFilename[ind]}{Style.RESET_ALL} created.\n"

summary += '\n'
totalTrack = 0

for track in media_info.tracks:
    if track.track_id is not None:
        totalTrack += 1

fileName = media_info.general_tracks[0].file_name_extension
fileName = re.sub('"', '\\\\\"', fileName)
fileName = re.sub("''", '\'\"\'\"\'', fileName)
if media_info.general_tracks[0].movie_name is not None:
    movieName = re.sub('"', '\\\\\"', media_info.general_tracks[0].movie_name)
    movieName = re.sub("''", '\'\"\'\"\'', movieName)
else:
    movieName = ''
if media_info.video_tracks[0].title is not None:
    videoTitle = ' --track-name 0:"' + media_info.video_tracks[0].title + '"'
else:
    videoTitle = ''
if sourceTags[media_info.tracks[1].source] is not None:
    videoTag = ' --tags 0:' + sourceTags[media_info.tracks[1].source] + '.disc.tag.xml'
else:
    videoTag = ''


if not args.remux:
    fileName = re.sub(r".Remux.*VC", "", fileName)
    if local:
        fileName = re.sub(r"-[^-]*\.mkv", "-SoLaR.mkv", fileName)
        fileName = re.sub("-SoLaR", encoder + "-SoLaR", fileName)
    else:
        fileName = re.sub(r"-[^-]*\.mkv", "-TAG.mkv", fileName)
        fileName = re.sub("-TAG", encoder + "-TAG", fileName)

    encoder = encoder[-3:]
    vsFile = 'x' + encoder + '.vpy'

    muxCommand = '# subprocess.run(\'mkvmerge --title "' + movieName + \
        '" \\\n# --stop-after-video-ends --global-tags imdb.tag.xml --chapters chapters.xml -v -o "' + fileName + '" \\\n'
    muxCommand += '# --default-track-flag 0:yes' + videoTag + videoTitle + ' --language 0:eng "1080p.' + encoder + '" \\\n'
else:
    vsFile = 'remux.vpy'
    muxCommand = '# subprocess.run(\'mkvmerge --title "' + movieName + \
        '" \\\n# --stop-after-video-ends --global-tags imdb.tag.xml --chapters chapters.xml -v -o "' + fileName + '" \\\n'
    muxCommand += '# --default-track-flag 0:yes' + videoTag + videoTitle + ' --language 0:eng "' + videoFilename + '" \\\n'

for track in media_info.tracks:
    if track.track_type == "Audio":
        if audioSource[track.track_id] is None:
            tag = ''
        elif "web" not in track.source.lower():
            tag = ' --tags 0:' + audioSource[track.track_id] + '.disc.tag.xml'
        else:
            tag = ' --tags 0:' + audioSource[track.track_id] + '.tag.xml'
        if audioDelay[track.track_id] is None or audioDelay[track.track_id] == 0:
            delay = ''
        else:
            delay = ' --sync 0:' + str(audioDelay[track.track_id])
        if track.title is not None:
            title = re.sub('"', '\\\\\\\"', track.title)
            title = re.sub("'", '\'\"\'\"\'', title)
            title = ' --track-name 0:"' + title + '"'
        else:
            title = ''
        muxCommand += '# --default-track-flag 0:' + track.default.lower() + tag + delay + title + ' --language 0:' + track.language + ' "' + audioFilename[track.track_id] + '" \\\n'
    if track.track_type == "Text":
        if subSource[track.track_id] is None:
            tag = ''
        elif "web" not in track.source.lower():
            tag = ' --tags 0:' + subSource[track.track_id] + '.disc.tag.xml'
        else:
            tag = ' --tags 0:' + subSource[track.track_id] + '.tag.xml'
        if track.title is not None:
            title = re.sub('"', '\\\\\"', track.title)
            title = re.sub("'", '\'\"\'\"\'', title)
            title = ' --track-name 0:"' + title + '"'
        else:
            title = ''
        if subFilename[track.track_id][-3:] == "sup":
            zlib = ' --compression 0:none'
        else:
            zlib = ''
        language = re.search(r"\.([^.]*)\.(sup|srt)$", subFilename[track.track_id]).group(1)
        language = ' --language 0:' + language 
        if track.title is not None and "sdh" in track.title.lower():
            sdh = ' --hearing-impaired-flag 0:yes'
        else:
            sdh = ''
        if track.forced == "Yes":
            forced = ' --forced-display-flag 0:yes'
        else:
            forced = ''
        muxCommand += '# --default-track-flag 0:' + track.default.lower() + tag + forced + sdh + zlib + title + language + ' "' + subFilename[track.track_id] + '" \\\n'
muxCommand += '# \', shell=True)'

if local:
    content = open(os.path.join(localDir, vsFile), 'r')
    if not args.remux:
        oldLoading = 'src = core.ffms2.Source(\'\')'
        newLoading = 'src = core.ffms2.Source(\'' + args.mkv +'\')'
    else:
        oldLoading = 'clip1 = core.ffms2.Source(\'\')'
        newLoading = 'clip1 = core.ffms2.Source(\'' + args.mkv +'\')'
else:
    vsFile = 'remux.py'
    content = open(os.path.join(templateDir, vsFile), 'r')
vsContent = content.read()
content.close()

if os.path.exists(vsFile):
    print('')
    print(f"File {Fore.BLUE}{vsFile}{Style.RESET_ALL} already exists. {Fore.RED}Overwrite?{Style.RESET_ALL} (y/N)")
    answer = input()
    if answer.lower() != 'y':
        summary = summaryTags + summary
        print(summary)
        sys.exit()

vapoursynthFile = Path(vsFile)
if local:
    oldMkvMerge = re.search(r"# subprocess.run\('mkvmerge --title \"(.|\n)*\.(srt|sup)\" \\\n# ', shell=True\)", vsContent, re.MULTILINE).group()
    vapoursynthFile.write_text(vsContent.replace(oldMkvMerge,muxCommand).replace(oldLoading,newLoading))
else:
    oldMkvMerge = re.search(r"subprocess.run\('mkvmerge --title \"(.|\n)*\.(srt|sup)\" \\\n# ', shell=True\)", vsContent, re.MULTILINE).group()
    muxCommand = re.sub('# ','',muxCommand)
    vapoursynthFile.write_text(vsContent.replace(oldMkvMerge,muxCommand))


summary += f"{Style.BRIGHT}{Fore.BLUE}Muxing command{Style.RESET_ALL}: {totalTrack} tracks.\n"
summary += f"File {Fore.BLUE}{vsFile}{Style.RESET_ALL} created.\n"
summary = summaryTags + summary

print('')
print(summary)

# print(muxCommand)

# for track in media_info.tracks:
#     if track.track_type == "Video":
#         print("Track data:")
#         pprint(track.to_data())
