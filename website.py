#!/usr/bin/env python3
from pathlib import Path
from uuid import uuid4

"""Simple HTTP Server With Upload.
This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.
see: https://gist.github.com/UniIsland/3346170
"""

__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456"
__home_page__ = "http://li2z.cn/"

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO
from memory_tempfile import MemoryTempfile

from redis import Redis
from rq import Queue
from queue_functions import save_to_hard_drive

REDIS = True
QUEUE = Queue(connection=Redis())

import redis
conn = redis.Redis('localhost')

# data = {}
# conn.hmset("pythonDict", data)
# conn.hgetall("pythonDict")
# conn.hget("pythonDict", "Name")
# conn.set('test.py',"value")

RESULTS = Path("./results")
html_path = "/handwriting"

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP request handler with GET/HEAD/POST commands.
    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.
    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.
    """

    server_version = "SimpleHTTPWithUpload/" + __version__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = REDIS
        if self.redis:
            # Make sure the sever is started
            # subprocess.Popen("bash /media/data/OneDrive/Documents/Graduate School/2020.1/601R - Big Data/redis/redis-5.0.7/src/redis-server", shell=True)
            self.queue = Queue(connection=Redis())
            print(self.queue)
            pass

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()
        else:
            print("f", f)

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r, info, rand_token = self.deal_post_data()

        print((r, info, "by: ", self.client_address))
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b"<html>\n<title>Upload Result Page</title>\n")
        f.write(b"<body>\n<h2>Upload Result Page</h2>\n")
        f.write(b"<hr>\n")
        if r:
            f.write(b"<strong>Success:</strong>")
        else:
            f.write(b"<strong>Failed:</strong>")
        f.write(info.encode())
        f.write(("<br><a href=\"%s\">back</a><br>" % self.headers['referer']).encode())

        if rand_token:
            result_website = f"<a href=\"{html_path}/RESULT_overlay_0_{rand_token}\">here</a>"
            result_website2 = f"<a href=\"{html_path}/RESULT_0_{rand_token}\">here</a>"
            f.write(f"Your results will be available {result_website} and {result_website2}".encode())

        #f.write(b"<hr><small>Powerd By: bones7456, check new version at ")
        #f.write(b"<a href=\"http://li2z.cn/?s=SimpleHTTPServerWithUpload\">")
        f.write(b"</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        rand_token = None
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        print("line", line)
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)

        rand_token = uuid4()
        raw_path = f"./raw/{rand_token}"
        try:
            out = open(raw_path, 'wb')
            #tempfile_obj = MemoryTempfile()
            #out = tempfile_obj.TemporaryFile()
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?", None)

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                #if self.redis:
                if REDIS:
                    try:
                        #self.queue.enqueue(save_to_hard_drive, (tempfile_obj, fn))
                        print(line.decode())
                        text = re.findall(r'.*name="gt"', line.decode())
                        user = re.findall(r'.*name="user"', line.decode())
                        print("QUEUING IT UP!")
                        QUEUE.enqueue(save_to_hard_drive, (fn,raw_path, rand_token, text, user))
                    except Exception as e:
                        print(e)
                        return (True, "Problem queuing to Redis", None)
                return (True, "File '%s' upload success!" % fn, rand_token)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpected end of data.", None)

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        job = Path(path).stem
        if job.startswith("RESULT_"):
            # Check if it's done
            print("Looking for result")
            f = self.check_on_file(job)
            return f
        else:
            f = None
            if os.path.isdir(path):
                if not self.path.endswith('/'):
                    # redirect browser - doing basically what apache does
                    self.send_response(301)
                    self.send_header("Location", self.path + "/")
                    self.end_headers()
                    return None
                for index in "index.html", "index.htm":
                    index = os.path.join(path, index)
                    if os.path.exists(index):
                        path = index
                        break
                else:
                    return self.list_directory(path)
            return self.return_file(path)

    def return_file(self, path):
        ctype = self.guess_type(str(path))
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
            print(f"File found, opening {path}")
        except IOError:
            self.send_error(404, "File not found")
            print("File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<title>Upload your handwriting!</title>\n").encode())
        f.write(("<body>\n<h2>Upload your handwriting!</h2>\n").encode())
        f.write(b"<hr>\n")
        f.write(b"<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write(b"<input name=\"file\" type=\"file\"/>")
        f.write(b"""<input type=\"submit\" value=\"upload\"/><br>
          <label for="user">Name:</label><br>
          <input type="text" id="user" name="user"><br>
          <label for="gt">Ground Truth Text:</label><br>
          <input type="text" id="gt" name="gt">    
            </form>\n""")
        f.write(b"""<br> This tool is designed to work on single lines of images, similar to the one below; tested with PNG images <br>""")
        f.write(f"""<br><img src=\"{html_path}/data/a01-000u-05.png\" height='30'><br>""".encode())
        f.write(b"""<br> Sample output: <br>""")
        f.write(f"""<img src=\"{html_path}/data/output/a01-000u-02.png\" height='60'>""".encode())

        f.write(b"<hr>\n<ul>\n")
        for name in []: #list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(('<li><a href="%s">%s</a>\n'
                     % (urllib.parse.quote(linkname), cgi.escape(displayname))).encode())
        f.write(b"</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.
        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).
        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.
        Argument is a PATH (a filename).
        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.
        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

    def check_on_file(self, result_token):
        token = result_token[7:]
        print(f"Requested {RESULTS / f'{token}.png'}")
        path = RESULTS / f"{token}.png"
        if path.exists():
            print("Image found")
            f = self.return_file(path)
            return f

        else:
            self.make_webpage(
            b"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
            <html>\n<title>Still processing</title>\n
            <body>\n<h2>This upload is still processing. Please check back later.</h2>\n            
            <hr> \n
            </body></html>""")
            return None
            # \n

    def make_webpage(self, html):
        #r, info = self.deal_post_data()

        f = BytesIO()
        f.write(html)
        #f.write(info.encode())

        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()


def test(HandlerClass=SimpleHTTPRequestHandler,
         ServerClass=http.server.HTTPServer):
    http.server.test(HandlerClass, ServerClass)

class Handler2(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="handwriting", **kwargs)


def run():
    PORT = 10031
    Handler = SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("", PORT), Handler)
    httpd.serve_forever()


if __name__ == '__main__':
    #test.py()
    run()