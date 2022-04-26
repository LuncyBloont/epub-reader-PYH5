#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import zipfile
import sys
import shutil
import xml.dom.minidom as dom
import webbrowser
import socket
import threading

class OpenBookT (threading.Thread):
    url = ''
    def __init__(self, id, name, delay, url):
        threading.Thread.__init__(self)
        self.threadID = id
        self.name = name
        self.delay = delay
        self.url = url
    def run(self):
        webbrowser.open(self.url)

def toMetaPath(dirPath):
    with open(os.path.join(dirPath, 'META-INF', 'container.xml'), 'r') as f:
        data = f.read()
        xr = dom.parseString(data).documentElement
        return '/' + xr.getElementsByTagName("rootfile")[0].getAttribute('full-path')

def openBook(url):
    time.sleep(1)
    webbrowser.open(url)

def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: too less arguments. Need file path')
        exit(-1)

    args = sys.argv.copy()
    args.pop(0)
    path = ' '.join(args)
    print('Open', path)
    port = 8123
    maxloop = 256
    while maxloop > 0:
        try:
            socket.socket(socket.AF_INET).connect(('127.0.0.1', port))
            port += 1
            maxloop -= 1
        except Exception as err:
            maxloop = -5
    if maxloop == 0:
        sys.stderr.write('Max port count!')
        exit(-1)
    tmpdir = os.path.join('.', r'tmp' + str(port))
    
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    
    metajs = '''
var meta = {
'''

    try:
        f = zipfile.ZipFile(path)
        for file in f.namelist():
            f.extract(file, tmpdir)
            
        metajs += '"metaPath": "%s"' % (toMetaPath(tmpdir))
        
        metajs += '\n}'
        with open('meta.js', 'w') as wf:
            wf.write(metajs)
        
        shutil.copy('index.html', os.path.join(tmpdir, 'index.html'))
        shutil.copy('meta.js', os.path.join(tmpdir, 'meta.js'))
        
        url = 'http://127.0.0.1:' + str(port) + '/index.html'
        print(url)
        t = OpenBookT(1, 'Book', 1, url)
        t.start()
        
        os.system(' '.join(['python', '-m', 'http.server',
                         '--directory', tmpdir,
                         str(port)]))
        exit(0)
        
    except Exception as err:
        sys.stderr.write(str(err))

if __name__ == '__main__':
    main()
