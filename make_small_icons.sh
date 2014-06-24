#!/bin/bash

# makes the icons smaller for raspberry and other low level clients
# the huge icons make it unusable
# needs imagemagick

# delete old small dir
rm -rf xbmc_icons_small

# make the dir
mkdir xbmc_icons_small

# copy icons to small dir
cp xbmc_icons/*.png xbmc_icons_small/
cp xbmc_icons/*.svg xbmc_icons_small/

# make them small :)
cd xbmc_icons_small
mogrify -resize 250x250 *.png
mogrify -format png -resize 250x250 *.svg
rm *.svg
mkdir backgrounded
for f in *.png; do
  echo "Processing $f file..";
  convert ../picons/backgrounds/xvdr/grey-white.png "$f" -gravity center -composite -resize 128X128 "backgrounded/$f"
done
rm *.png
mv backgrounded/*.png ./
rm -rf backgrounded
cd ..
