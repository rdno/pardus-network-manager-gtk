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

import gettext
import locale
import os

import pygtk
pygtk.require('2.0')
import gtk, gobject

from backend import NetworkIface


APP_NAME="network_manager_gtk"
LOCALE_DIR= "locale"
trans = gettext.translation(APP_NAME, LOCALE_DIR, fallback=True)
_ = trans.ugettext
from gtk import glade
glade.bindtextdomain(APP_NAME, LOCALE_DIR)
glade.textdomain(APP_NAME)


class ConnectionWidget(gtk.Table):
    """A special widget contains connection related stuff
    """
    def __init__(self, package_name, connection_name, state=None):
        """init
        Arguments:
        - `package_name`: package of this (like wireless_tools)
        - `connection_name`: user's connection name
        - `state`: connection state
        """
        gtk.Table.__init__(self, rows=2, columns=3)
        self._package_name = package_name
        self._connection_name = connection_name
        self._state = state
        self._createUI()
    def _createUI(self):
        """creates UI
        """
        self.check_btn = gtk.CheckButton()
        self._label = gtk.Label(self._connection_name)
        self._info = gtk.Label(self._state)
        self._label.set_alignment(0.0, 0.5)
        self._info.set_alignment(0.0, 0.5)
        self.edit_btn = gtk.Button(_('Edit'))
        self.attach(self.check_btn, 0, 1, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self._label, 1 , 2, 0, 1,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._info, 1 , 2, 1, 2,
                    gtk.EXPAND|gtk.FILL,  gtk.SHRINK)
        self.attach(self.edit_btn, 2, 3, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.setMode(self._state.split(' '))
    def setMode(self, args):
        """sets _info label text
        and is _on or not
        Arguments:
        - `args`: state, detail
        """
        detail = ""
        if len(args) > 1:
            detail = args[1]
        states = {"down"        : _("Disconnected"),
                  "up"          : _("Connected"),
                  "connecting"  : _("Connecting"),
                  "inaccessible": detail,
                  "unplugged"   : _("Cable or device is unplugged.")}

        if args[0] != "up":
            self.check_btn.set_active(False)
            self._info.set_text(states[args[0]])
        else:
            self.check_btn.set_active(True)
            self._info.set_markup('<span color="green">'+
                                  args[1]+
                                  '</span>')
    def connectSignals(self, click_signal, edit_signal):
        """connect widgets signals
        Arguments:
        - `click_signal`:
        - `edit_signal`:
        """
        self.check_btn.connect("pressed", click_signal,
                              {"package":self._package_name,
                               "connection":self._connection_name})
        self.edit_btn.connect("clicked", edit_signal,
                              {"package":self._package_name,
                               "connection":self._connection_name})

gobject.type_register(ConnectionWidget)

class Base(object):
    def __init__(self):
        self._dbusMainLoop()
        self.iface = NetworkIface()
        #ui
        ui = glade.XML("ui/main.glade")
        ui.signal_connect("on_window_main_destroy", gtk.main_quit)
        self.window = ui.get_widget("window_main")
        # show connection as Widgets
        self.widgets = {}
        self.showConnections()
        self.holder = ui.get_widget("holder")
        self.holder.add_with_viewport(self.vbox)
        # listen for changes
        self.iface.listen(self._listener)

    def _onConnectionClicked(self, widget, callback_data):
        self.iface.toggle(callback_data['package'],
                          callback_data['connection'])
    def _onConnectionEdit(self, widget, callback_data):
        print "TODO"

    def showConnections(self):
        """show connection on gui
        """
        self.vbox = gtk.VBox(homogeneous=False, spacing=10)
        for package in self.iface.packages():
            self.widgets[package] = {}
            for connection in self.iface.connections(package):
                state = self.iface.info(package, connection)[u"state"]
                con_wg = ConnectionWidget(package,
                                          connection,
                                          state)
                con_wg.connectSignals(self._onConnectionClicked,
                                      self._onConnectionEdit)
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
            print "TODO:Listen comar signal connectionChanged"

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
