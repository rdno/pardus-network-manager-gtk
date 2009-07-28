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
    os.system("intltool-extract --type=gettext/glade ui/main.glade")
    os.system("xgettext --language=Python --keyword=_ --keyword=N_ --output=network_manager_gtk.pot main.py ui/main.glade.h")

def help():
    print """make pot: makes .pot
make mo : makes .mo"""
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "mo":
            mo()
        elif sys.argv[1] == "pot":
            pot()
        else:
            help()
    else:
        help()
