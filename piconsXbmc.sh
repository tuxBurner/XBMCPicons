#!/bin/bash

PICONS_GIT_REPO="https://github.com/picons/picons-source.git"

#update the script folder for any changes
echo "Checking if Script is up to date"
git pull origin master

# get the picons :)
if [ ! -d "./picons" ]; then
 echo "Picons dir does not exist. Cloning it from: $PICONS_GIT_REPO";
 git clone  --depth 1 --branch master $PICONS_GIT_REPO ./picons;
fi

echo "Update picons"
cd ./picons
git pull origin master
cd ..


# create the icons folder
if [ ! -d "./xbmc_icons" ]; then
 echo "xbmc_icons dir does not exist. Creating it.";
 mkdir ./xbmc_icons;
fi

# clean out
echo "Deleting old xbmc_icons"
rm xbmc_icons/*

# call the python script in copy mode
python2 xbmcIconLinks.py -p ./picons/build-source/tv/ -c ./channels.conf -m c > createXbmcIonsLinks.sh

# run the sh
sh createXbmcIonsLinks.sh
