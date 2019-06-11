#!/usr/bin/env python

from __future__ import print_function
import os
import time
import gzip
import sys
import sqlite3
from distutils.dir_util import mkpath

class SQLite():
    def __init__(self, file='sqlite.db'):
        self.file=file
    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        #self.conn.row_factory = sqlite3.Row
        return self.conn.cursor()
    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

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


def indexFile(inputDir, filename, fileNumber, cursor):
    bytesWriten = 0
    indexData = []
    position = 0
    cidString = "<PUBCHEM_CID_ASSOCIATIONS>\n"
    cursor.execute('INSERT OR REPLACE INTO oechem_filenames(id,filename) VALUES (?,?)', (fileNumber,filename))
    filename_id = cursor.lastrowid
    with open(inputDir + '/' + filename, "r") as f:
        data = f.read()
        for j in data.split('\n\n$$$$\n'):
            try:
                size = len(j)+2
                if j == '':
                    continue
                id = int( j[:j.find('\n')] )
                cid_pos = j.find(cidString)
                if cid_pos == -1:
                    cid = None
                else:
                    cid_pos += len(cidString)
                    cid = int( j[cid_pos:cid_pos+12].split()[0] )
                currentMoleculeData = (id, position, size, cid, filename_id)
                #print(currentMoleculeData)
                indexData.append(currentMoleculeData)
                position += size + 5
                idprev = id
                #print(indexData)
            except Exception as e:
                print("\n", e)
                print("j:'{}'".format(j))
                print(filename)
                print(idprev)
                exit(1)
        filesize = f.tell()
        cursor.executemany('INSERT OR REPLACE INTO oechem_data(sid,pos,size,cid,filename_id) VALUES (?,?,?,?,?)', indexData)
    return filesize 

def main(startFrom, dbFile, inputDir):
    work_time = time.time()
    filesList = os.listdir(inputDir)
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
    
    with SQLite(dbFile) as cursor:
        initDB(cursor)
        for currentFile in filesList:
            currentFileStartTime = time.time()
            fileNumber += 1
            bytesReaden = indexFile(inputDir, currentFile, fileNumber, cursor)
            secSinceStart = time.time() - work_time
            secLeft = (size-fileNumber)*secSinceStart/fileNumber
            print ("\r{} [{}/{}] {:.2f}MB/sec | time {} | ETA {}".format(currentFile, fileNumber, len(filesList), (bytesReaden/1048576)/(time.time() - currentFileStartTime), sec2time(secSinceStart), sec2time(secLeft)), end="")
            sys.stdout.flush()

    work_time = time.time() - work_time
    print("\nExecution completed. Work time {:.3f} sec".format(work_time))

def initDB(cursor):
    initTables = '''
    CREATE TABLE IF NOT EXISTS oechem_data (
        sid INTEGER PRIMARY KEY NOT NULL,
        pos INTEGER NOT NULL,
        size INTEGER NOT NULL,
        cid INTEGER KEY,
        filename_id INTEGER NOT NULL
    );
    CREATE TABLE IF NOT EXISTS oechem_filenames (
        id INTEGER PRIMARY KEY NOT NULL,
        filename TEXT NOT NULL
    )
    '''
    for statement in initTables.split(';'):
        cursor.execute(statement)

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
    currentDir = os.getcwd()
    parser = argparse.ArgumentParser(description="OEchem data downloader", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--db", dest='dbFile',  
                        metavar='DBFILE', required=True,
                        help="SQLite database file to store index. Must not exist")
    parser.add_argument("-r", "--readfromdir", dest='inputDir',  
                        metavar='DIR', default = currentDir,
                        help='Directory to search input SDF files')     

    args = parser.parse_args()

    if os.path.isfile(args.dbFile):
        print("file {} exists, exiting".format(args.dbFile))
        exit(1)
    inputDir = os.path.abspath(args.inputDir)
    dbFile = os.path.abspath(args.dbFile)
    main(startFrom=None, dbFile = dbFile, inputDir = inputDir)
    print("Index saved to {}.".format(dbFile))
    print("To get CSV from sqlite database you can use this command:")
    print(" sqlite3 -header -csv {} 'select sid,cid from oechem_data' > output.csv".format(dbFile))
    print("")