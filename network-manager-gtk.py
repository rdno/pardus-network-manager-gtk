#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Rıdvan Örsvuran (C) 2009
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os

import pygtk
pygtk.require('2.0')
import gtk

from network_manager_gtk.backend import NetworkIface

from network_manager_gtk.windows import MainWindow


class Base(object):
    def __init__(self):
        self._dbusMainLoop()
        self.iface = NetworkIface()
        self.window = MainWindow(self.iface)

    def _dbusMainLoop(self):
        from dbus.mainloop.glib import DBusGMainLoop
        DBusGMainLoop(set_as_default = True)

    def run(self, argv=None):
        """Runs the program
        Arguments:
        - `argv`: sys.argv
        """
        self.window.show_all()
        gtk.main()

if __name__ == "__main__":
    import sys
    app = Base()
    app.run(sys.argv)
