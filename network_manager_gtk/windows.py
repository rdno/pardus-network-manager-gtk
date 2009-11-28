#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Network Manager gtk windows module

MainWindow - Main Window
EditWindow - Edit Settings Window
NewWindow - New Profile Window
NewEditWindow - heyya

"""

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

import gtk

from network_manager_gtk.translation import _

from network_manager_gtk.widgets import ProfilesHolder

class MainWindow(gtk.Window):
    """Main Window
    profile list
    """

    def __init__(self, iface):
        """init MainWindow

        Arguments:
        - `iface`: backend.NetworkIface
        """
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.iface = iface
        self.get_state = lambda p,c:self.iface.info(p,c)[u"state"]
        self._set_style()
        self._create_ui()
        self._listen_signals()
        self._get_profiles()
    def _set_style(self):
        """sets title and defualt size
        """
        self.set_title = _("Network Manager")
        self.set_default_size(400, 300)
    def _create_ui(self):
        """creates ui elements
        """
        self._vbox = gtk.VBox()
        self.add(self._vbox)

        self._new_btn = gtk.Button(_('New Connection'))
        self._vbox.pack_start(self._new_btn, expand=False)

        self._holder = ProfilesHolder()
        self._holder.set_connection_signal(self._connection_callback)
        self._vbox.pack_start(self._holder)
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
            pass
        else:
            m = _("Do you wanna delete the connection  '%s' ?") % \
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
        """listen some signals
        """
        self.connect("destroy", gtk.main_quit)
        self.iface.listen(self._listen_comar)
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
        """get profiles from iface
        """
        for package in self.iface.packages():
            for connection in self.iface.connections(package):
                state = self.get_state(package, connection)
                self._holder.add_profile(package,
                                         connection,
                                         state)
