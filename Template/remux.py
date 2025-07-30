import sys
import subprocess


##########
# Muxing #
##########

subprocess.run('mkvmerge --title "Little Women (2019)" \
--stop-after-video-ends --global-tags imdb.tag.xml --chapters chapters.xml -v -o "Parthenope.2024.2160p.UHD.Blu-ray.Remux.HDR.HEVC.DTS-HD.MA.5.1-CiNEPHiLES.mkv" \
--default-track-flag 0:yes --tags 0:uhd.disc.tag.xml --language 0:eng "uhd.video.hevc" \
--default-track-flag 0:yes --tags 0:uhd.disc.tag.xml --track-name 0:"Surround 7.1" --language 0:eng "uhd.surround.dtsma" \
--default-track-flag 0:no --tags 0:nf.tag.xml --language 0:ukr "nf.ukr.srt" \
--default-track-flag 0:no --tags 0:nf.tag.xml --language 0:vie "nf.vie.srt" \
', shell=True)
