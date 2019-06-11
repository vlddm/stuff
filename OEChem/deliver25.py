#!/usr/bin/env python

from __future__ import print_function
import sqlite3, sys, os, time
from distutils.dir_util import mkpath

def deliverFiles(ids, dbFile, inputDir, outputDir):
    i = 0
    missedFiles = 0
    for sid in ids:
        with sqlite3.connect(dbFile) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sid,pos,size,filename FROM oechem_data JOIN oechem_filenames ON oechem_filenames.id = oechem_data.filename_id WHERE sid = ?", (sid,))
            row = cursor.fetchone()
            if row:
                sid, pos, size, filename = row

                with open(inputDir + '/' + filename, "r") as f:
                    f.seek(pos)
                    s = f.read(size)
                    #print(s)
                    with open (outputDir + '/' + str(sid), 'wb') as outputFile:
                        outputFile.write(s)
            else:
                missedFiles+=1
        i+=1
        if i % 100 == 0:
                print("\rProgress: [{}/{}]. Missed files count: {}".format(i, len(ids), missedFiles), file=sys.stderr, end='')
                sys.stderr.flush()

def check_ids(ids):
    result = []
    for item in ids.split():
        try:
            result.append(int(item))
        except:
            print("Ignoring {}".format(item), file=sys.stderr)
    return result

def check_dir(myDir):
    if not os.path.isdir(myDir):
        mkpath(myDir)
        print('Creating {}'.format(myDir))
    return myDir

if __name__ == '__main__':
    import argparse
    currentDir = os.getcwd()
    parser = argparse.ArgumentParser(description="OEchem data downloader", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--input-file", dest='inputFile', type=argparse.FileType('r'), metavar='FILE',
                        help="input file with space or newline separated IDs. For stdin use -")
    parser.add_argument("-i", "--ids", dest='ids', type=check_ids, metavar='LIST',
                        help="List of IDs, --ids '399 400 5476276'")
    parser.add_argument("--db", dest='dbFile',  
                        metavar='DBFILE', required=True,
                        help="SQLite database file to read index from.")
    parser.add_argument("-r", "--readfromdir", dest='inputDir',  
                        metavar='DIR', default = currentDir,
                        help='Directory to search input SDF files')     
    parser.add_argument("--output-dir", dest='outputDir', type=check_dir,
                        metavar='DIR', required=True,
                        help='Directory to put resulting SDF files')  

    args = parser.parse_args()

    ids = []
    if args.inputFile:
        ids.extend( check_ids( args.inputFile.read() ) )
        args.inputFile.close()
    if args.ids:
        ids.extend(args.ids)
    if ids:
        startTime = time.time()
        print("Delivering {} files to {}".format(len(ids), args.outputDir), file=sys.stderr)
        deliverFiles(ids = ids, dbFile = args.dbFile, inputDir =args.inputDir, outputDir = args.outputDir)
        print( "\nExecution completed. Work time {:.2f} sec".format(time.time()-startTime) )
    else:
        parser.error ('Either --input-file or --ids is required.')
