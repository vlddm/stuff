#!/usr/bin/env python

from __future__ import print_function
import sys, tarfile, gzip, os, time
from io import BytesIO

def downloadFiles(IDs, outfile, inputDir):
    missedFiles = 0
    i = 0
    with tarfile.open(fileobj=outfile, mode="w:gz") as tf:
        for shortID in IDs:
            i+=1
            ID = '{:09d}'.format(int(shortID)) # Leading zeros
            gzFilePath = "{}/{}/{}/{}.gz".format(inputDir, ID[0:3], ID[3:6], ID)
            if os.path.isfile(gzFilePath):
                with gzip.open(gzFilePath, 'rb') as f:
                    data = f.read()
                    tarinfo = tarfile.TarInfo(name=str(shortID))
                    tarinfo.size = len(data)
                    tf.addfile(tarinfo, BytesIO(data))
            else:
                missedFiles += 1
            if i % 100 == 0:
                print("\rProgress: [{}/{}]. Missed files count: {}".format(i, len(IDs), missedFiles), file=sys.stderr, end='')
                sys.stderr.flush()


def check_ids(ids):
    result = []
    for item in ids.split():
        try:
            result.append(int(item))
        except:
            print("Ignoring {}".format(item), file=sys.stderr)
    return result


if __name__ == '__main__':
    import argparse
    readFromPath = os.path.realpath(os.path.dirname(__file__)+"/../resultFiles/")
    parser = argparse.ArgumentParser(description="OEchem data downloader", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--input-file", dest='inputFile', type=argparse.FileType('r'), metavar='FILE',
                        help="input file with space or newline separated IDs. For stdin use -")
    parser.add_argument("-i", "--ids", dest='ids', type=check_ids, metavar='LIST',
                        help="List of IDs, --ids '399 400 5476276'")
    parser.add_argument("-o", "--output-file", dest='outFile', type=argparse.FileType('w'), 
                        metavar='FILE', required=True,
                        help='Output archive name, like result.tar.gz. For stdout use -')     
    parser.add_argument("-r", "--readfromdir", dest='readFromPath',  
                        metavar='DIR', default = readFromPath,
                        help='Directory to search input files.')     

    args = parser.parse_args()

    ids = []
    if args.inputFile:
        ids.extend( check_ids( args.inputFile.read() ) )
        args.inputFile.close()
    if args.ids:
        ids.extend(args.ids)
    if ids:
        print("packing {} files to {}".format(len(ids), args.outFile.name), file=sys.stderr)
        downloadFiles(IDs = ids, outfile = args.outFile, inputDir = readFromPath)
    else:
        parser.error ('Either --input-file or --ids is required.')

        
