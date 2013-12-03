#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import os, os.path
import re
import sys

class Srindex(object):
    """ Parses a .srindex file for the mapping from a channel to img file """

    srindexInfos = dict()

    def __init__(self, srindex_file = './picons/tv.srindex'):
        """Reads the tv.srindex file """

        try:
            # Open channels.conf
            srindexFile = open(srindex_file, 'r')
        except IOError:
            # Not found / not accessible
            sys.exit ('ERROR: Could not open %s' % srindex_file)

        currStation = ''  
        for srindexLine in srindexFile:
            strippedLine = srindexLine.strip() 
            # means here starts some channelInformations
            if strippedLine.startswith('#') :
                # remove #_ by 2: and strip whitespaces and set it to currStation
                currStation = strippedLine[2:]    
                continue    
            # ignore all --- starting lines    
            if strippedLine.startswith('---') :
                continue 
            # skip empty lines    
            if not strippedLine :
                continue    
            # line contains hash stuff for the channel which matches Channels so we have hash to channelname
            self.srindexInfos[strippedLine] = currStation



class Channels(Srindex):
    """ Holds all the information and routines related to
        linking VDR channels to picons via their respective
        servicerefs. """
        
    channels = []

    def __init__(self, channels_conf = '/etc/vdr/channels.conf', tvonly = False):
        """ Initialize, read and store the channels from
            a given channels.conf. """

        #hier noch den parameter von srindex setzen  
        super(Channels, self).__init__()

        self.tvonly = tvonly

        try:
            # Open channels.conf
            channelsFile = open(channels_conf, 'r')
        except IOError:
            # Not found / not accessible
            sys.exit ('ERROR: Could open %s' % channels_conf)

        # Determine name and parameters for each channel and
        # place that info in the channels list.
        for channelLine in channelsFile:
            # Break down a line from channels.conf and remove
            # leading and trailing whitespace (if any)
            channelSplit = [x.strip() for x in channelLine.split(':')]

            # Add to channels list.
            # Skip '(null)' provider name (Data channels, ...)
            if ((channelSplit[0] is not None)
                and (len(channelSplit) == 13) and channelSplit[0]
                and (';' in channelSplit[0])
                and not (channelSplit[0].split(';')[1] == '(null)')):
                self.channels.append((channelSplit[0], channelSplit[1:],))
    

    def servicerefs(self):
        """ Provides a dictionary of
              ('Channel name': 'serviceref')
            items, e.g.
              ('Das Erste HD;ARD': '2B5C_41B_A401_FFFF0000') """
 
        def _createserviceref(source, freq, vpid, sid, nid, tid):
            """ Subroutine for creating a single service reference.
                All credit to pipelka (https://github.com/pipelka). """

            # Analyze the 'vpid' as early as possible to skip unwanted
            # channels (e.g. set by 'self.tvonly' more quickly).
            if (vpid == '0') or (vpid == '1'):

                # Skip channels of type '2', if 'self.tvonly' is set.
                if self.tvonly:
                    return


            # usually (on Enigma) the frequency is part of the namespace
            # for picons this seems to be unused, so disable it by now
            freq = 0;

            if source.startswith('S'):
                negative = False

                source = source[1:]
                if source.endswith('E'):
                    negative = True
                source = source[:-1]
                if '.' in source:
                    (number, decimal) = source.split('.')
                position = 10 * int(number) + int(decimal)
                if negative:
                    position = -position

                if position > 0x00007FFF:
                    position |= 0xFFFF0000

                if position < 0:
                    position = -position
                else:
                    position = 1800 + position

                hash = position << 16 | ((freq / 1000) & 0xFFFF)

            elif source.startswith('C'):
                hash = 0xFFFF0000 | ((freq / 1000) & 0xFFFF)

            elif source.startswith('T'):
                hash = 0xEEEE0000 | ((freq / 1000000) & 0xFFFF)

            if '=' in vpid:
                (pid, streamtype) = [x.strip() for x in vpid.split('=')]

            return '%X_%X_%X_%X' % (
                    sid,
                    tid,
                    nid,
                    hash
                )

        serviceRefs = dict()

        for (channelName, channelParams) in self.channels:
            # Determine serviceref and fill dictionary.
            serviceRef = _createserviceref(
                channelParams[2],
                int(channelParams[0]),
                channelParams[4],
                int(channelParams[8]),
                int(channelParams[9]),
                int(channelParams[10]))

            # A skipped channel (e.g. with 'self.tvonly') would return
            # None for serviceref. Don't add those to the dictionary
            if serviceRef is not None:
                serviceRefs[serviceRef] = channelName

        return serviceRefs

