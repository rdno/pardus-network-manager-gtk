# -*- coding: utf-8 -*-
"""NetworkManager gtk Main Module

NetworkManager - Network Manager gtk's main widget

"""
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

__all__ = ["backend", "translation", "widgets", "windows",
           "NetworkManager"]

import gtk
import gobject

from dbus.mainloop.glib import DBusGMainLoop

from network_manager_gtk.backend import NetworkIface
from network_manager_gtk.translation import _
from network_manager_gtk.widgets import ProfilesHolder
from network_manager_gtk.windows import EditWindow
from network_manager_gtk.windows import NewConnectionWindow

class NetworkManager(gtk.VBox):
    """Network Manager gtk's main widget"""
    def __init__(self):
        """init"""
        gtk.VBox.__init__(self, homogeneous=False, spacing=5)
        self._dbus_loop()
        self.iface = NetworkIface()
        self.get_state = lambda p,c:self.iface.info(p,c)[u"state"]
        self._create_ui()
        self._listen_signals()
    def _dbus_loop(self):
        #runs dbus main loop
        DBusGMainLoop(set_as_default=True)
    def _create_ui(self):
        #creates ui elements
        self._new_btn = gtk.Button(_('New Connection'))
        self.pack_start(self._new_btn, expand=False)

        self._holder = ProfilesHolder()
        self._holder.set_connection_signal(self._connection_callback)
        self.pack_start(self._holder, expand=True, fill=True)
        self._get_profiles()
    def _connection_callback(self, widget, data):
        """listens ConnectionWidget's signals

        Arguments:
        - `widget`: widget
        - `data`: {'action':(toggle | edit | delete)
                   'package':package_name,
                   'connection':connection_name}
        """
        action = data["action"]
        if action == "toggle":
            self.iface.toggle(data["package"],
                              data["connection"])
        elif action == "edit":
            EditWindow(self.iface,
                       data["package"],
                       data["connection"]).show()
        else:
            m = _("Do you want to delete the connection  '%s' ?") % \
                data['connection']
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_WARNING,
                                       buttons=gtk.BUTTONS_YES_NO,
                                       message_format=m)
            response = dialog.run()
            if response == gtk.RESPONSE_YES:
                try:
                    self.iface.deleteConnection(data['package'],
                                                data['connection'])
                except Exception, e:
                    print "Exception:",e
            dialog.destroy()
    def _listen_signals(self):
        """listen some signals"""
        self._new_btn.connect("clicked", self.new_profile)
        self.iface.listen(self._listen_comar)
    def new_profile(self, widget):
        #TODO: classic mode support
        self.classic = False
        if self.classic:
            device = self.iface.devices("wireless_tools").keys()[0]
            EditWindow(self.iface,"wireless_tools", "new",
                       device_id=device)
        else:
            NewConnectionWindow(self.iface).show()
    def _listen_comar(self, package, signal, args):
        """comar listener

        Arguments:
        - `package`: package
        - `signal`: signal type
        - `args`:   arguments
        """
        args = map(lambda x: unicode(x), list(args))
        if signal == "stateChanged":
            self._holder.update_profile(package,
                                        args[0],
                                        args[1:])
        elif signal == "deviceChanged":
            print "TODO:Listen comar signal deviceChanged "
        elif signal == "connectionChanged":
            if args[0] == u"changed":
                pass#Nothing to do ?
            elif args[0] == u"added":
                self._holder.add_profile(package,
                                         args[1],
                                         self.get_state(package,
                                                        args[1]))
            elif args[0] == u"deleted":
                self._holder.remove_profile(package,
                                            args[1])
    def _get_profiles(self):
        """get profiles from iface"""
        for package in self.iface.packages():
            for connection in self.iface.connections(package):
                state = self.get_state(package, connection)
                self._holder.add_profile(package,
                                         connection,
                                         state)
