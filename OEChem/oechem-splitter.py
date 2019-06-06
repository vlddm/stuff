#!/usr/bin/env python
from __future__ import print_function
import os
import time
import gzip
import sys
from distutils.dir_util import mkpath

__author__ = 'span1ard'

def sec2time(sec, n_msec=0):
    ''' Convert seconds to 'D days, HH:MM:SS.FFF' '''
    if hasattr(sec,'__len__'):
        return [sec2time(s) for s in sec]
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if n_msec > 0:
        pattern = '%%02d:%%02d:%%0%d.%df' % (n_msec+3, n_msec)
    else:
        pattern = r'%02d:%02d:%02d'
    if d == 0:
        return pattern % (h, m, s)
    return ('%d days, ' + pattern) % (d, h, m, s)

def splitFile(filename):
    bytesWriten = 0
    with open(filename, "r") as f:
        data = f.read()
        for j in data.split('$$$$'):
            if j.find('\n') == 0:
                j = j[1:]
            resultFileName = j[:j.find('\n')]
            if resultFileName != '':
                resultFileName = '{:09d}'.format(int(resultFileName))
                one = resultFileName[0:3]
                two = resultFileName[3:6]
                deepDir = 'resultFiles/{}/{}'.format(one, two)
                if not os.path.isdir(deepDir):
                    mkpath(deepDir)
                with gzip.open(deepDir + '/' + resultFileName + '.gz', 'wb', 3) as fr:
                #with open(deepDir + '/' + resultFileName, 'w') as fr:
                    fr.write(j)
                    fr.flush()
                    #os.fsync(fr.fileno())
                    bytesWriten += len(j)
    return bytesWriten

def savePosition(fileNameString):
    global storageFile
    with open(storageFile, 'w') as f:
        f.write(fileNameString)
        f.flush()
        os.fsync(f.fileno())

def readPosition():
    global storageFile
    try: 
        with open(storageFile, 'r') as f:
            return f.readline()
    except:
        pass    

def main(startFrom=None):
    work_time = time.time()
    try:
        os.mkdir('resultFiles')
    except OSError:
        pass
    filesList = os.listdir(os.getcwd())
    filesList = [x for x in filesList if x[-4:] == '.sdf']
    filesList.sort()
    if startFrom != None:
        if startFrom not in filesList:
            print("Error: startfile {} not found".format(startFrom))
            exit(1)
        filesList = filesList[filesList.index(startFrom):]
        print('Starting from {}'.format(startFrom))

    fileNumber = 0 
    bytesWriten = 0
    size = len(filesList)
    fileProcessingSec = 10

    for currentFile in filesList:
        secSinceStart = time.time() - work_time
        fileNumber += 1
        secLeft = (size-fileNumber)*secSinceStart/fileNumber
        print ("\rProgress: [{}/{}], speed: {:.2f} MB/sec, elapsed time: {}, ETA: {}. Processing now: {}".format( fileNumber, len(filesList), (bytesWriten/1048576)/secSinceStart, sec2time(secSinceStart), sec2time(secLeft), currentFile), end="")
        sys.stdout.flush()
        savePosition(currentFile)
        bytesWriten = splitFile(currentFile)

    work_time = time.time() - work_time
    print("\nExecution completed. Work time {:.3f} sec".format(work_time))

if __name__ == '__main__':
    storageFile = '.oechem-splitter-last-file.txt'
    startfile = None
    if len(sys.argv) >= 2:
        if os.path.isfile(sys.argv[1]):
            startfile = sys.argv[1]
        else:
            print ("{} is not exist in current directory, exiting".format(sys.argv[1]))
            exit(1)
    else:
        fromFile = readPosition()
        if fromFile and os.path.isfile(fromFile):
            print('Looks like last run was terminated on {}. Do you want to continue from it or start over?'.format(fromFile))
            userInput = ''
            while userInput not in ('C', 'S', 'E'):
                userInput = raw_input('C to Contunue, S to start over, E to exit [C/S/E]: ').upper()
            if userInput == 'C':
                startfile = fromFile
            if userInput == 'S':
                print('Starting over')
            if userInput == 'E':
                print("Exiting")
                exit(1)

    main(startfile)
