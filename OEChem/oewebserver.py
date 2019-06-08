#!/usr/bin/env python

import SocketServer, cgi, oechem, time
from BaseHTTPServer import BaseHTTPRequestHandler

class PostHandler(BaseHTTPRequestHandler):
    
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
        tarFile = oechem.downloadFiles(form['IDs'].value.split())
        self.send_header("Content-Type", 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename=OEChem_{}.tar.gz'.format(time.strftime("%Y-%m-%d_%H-%M-%S")))
        self.send_header("Content-Length", str(len(tarFile)))
        self.end_headers()
        self.wfile.write(tarFile)

    def do_GET(self):
        # Parse the form data posted
        html = """
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta charset="utf-8" />
            <title>OEchem</title>
        </head>
        <body style="padding:40px; padding-top:20px;">
            <h2>Input OEChem IDs:</h2>
            <form action="getTarFile" form="IDs" method="post">
                <textarea name="IDs" style="width:100%;height:200px;"></textarea>
                <button type="submit" style="margin-top:30px; padding:10px">Get TAR</button>
            </form>
        </body>
        </html>
        """
        # Begin the response
        self.send_response(200)
        self.send_header("Content-Type", 'text/html')
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="OEchem web server")
    parser.add_argument("-p", "--port", dest='port', type=int, default=8000, 
                        nargs="?", metavar='PORT',
                        help='Start http server on PORT')
    args = parser.parse_args()

    try:
        httpd = SocketServer.TCPServer(("", args.port), PostHandler)
        print "serving at port", args.port
        httpd.serve_forever()
    except Exception as e: 
        print(e)
    finally:
        print("Closing socket")
        if httpd in vars():
            httpd.server_close()     