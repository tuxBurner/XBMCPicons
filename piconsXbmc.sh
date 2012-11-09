#!//bin/bash

#update the icons
git pull;

mkdir -p xbmc_icons;

rm xbmc_icons/*

python2 xbmcIconLinks.py -c channels.conf -m c > createXbmcIonsLinks.sh

sh createXbmcIonsLinks.sh 
