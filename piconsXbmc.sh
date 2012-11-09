#!//bin/bash

#update the script folder for any changes
git pull;

# initialize the submodules
git submodule init

# update the submoudles
git submodule update

# create picons symlinks
sh ./picons/picons.sh ./picons/picons


# create the icons folder
mkdir -p xbmc_icons;

# clean out
rm xbmc_icons/*

# call the python script in copy mode
python2 xbmcIconLinks.py -c channels.conf -p ./picons/picons/ -m c > createXbmcIonsLinks.sh

# run the sh
sh createXbmcIonsLinks.sh 
