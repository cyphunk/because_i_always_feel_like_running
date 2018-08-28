#!/usr/bin/python
# -*- coding: utf-8 -*-
# RUN AS ROOT FOR PORT 80
import web
from web.wsgiserver import CherryPyWSGIServer
import subprocess
import os, signal
import re
import time
import liblo

DEBUG=True
MODEL_NAME     = os.environ.get('MODEL_NAME') or "v1"
BASE_DIR       = os.environ.get('BASE_DIR') or os.path.dirname(os.path.abspath(__file__))+"/../"

MEDIADIR         = BASE_DIR+"/media_player/media"
MEDIACONTROLFILE = BASE_DIR+"/media_player/media_selected.txt"
MEDIAVIDEO       = ['mov','avi','mp4', 'mkv']
MEDIAIMAGE       = ['png','jpeg','jpg','gif']
MEDIACOUNTER     = ['txt'] # special type to schedule in the counter
MEDIATYPES       = MEDIAVIDEO+MEDIAIMAGE+MEDIACOUNTER
MEDIADEFAULT     = '00_blank.png'
MATRIXARGS    = os.environ.get('MATRIXARGS') or ""
BRIGHTNESS    = os.environ.get('BRIGHTNESS') or "100"
CMDIMAGE      = os.environ.get('CMDIMAGE') or "eog"
CMDIMAGEARGS  = os.environ.get('CMDIMAGEARGS') or ""
CMDVIDEO      = os.environ.get('CMDVIDEO') or "mplayer"
CMDVIDEOARGS  = os.environ.get('CMDVIDEOARGS') or ""
CMDCOUNT      = os.environ.get('CMDCOUNT') or CMDIMAGE
CMDCOUNTARGS  = os.environ.get('CMDCOUNTARGS') or ""
CMDTESTDISPLAY = os.environ.get('CMDTESTDISPLAY') or  "../test_display.sh"
CMDTEXT      = os.environ.get('CMDTEXT') or "cat"

urls = (
  "/osctest",     "osctest",
  "/displaytest", "displaytest",

  "/help",        "help",
  "/hr",          "hr",
  "/counter",     "counter",
  "/media_play",  "media_play",
  "/upload",      "upload",
  "/(.*)",        "index"
)

def debug(message):
    if not DEBUG:
        return
    print (message)


# First arg on cmdline would be port
#app = web.application(urls, globals())
# Do this to set port in code
class myApp(web.application):
    def run(self, port=80, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

app = myApp(urls, globals())

class hr:
    def GET(self):
        x = web.input()
        t = liblo.Address(9001)
        global BRIGHTNESS
        if 'brightness' in x and len(x.brightness)>0 and x.brightness != 'undefined':
            BRIGHTNESS = str(min(100, int(x.brightness)))

        if x.do == 'start':
            liblo.send(t, 'max', BRIGHTNESS)
            liblo.send(t, 'pause', 0)
        elif x.do == 'stop':
            liblo.send(t, 'pause', 1)
        elif x.do == 'set':
            print("send hr", x.hr)
            liblo.send(t, 'int', int(x.hr))
        return
class osctest:
    def GET(self):
        t = liblo.Address(9000)
        for x in range(1,20):
            print ("osctest loop", x)
            for i in range(100,0,-1):
                liblo.send(t, 'int', i)
                time.sleep(0.01)
            # for i in range(0,100,10):
            #     liblo.send(t, 'int', i)
            #     time.sleep(0.01)
        for i in range(0,100):
            liblo.send(t, 'int', i)
            time.sleep(0.001)
        return "done"

class displaytest:
    def GET(self):
        killall()
        os.system(CMDTESTDISPLAY+" &")
        return "started"


def get_filepaths(directory, filetypes=MEDIATYPES):
    file_paths = []  # List which will store all of the full filepaths.
    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            for filetype in filetypes:
                # assume a '.'
                typelength = len(filetype)+1
                if filename[-typelength:] == '.'+filetype:
                    # Join the two strings in order to form the full filepath.
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)  # Add it to the list.
    return file_paths  # Self-explanatory.

