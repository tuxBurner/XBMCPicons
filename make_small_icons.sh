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

# make them small :)
cd xbmc_icons_small
mogrify -resize 128x128 *.png
cd ..
