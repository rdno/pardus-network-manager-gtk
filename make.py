#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Rıdvan Örsvuran (C) 2009
import os
import sys
LANGS = ["en", "tr"]
def mo():
    for lang in LANGS:
        os.system("mkdir -p locale/%s/LC_MESSAGES" % lang)
        os.system("msgfmt --output-file=locale/%s/LC_MESSAGES/network_manager_gtk.mo po/%s.po" % (lang, lang))
def pot():
    glade_extract("main.glade")
    glade_extract("edit.glade")
    xgettext_cmd = "xgettext --keyword=_ --keyword=N_"
    os.system("%s -f %s --output=%s" % (xgettext_cmd,
                                        "po/POTFILES.in",
                                        "po/network_manager_gtk.pot"))
def tags():
    os.system("etags network-manager-gtk.py network_manager_gtk/*.py")

def glade_extract(file):
    """intltool-extract glade file to .h
    Arguments:
    - `file`:glade file name
    """
    os.system("intltool-extract --type=gettext/glade ui/"+file)

def help():
    print """make pot : makes .pot
make mo  : makes .mo files
make tags: makes TAGS (emacs) file"""
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "mo":
            mo()
        elif sys.argv[1] == "pot":
            pot()
        elif sys.argv[1] == "tags":
            tags()
        else:
            help()
    else:
        help()