def make_select_list(name, files, selected=None, multiple=None):
    if multiple:
        html = "<select name='%s' id='%s' size='%s' multiple>\n"%(name,name,len(files))
    else:
        html = "<select name='%s' id='%s'>\n"%(name,name)
    for f in files:
        if f == selected:
            html += "<option value='%s' selected>%s</option>\n"%(f, f)
        else:
            html += "<option value='%s'>%s</option>\n"%(f, f)
    html += "</select>"
    return html

def make_control_list(files, selected=None):
    html = ''
    for f in files:
        if f == selected:
            addclass=' class=media_selected '
        else:
            addclass = ''
        html += "<a href='#' onclick='javascript:media_play(\"%s\")' id='%s' %s>%s</a><br>\n"%(f, f, addclass, f)
    return html

UIDIR=os.path.dirname(os.path.abspath(__file__))
class index:
    def GET(self, file=None):
        # Static files (style sheets, index.html)
        if file:
            if not os.path.exists(file):
                raise web.NotFound()
            elif not os.access(file, os.R_OK):
                raise web.Unauthorized()
            else:
                #print "have file", file
                f = open(UIDIR+'/'+file, 'r')
                return f.read()

        cwd=os.getcwd()

        # GET MEDIA FILE LIST
        os.chdir(MEDIADIR)
        mediafiles = [f[2:] for f in get_filepaths(".", MEDIATYPES)]
        mediafiles.sort()
        os.chdir(cwd)
        # multiple file select for delete file select box:
        mediafilesdelete = make_select_list("delete", mediafiles, None, True)
        mediafilestest = make_select_list("test", mediafiles, None, False)

        # which is current:
        mediacurrent = open(MEDIACONTROLFILE, 'r').read().split()[0]
        if len(mediacurrent)>1 and mediacurrent not in mediafiles:
            mediacurrent = mediafiles[0]
        mediafilescontrol = make_control_list(mediafiles, mediacurrent)
        # set next and previous
        i = mediafiles.index(mediacurrent)
        mediaprevious = mediafiles[(i-1)%len(mediafiles)]
        medianext = mediafiles[(i+1)%len(mediafiles)]

        clientip=web.ctx.env['REMOTE_ADDR']
        serverip=web.ctx.env['HTTP_HOST']

        web.header('Cache-control', 'no-cache, no-store, must-revalidate')
        web.header('Pragma', 'no-cache')
        #web.header('Expires', '0')
        #web.header('Cache-Control', 'post-check=0, pre-check=0', False)
        return """<html><head><title>model: %s</title><meta charset="utf-8">
        <link rel="stylesheet" href="/style.css">
        </head>
        <body>
        <script>
        function http_get(theUrl)
            {
                console.log('get: '+theUrl);
                var xmlHttp = null;
                try {
                        xmlHttp = new XMLHttpRequest();
                        xmlHttp.open( "GET", theUrl, false );
                        xmlHttp.send( null );
                    }
                catch(err) {
                    console.log(err);
                    return null;
                }
                document.getElementById('debug').innerText = 'response: '+xmlHttp.responseText;
                //return JSON.parse(xmlHttp.responseText);
            }
        function media_play(file) {
            //var brightness=parseInt(document.getElementById('brightness').value)
            brightness=localStorage.brightness
            http_get("/media_play?file="+file+"&brightness="+brightness);
            window.location.reload(); // pretty cheap
        }
        function hr_set(offset=0) {
            var hr=parseInt(document.getElementById('hr').value)
            if (offset < 0 || offset > 0) {
                hr += offset
                document.getElementById('hr').value = hr
            }
            http_get('/hr?do=set&hr='+hr+'&brightness='+localStorage.brightness)
        }
        window.onload = function (e) {
            console.log("localStorage", localStorage)
            if (localStorage.brightness) {
                document.getElementById('brightness').value=localStorage.brightness
            }
        }
        </script>

        <style>
        /** { font-size: 10pt; font-family: sans-serif, sans; }*/
        _input, _button, select { font-size: 0.8em; margin: 0px; padding: 0px; }
        select { max-width:300px; background-color: white; border: solid 1px #ccc; border-radius: 0; padding: 0 4; margin: 1 0; outline:0px;
                 -webkit-appearance: none; -moz-appearance: none; appearance: none; }
        #debug {opacity: 0.3;}
        td { padding: 8px 28px; }
        a { text-decoration: none; color: inherit}
        .media_selected { font-weight: bold }
        .media_selected::after { content: ' <-' }
        h2 { text-decoration: underline;}
        button { margin: 2px 3px; font-size: 1.1em;}
        </style>
        <center>Model: %s<br>
        </center>
        <table>

        <td valign=top bgcolor="#eee">
            <h2>Upload Media</h2>
            <form method="POST" enctype="multipart/form-data" action="/upload">
            <input type="file" name="newfile" /><br>
            <input type="submit" value="Upload"/>
            </form>
            <h2>Delete</h2>
            <form method="POST" action="/upload">
            %s
            <br><input type="submit" value="Delete"/>
            </form>

        </td>

        <td valign=top>
            <h2>Control Display</h2>
            <input type=text size=4 id=brightness value=%s onchange='javascript:localStorage.brightness=document.getElementById("brightness").value'> brightness<br>
            <h3>Counter</h3>
            <!-- stop: &#9724; pause: &#9646;&#9646; play: &#9654; record: &#9679; -->
            <button onclick="javascript:http_get('/counter?do=play&brightness='+localStorage.brightness)" class=play>&#9654;</button>
            <button onclick="javascript:http_get('/counter?do=pause')" class=pause>&#9646;&#9646;</button>
            <button onclick="javascript:http_get('/counter?do=stop')" class=pause>&#9724;</button><br>
            <h3>Set Pulse</h3>
            <button onclick="javascript:http_get('/hr?do=start&brightness='+localStorage.brightness)">&#9654;</button>
            <button onclick="javascript:http_get('/hr?do=stop')">&#9724;</button><br>
            <button onclick="javascript:hr_set(1)">+</button><button onclick="javascript:hr_set(-1)">-</button>
<input type=text size=4 id=hr value=60><button onclick="javascript:hr_set()">set</button><br>
            <h3>Media Show</h3>
            <button onclick="javascript:media_play('%s')">&lt;&lt;</button>
            <button onclick="javascript:media_play('%s')">&gt;&gt;</button><br><br>
            <div id=medialist>
            %s
            </div>
        </td>

        </table>
        <br><hr>

        <button onclick="javascript:http_get('/osctest')">osc test</button>
        <button onclick="javascript:http_get('/displaytest')">display test</button>
        <br>
        </center><pre id=debug></pre>
        </body>
        </html>
        """%(MODEL_NAME, MODEL_NAME, mediafilesdelete, BRIGHTNESS, mediaprevious, medianext, mediafilescontrol, ) #"<br>\n".join(soundfiles))

