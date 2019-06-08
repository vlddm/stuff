#!/usr/bin/env python

from __future__ import print_function
import sys, tarfile, gzip, os, time
from io import BytesIO


PATH = os.path.dirname(__file__)+"/../resultFiles"


def downloadFiles(IDs):
    global PATH
    memoryFile = BytesIO()
    with tarfile.open(fileobj=memoryFile, mode="w:gz") as tf:
        for shortID in IDs:
            ID = '{:09d}'.format(int(shortID)) # Leading zeros
            gzFilePath = "{}/{}/{}/{}.gz".format(PATH, ID[0:3], ID[3:6], ID)
            if os.path.isfile(gzFilePath):
                with gzip.open(gzFilePath, 'rb') as f:
                    data = f.read()
                    tarinfo = tarfile.TarInfo(name=str(shortID))
                    tarinfo.size = len(data)
                    tf.addfile(tarinfo, BytesIO(data))
            else:
                print("No such file: {}".format(gzFilePath), file=sys.stderr)
    resultData = memoryFile.getvalue()
    memoryFile.close()
    return resultData

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
    
    parser = argparse.ArgumentParser(description="OEchem data downloader")
    parser.add_argument("-f", "--input-file", dest='inputFile', type=argparse.FileType('r'), metavar='FILE',
                        help="input file with space or newline separated IDs. For stdin use -")
    parser.add_argument("-i", "--ids", dest='ids', type=check_ids, metavar='LIST',
                        help="List of IDs, --ids '399 400 5476276'")
    parser.add_argument("-o", "--output-file", dest='outFile', type=argparse.FileType('w'), 
                        metavar='FILE', required=True,
                        help='Output archive name, like result.tar.gz. For stdout use -')     

    args = parser.parse_args()

    ids = []
    if args.inputFile:
        ids.extend( check_ids( args.inputFile.read() ) )
        args.inputFile.close()
    if args.ids:
        ids.extend(args.ids)
    if ids:
        print("packing {} to {}".format(ids, args.outFile.name), file=sys.stderr)
        resultZip = downloadFiles(ids)
        args.outFile.write(resultZip)
        args.outFile.close()
    else:
        parser.error ('Either --input-file or --ids is required.')

        
