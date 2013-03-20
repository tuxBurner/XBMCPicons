#!/bin/bash

#update the script folder for any changes
git pull;

# initialize the submodules
git submodule init

# pull the latest version for the submodules
git submodule foreach git pull origin master

# update the submoudles
#git submodule update

# rem old picons symlinks
rm ./picons/picons/1_0*.png

# create picons symlinks
sh ./picons/picons.sh ./picons/picons


# create the icons folder
mkdir -p xbmc_icons

# clean out
rm xbmc_icons/*.png

# call the python script in copy mode
python2 xbmcIconLinks.py -p ./picons/picons/ -m c > createXbmcIonsLinks.sh

# run the sh
sh createXbmcIonsLinks.sh 