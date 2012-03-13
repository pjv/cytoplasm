# -*- coding: utf-8 -*-
''' These are the things that are used when you `cytoplasm serve`.
'''

import os
import sys
import cytoplasm


# make this work in either Python 2.x or 3.x
if sys.version_info.major >= 3:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
else:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer


# keep track of when things were last built in this global variable
most_recent_time = 0
# keep track of the site in this global variable
site = None


def serve(port, rebuild, event=None):
    "Serve the Cytoplasm site."
    # keep track of the most recently modified time in global variable
    # most_recent_time
    global most_recent_time
    global site
    # create a site and rebuild it first.
    site = cytoplasm.Site(".")
    site.build()
    # set the most recent time.
    most_recent_time = most_recent()
    # change to the build directory, where things are to be served from.
    os.chdir(site.config.build_dir)
    # use either SimpleHTTPRequestHandler or RebuildHandler, depending on
    # whether rebuild is True.
    if rebuild:
        handler = RebuildHandler
    else:
        handler = SimpleHTTPRequestHandler
    # make a server with the handler and the port
    httpd = HTTPServer(('', port), handler)
    # serve!
    httpd.serve_forever()


def most_recent():
    """Determine the most recent modified time in the source directory,
    ignoring dotfiles and _build.
    """
    directory = site.source
    build_dir = site.config.build_dir
    #get the candidate files:
    files = [f for f in os.listdir(directory) if f != build_dir and not
            f.startswith(".")]
    # append files in additional watch directories
    if site.config.watch_dirs:
        for dir in site.config.watch_dirs:
            files += [os.path.join(dir, f) for f in 
            os.listdir(os.path.join(directory, dir)) if not f.startswith(".")]
    # get each of their times
    times = [os.stat(os.path.join(directory, f)).st_mtime for f in files]
    # the highest time here is the most recent; return that.
    return max(times)


class RebuildHandler(SimpleHTTPRequestHandler):
    def handle(self):
        "Handle a request and, if anything has changed, rebuild the site."
        # overwrite the handle method in SimpleHTTPRequestHandler with this.
        # declare most_recent_time global; we'll be changing it later.
        global most_recent_time
        # figure out the most recent time edited in the source directory
        new_recent = most_recent()
        # only build the site if the new most recent is more recent than the
        # old one, i.e. if one or more of the files has been edited.
        if new_recent > most_recent_time:
            # update most_recent_time
            most_recent_time = new_recent
            # Build the site from the source directory
            print("Rebuilding your Cytoplasm site...")
            site.build()
        # Call SimpleHTTPRequestHandler.handle(), so it can do stuff there too.
        SimpleHTTPRequestHandler.handle(self)
