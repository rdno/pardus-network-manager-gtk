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
import gobject

from network_manager_gtk.backend import NetworkIface

from network_manager_gtk.widgets import ConnectionWidget
from network_manager_gtk.widgets import MainInterface
from network_manager_gtk.widgets import EditInterface

from network_manager_gtk.translation import _

class Base(object):
    def __init__(self):
        self._dbusMainLoop()
        self.iface = NetworkIface()
        #ui
        self.main = MainInterface()
        self.window = self.main.getWindow()
        # show connection as Widgets
        self.widgets = {}
        self.showConnections()
        self.holder = self.main.getHolder()
        self.holder.add_with_viewport(self.vbox)
        # listen for changes
        self.iface.listen(self._listener)

    def _onConnectionClicked(self, widget, callback_data):
        self.iface.toggle(callback_data['package'],
                          callback_data['connection'])
    def _onConnectionEdit(self, widget, callback_data):
        try:
            a = EditInterface(callback_data['package'],
                              callback_data['connection'])
            a.getWindow().props.modal = True
            a.getWindow().show()
        except Exception, e:
            print "Exception:", e
    def _onConnectionDelete(self, widget, callback_data):
        message = _("Do you wanna delete the connection '%s' ? " % \
                    callback_data["connection"])
        dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                   buttons=gtk.BUTTONS_YES_NO,
                                   message_format=message)
        response = dialog.run()
        if response == gtk.RESPONSE_YES:
            try:
                self.iface.deleteConnection(callback_data['package'],
                                            callback_data['connection'])
            except Exception, e:
                print "Exception:",e
        dialog.destroy()
    def showConnections(self):
        """show connection on gui
        """
        self.vbox = gtk.VBox(homogeneous=False, spacing=10)
        for package in self.iface.packages():
            self.widgets[package] = {}
            for connection in self.iface.connections(package):
               self.add_to_vbox(package, connection)
    def add_to_vbox(self, package, connection):
        state = self.iface.info(package, connection)[u"state"]
        con_wg = ConnectionWidget(package,
                                  connection,
                                  state)
        con_wg.connectSignals(self._onConnectionClicked,
                              self._onConnectionEdit,
                              self._onConnectionDelete)
        self.vbox.pack_start(con_wg, expand=False, fill=False)
        self.widgets[package][connection] = con_wg
    def _listener(self, package, signal, args):
        """comar listener
        Arguments:
        - `package`: package of item
        - `signal`: comar signal type
        - `args`: arguments
        """
        args = map(lambda x: unicode(x), list(args))
        if signal == "stateChanged":
            self.widgets[package][args[0]].setMode(args[1:])
        elif signal == "deviceChanged":
            print "TODO:Listen comar signal deviceChanged "
        elif signal == "connectionChanged":
            if args[0] == u"changed":
                pass#Nothing to do ?
            elif args[0] == u"added":
                self.add_to_vbox(package, args[1])
                self.vbox.show_all()
            elif args[0] == u"deleted":
                self.vbox.remove(self.widgets[package][args[1]])
                pass

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