def killall():
    p = subprocess.Popen(['ps', '-x'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    for p in out.splitlines():
        if CMDIMAGE in p or CMDVIDEO in p or \
           CMDCOUNT in p or CMDTESTDISPLAY in p or \
           CMDTEXT in p or 'sleep' in p:
           print ('kill',p)
           pid=int(p.split()[0])
           print ('pid', pid)
           os.kill( int(p.split()[0]), 15) #15=SIGTERM, 9=SIGKILL


class media_play:
    def GET(self):
        input = web.input()
        file = input.file
        global BRIGHTNESS
        if 'brightness' in input and len(input.brightness)>0 and input.brightness != 'undefined':
            BRIGHTNESS = str(min(100, int(input.brightness)))

        print('media_play', file)
        fctl = open(MEDIACONTROLFILE, 'w')
        fctl.write(file)
        fctl.close()

        cwd=os.getcwd()
        os.chdir(MEDIADIR)

        type = file.split('.')[-1]
        if not type or len(type) < 3 or type not in MEDIATYPES:
            raise web.internalerror("Uploaded file invalid media type or file name.")

        if type in MEDIACOUNTER:
            # check if contents of the file are valid arguemtns and if so
            # change the defaults. Mainly check font exists
            if 'counter' in file:
                countargs = CMDCOUNTARGS
                with open(file) as f:
                    newargs = f.read().replace('\n', '').replace('\r', '')
                    if len(newargs) > 0:
                        font = [elm for elm in newargs.split() if '.bdf' in elm]
                        if len(font) > 0 and os.path.exists(font[0]):
                            countargs = newargs
                command = CMDCOUNT
                bright = "-b "+BRIGHTNESS
                args = [command, bright]+MATRIXARGS.split(' ')+countargs.split(' ')
            else:
                command = 'B='+BRIGHTNESS+' '+CMDTEXT
                # MATRIXARGS already contained inside of text.sh
                args = [command]+[file]

        elif type in MEDIAVIDEO:
            command = CMDVIDEO
            bright = "--led-brightness="+BRIGHTNESS
            args = [command,bright]+MATRIXARGS.split(' ')+CMDVIDEOARGS.split(' ')+[file]
        elif type in MEDIAIMAGE:
            command = CMDIMAGE
            bright = "--led-brightness="+BRIGHTNESS
            args = [command,bright]+MATRIXARGS.split(' ')+CMDIMAGEARGS.split(' ')+[file]
        else:
            raise web.internalerror()

        print('exec:', " ".join(args))
        killall()
        os.system(" ".join(args)+" &")
        os.chdir(cwd)
        return "started"

class counter:
    def GET(self):
        input = web.input()
        global BRIGHTNESS
        if 'brightness' in input and len(input.brightness)>0 and input.brightness != 'undefined':
            BRIGHTNESS = str(min(100, int(input.brightness)))
        if input.do == "play":
            # If already running just unpause, else start new
            p = subprocess.Popen(['ps', '-x'], stdout=subprocess.PIPE)
            out, err = p.communicate()
            for p in out.splitlines():
                if CMDCOUNT in p:
                   pid=int(p.split()[0])
                   os.kill( int(p.split()[0]), 12) #10=SIGUSR1, 12=SIGUSR2, 15=SIGTERM, 9=SIGKILL
                   return "unpaused"

            killall()
            command = CMDCOUNT
            bright = "-b "+BRIGHTNESS
            args = [command, bright]+MATRIXARGS.split(' ')+CMDCOUNTARGS.split(' ')
            os.system(" ".join(args)+" &")
            return "started"
        elif input.do == "pause":
            print('counter pause')
            # to we send SIGUSR1 (10) to counter will then pause itself
            p = subprocess.Popen(['ps', '-x'], stdout=subprocess.PIPE)
            out, err = p.communicate()
            for p in out.splitlines():
                if CMDCOUNT in p:
                   pid=int(p.split()[0])
                   os.kill( int(p.split()[0]), 10) #10=SIGUSR1, 15=SIGTERM, 9=SIGKILL
            return "paused"
        elif input.do == "stop":
            print('counter stop')
            killall()
        return "done"


class upload:
    def POST(self):
        x = web.input(newfile={},delete=[])
        # newfile should have type <type 'instance'> if it is not empty
        if 'newfile' in x and type(x.newfile) != dict: # to check if the file-object is created
            filepath=x.newfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(MEDIADIR +'/'+ filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.newfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            fctl = open(MEDIACONTROLFILE, 'w')
            fctl.write(filename)
            fctl.close()
        elif 'delete' in x and len(x['delete']) > 0: # to check if the file-object is created
            cwd=os.getcwd()
            os.chdir(MEDIADIR)
            files = [f[2:] for f in get_filepaths(".", MEDIATYPES)]
            for delitem in x.delete:
                # removed this kind'a secutity check due to problems with deleting unicode/utf8 files
                #if delitem in files:
                if delitem == MEDIADEFAULT:
                    print ("not deleting "+MEDIADEFAULT)
                else:
                    print ("deleting", delitem, os.getcwd())
                    os.remove(delitem)
            os.chdir(cwd)
        elif 'test' in x and len(x['test']) > 0: # to check if the file-object is created
            print ("test image:",x.test)
            fctl = open(MEDIACONTROLFILE, 'w')
            fctl.write(x.test)
            fctl.close()
        raise web.seeother('/')

class Help:
    def GET(self):
        return """
            <html><head><title>model: %s</title><meta charset="utf-8">
            <link rel="stylesheet" href="/style.css">
            </head><body>
            Uploaded files (media files) that have the file name ending of .txt
            will cause the counter to be started or text to be shown.
            </body></html>"""



try:
    from html import escape  # python 3.x
except ImportError:
    from cgi import escape  # python 2.x

if __name__ == "__main__":
    os.setpgrp() # child procs will be in proc group. when we die they do
    try:
        app.run()
    finally:
        os.killpg(0, signal.SIGTERM)
