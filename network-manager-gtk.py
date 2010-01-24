#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Rıdvan Örsvuran (C) 2009, 2010
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

import pygtk
pygtk.require('2.0')
import gtk

from network_manager_gtk import NetworkManager
from network_manager_gtk.translation import _
from network_manager_gtk.windows import BaseWindow

class MainWindow(BaseWindow):
    """Standalone window for network_manager_gtk"""
    def __init__(self):
        """init"""
        self.manager = NetworkManager()
        BaseWindow.__init__(self, None)
    def _set_style(self):
        self.set_title(_("Network Manager"))
        self.set_default_size(483, 300)
    def _create_ui(self):
        self.add(self.manager)
    def _listen_signals(self):
        self.connect("destroy", gtk.main_quit)
    def run(self, args):
        """Runs the program with args

        Arguments:
        - `argv`: sys.argv
        """
        self.show_all()
        gtk.main()

if __name__ == "__main__":
    import sys
    MainWindow().run(sys.argv)
