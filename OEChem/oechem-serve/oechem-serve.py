#!/usr/bin/env python

import sys, zipfile, gzip, os, time
import SimpleHTTPServer, SocketServer, cgi
from io import BytesIO
import config


class PostHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_POST(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        zipFile = downloadFiles(form['IDs'].value.split())
        self.send_header("Content-Type", 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename=OEChem_{}.zip'.format(time.strftime("%Y-%m-%d_%H-%M-%S")))
        self.send_header("Content-Length", str(len(zipFile)))
        self.end_headers()
        self.wfile.write(zipFile)


def downloadFiles(IDs):
    memoryFile = BytesIO()
    with zipfile.ZipFile(memoryFile,'w') as zf:
        for shortID in IDs:
            ID = '{:09d}'.format(int(shortID)) # Leading zeros
            gzFilePath = "{}/{}/{}/{}.gz".format(config.PATH, ID[0:3], ID[3:6], ID)
            if os.path.isfile(gzFilePath):
                with gzip.open(gzFilePath, 'rb') as f:
                    data = f.read()
                    zf.writestr(shortID, data)
            else:
                print("No such file: {}".format(gzFilePath))
    resultData = memoryFile.getvalue()
    memoryFile.close()
    return resultData

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        resultZip = downloadFiles(sys.argv[1:])
        with open(config.ZIPNAME, 'wb') as zp:
            zp.write(resultZip)
    else:

        webDir = os.path.join(os.path.dirname(__file__), 'html')
        os.chdir(webDir)

        try:
            httpd = SocketServer.TCPServer(("", config.PORT), PostHandler)
            print "serving at port", config.PORT
            httpd.serve_forever()
        except Exception as e: 
            print(e)
        finally:
            print("Closing socket")
            if httpd in vars():
                httpd.server_close()