class PIcons(Channels):
    """ Find all available picons in a given path and determine
        the channels that can be linked automatically. """

    picons = []

    def __init__(self, channels_conf = '/etc/vdr/channels.conf', tvonly = False,
         picons_dir = './picons', dest_dir = './xbmc_icons', mode = 'l'):

        if(mode != 'l' and mode != 'c'):
              sys.exit('ERROR: mode must be l or c you give %s' % mode);

        # Initialize superclass
        super(PIcons, self).__init__(channels_conf = channels_conf,
            tvonly = tvonly)

    
        try:
            # List directory containing picons.
            piconDirList = os.listdir(picons_dir)
        except OSError:
            # Not found / not accessible.
            sys.exit ('ERROR: Couldn\'t open %s' % picons_dir)

        # Filter for '.png' and '.svg'.
        def png(x):
           return  x.endswith('.png') or x.endswith('.svg')
        piconDirList = filter(png, piconDirList)


        if piconDirList == []:
            # Empty directory or no '.png' files
            sys.exit ('ERROR: The directory %s does not contain any picons.' % picons_dir)

        # Fill class variable
        self.picons = [x for x in piconDirList]

        self.dest_dir = dest_dir
        self.picons_dir = picons_dir
        self.mode = mode

    def lnscript(self):
        """ Finally, create mapping between picon and serviceref.
            Return the result in form of a shell script. """
        
        links = dict()
        unmatched = []

        serviceRefs = self.servicerefs()
        for serviceRef  in serviceRefs:
            # icons not mapped should go into umateched
            if not self.srindexInfos.has_key(serviceRef) : 
                unmatched.append(serviceRef)
                continue

            channelPngName = self.srindexInfos[serviceRef]
            # use the channel name from the channels.conf so xbmc can map it
            xbmcIconName = serviceRefs[serviceRef];
            links[channelPngName] = (xbmcIconName.rsplit(';', 1)[0].rsplit(',',1)[0])    
            
            #if serviceRef in self.picons:
            #    channelPngName = serviceRefs[serviceRef]
            #    channelPngName = channelPngName.rsplit(';', 1)[0].rsplit(',',1)[0]
            #    links[serviceRef] = (channelPngName)
            #    continue

            
        
        for (iconName, channelName) in sorted(links.iteritems()):            
            #check svg or png
            fileEnding = '.svg'
            if iconName+'.png' in self.picons :
              fileEnding = '.png'               

            channelName = channelName.replace('/',' ')
            srcPath = os.path.abspath(self.picons_dir+'/'+iconName+fileEnding)
            destPath = os.path.abspath(self.dest_dir+'/'+channelName+fileEnding)

            if self.mode == 'l':
                print 'ln -sf "%s" "%s"' % (srcPath,destPath)
            elif self.mode == 'c':
                print 'cp "%s" "%s"' % (srcPath,destPath)  
        
        # Print unmatched
        if unmatched != []:
            print '# unmatched channels:'

        for serviceRef in unmatched:
            print '# %s %s' % (serviceRef, serviceRefs[serviceRef])


def main():
    # Define commandline arguments
    parser = argparse.ArgumentParser(description="Automatically provide shell scripts for linking ocram's picons.")
    parser.add_argument('-c', '--channels',
        metavar = 'channels.conf',
        default = '/etc/vdr/channels.conf',
        help = 'pathname of channels.conf')
    parser.add_argument('-p', '--picondir',
        metavar = 'picons dir',
        default = './picons',
        help = "directory containing ocram's picons")
    parser.add_argument('-t', '--tvonly',
        action = 'store_true',
        default = False,
        help = "process TV channels only (i.e. no Radio)")
    parser.add_argument('-d', '--destination',
        metavar = 'destination dir',
        default = './xbmc_icons',
        help = "where to put the matched icons for xbmc")
    parser.add_argument('-m', '--mode',
        metavar = 'l or c',
        default = 'l',
        help = "mode for creating xbmc icons l means link c means to copy")
    
    argsDict = vars(parser.parse_args())

    # Instantiate
    picons = PIcons(channels_conf = argsDict['channels'],
        tvonly = argsDict['tvonly'],
        picons_dir = argsDict['picondir'],
        dest_dir = argsDict['destination'],
        mode = argsDict['mode'])
    # Print script snippet
    picons.lnscript()

if __name__ == '__main__':
    sys.exit(main())
