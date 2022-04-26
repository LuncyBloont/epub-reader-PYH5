#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile
import sys
import shutil
import subprocess
import xml.dom.minidom as dom
import webbrowser
import socket

def toMetaPath(dirPath):
    with open(os.path.join(dirPath, 'META-INF', 'container.xml'), 'r') as f:
        data = f.read()
        xr = dom.parseString(data).documentElement
        return '/' + xr.getElementsByTagName("rootfile")[0].getAttribute('full-path')

def main():
    if len(sys.argv) < 2:
        sys.stderr.write('Error: too less arguments. Need file path')
        exit(-1)

    path = sys.argv[1]
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
        
        print('http://127.0.0.1:' + str(port) + '/index.html')
        webbrowser.open('http://127.0.0.1:' + str(port) + '/index.html')
        subprocess.run(['python', '-m', 'http.server',
                         '--directory', tmpdir,
                         str(port)], shell=True)
        exit(0)
        
    except Exception as err:
        sys.stderr.write(str(err))

if __name__ == '__main__':
    main()
