# -*- coding: utf-8 -*-
"""Network Manager gtk windows module


BaseWindow - Base window for network_manager_gtk
EditWindow - Edit Settings Window
NewConnectionWindow - show new connections as a list
NewConnectionEditWindow - new connection settings window

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

import gtk
import gobject

from network_manager_gtk.translation import _

from network_manager_gtk.widgets import ProfilesHolder

from network_manager_gtk.widgets import ProfileFrame
from network_manager_gtk.widgets import NetworkFrame
from network_manager_gtk.widgets import NameServerFrame
from network_manager_gtk.widgets import WirelessFrame

from network_manager_gtk.widgets import NewWifiConnectionItem
from network_manager_gtk.widgets import NewEthernetConnectionItem

class BaseWindow(gtk.Window):
    """BaseWindow for network_manager_gtk
    """

    def __init__(self, iface):
        """init

        Arguments:
        - `iface`:
        """
        gtk.Window.__init__(self)
        self.iface = iface
        self._set_style()
        self._create_ui()
        self._listen_signals()
    def _set_style(self):
        """sets title and default size etc.
        """
        pass
    def _create_ui(self):
        """creates ui elements
        """
        pass
    def _listen_signals(self):
        """listens signals
        """
        pass

gobject.type_register(BaseWindow)

class EditWindow(BaseWindow):
    """Edit Window
    """

    def __init__(self, iface, package, connection,
                 device_id=None):
        """init

        Arguments:
        - `iface`: backend.NetworkIface
        - `package`: package name
        - `connection`: connection name (can be 'new')
        """
        self._package = package
        self._connection = connection
        self._device_id = device_id
        self.is_wireless = False
        if self._package == "wireless_tools":
            self.is_wireless = True
        BaseWindow.__init__(self, iface)
    def _set_style(self):
        """sets title and default size
        """
        self.set_title(_("Edit Connection"))
        self.set_modal(True)
        if self.is_wireless:
            self.set_default_size(644, 400)
        else:
            self.set_default_size(483, 300)
    def _create_ui(self):
        self.data = ""
        self._is_new = self._connection == "new"
        if not self._is_new:
            self.data = self.iface.info(self._package,
                                        self._connection)
            self.is_up = self.data["state"][0:2] == "up"
        else:
            dname = self.iface.devices(self._package)[self._device_id]
            self.data = {"name":"",
                         "device_id":self._device_id,
                         "device_name":dname,
                         "net_mode":"auto",
                         "name_mode":"default"}
            self.is_up = False
        vbox = gtk.VBox(homogeneous=False,
                        spacing=6)
        self.add(vbox)

        self.pf = ProfileFrame(self.data)
        vbox.pack_start(self.pf, expand=False, fill=False)

        if self.is_wireless:
            self.wf = WirelessFrame(self.data, self.iface,
                                    package=self._package,
                                    connection=self._connection,
                                    with_list=True,
                                    is_new=self._is_new)
            vbox.pack_start(self.wf, expand=True, fill=True)
            self.wf.show()

        self.nf = NetworkFrame(self.data)
        vbox.pack_start(self.nf, expand=False, fill=False)

        self.nsf = NameServerFrame(self.data)
        vbox.pack_start(self.nsf, expand=False, fill=False)
        self.nsf.show()

        buttons = gtk.HBox(homogeneous=False,
                           spacing=6)
        self.apply_btn = gtk.Button(_("Apply"))
        self.cancel_btn = gtk.Button(_("Cancel"))
        buttons.pack_end(self.apply_btn, expand=False, fill=False)
        buttons.pack_end(self.cancel_btn, expand=False, fill=False)
        buttons.show_all()
        vbox.pack_end(buttons, expand=False, fill=False)
        vbox.show()
    def _listen_signals(self):
        self.apply_btn.connect("clicked", self.apply)
        self.cancel_btn.connect("clicked", self.cancel)
    def cancel(self, widget):
        self.destroy()
    def apply(self, widget):
        data = self.collect_data()
        try:
            self.iface.updateConnection(self._package,
                                        data["name"],
                                        data)
        except Exception, e:
            print "Exception:", unicode(e)
        if not self._is_new:
            if not self.data["name"] == data["name"]:
                self.iface.deleteConnection(self._package,
                                            self.data["name"])
            if self.is_up:
                self.iface.connect(self._package, data["name"])
        self.destroy()
    def collect_data(self):
        data = {}
        self.pf.collect_data(data)
        self.nf.collect_data(data)
        self.nsf.collect_data(data)
        if self.is_wireless: self.wf.collect_data(data)
        return data

gobject.type_register(EditWindow)

class NewConnectionWindow(BaseWindow):
    """show new connections as a list"""

    def __init__(self, iface):
        """init
        Arguments:
        - `iface`: NetworkIface
        """
        self._cons = [] #connections
        BaseWindow.__init__(self, iface)
    def _set_style(self):
        self.set_title(_("New Connection"))
        self.set_default_size(483, 300)
    def _create_ui(self):
        """creates ui
        """
        self._ui = gtk.VBox(homogeneous=False,
                            spacing=10)
        self.add(self._ui)
        self._ui.show()

        self._refresh_btn = gtk.Button("")
        self._ui.pack_start(self._refresh_btn,
                            expand=False)
        self._refresh_btn.show()

        self._list= gtk.VBox(homogeneous=True,
                             spacing=5)
        self._ui.pack_start(self._list,
                            expand=False,
                            fill=False)
        self._list.show_all()

        self._show_list([]) #show none wireless connections
        self.scan()
    def _listen_signals(self):
        self._refresh_btn.connect("clicked", self.scan)
    def _set_scanning(self, status):
        """disable/enable refresh btn
        Arguments:
        - `status`: if True then disable button
        """
        if status:
            self._refresh_btn.set_label(_("Refreshing..."))
        else:
            self._refresh_btn.set_label(_("Refresh"))
        self._refresh_btn.set_sensitive(not status)
    def scan(self, widget=None):
        """scan for wifi networks
        """
        #if user have wireless support
        if self.get_devices("wireless_tools"):
            self._set_scanning(True)
            #TODO:more than one device support
            d = self.get_devices("wireless_tools")[0]
            self.iface.scanRemote(d, "wireless_tools",
                                  self._scan_callback)
    def get_devices(self, package):
        """returns devices of package
        """
        return self.iface.devices(package).keys()
    def _scan_callback(self, package, exception, args):
        """wifi scan callback

        Arguments:
        - `package`: package name
        - `exception`: exception
        - `args`: connection array
        """
        self._set_scanning(False)
        if not exception:
            self._show_list(args[0])
        else:
            print exception
    def create_new(self, widget, data):
        NewConnectionEditWindow(self.iface,
                                data["package"],
                                data["device"],
                                data["connection"]).show()
    def _show_list(self, connections):
        """show list

        Arguments:
        - `connections`: wireless connections array
        """
        methods = self.iface.authMethods("wireless_tools")
        def get_type(x):
            for name, desc in methods:
                if name == x:
                    return desc
        #remove old ones
        map(self._list.remove, self._cons)
        self._cons = []
        #add new ones
        ##ethernet
        for device in self.get_devices("net_tools"):
            name = self.iface.devices("net_tools")[device]
            self.add_to_list(NewEthernetConnectionItem(device,
                                                       name))
        ##wireless
        device_id = self.get_devices("wireless_tools")[0]
        for connection in connections:
            encryption = get_type(connection["encryption"])
            self.add_to_list(NewWifiConnectionItem(device_id,
                                                   connection,
                                                   encryption))
        self._list.show_all()
    def add_to_list(self, item):
        """add connection item to list
        - `item`: connection item
        """
        self._list.pack_start(item,
                              expand=False,
                              fill=False)
        self._cons.append(item)
        item.on_connect(self.create_new)

gobject.type_register(NewConnectionWindow)

class NewConnectionEditWindow(BaseWindow):
    """New Connection Settings Window"""
    def __init__(self, iface,
                 package, device, data):
        self.package = package
        self.data = data
        self.device = device
        BaseWindow.__init__(self, iface)
    def _set_style(self):
        self.set_title(_("Save Profile"))
        self.set_default_size(483, 300)
    def _create_ui(self):
        dname = self.iface.devices(self.package)[self.device]
        new_data = {"name":_("New Profile"),
                    "device_id":self.device,
                    "device_name":dname,
                    "net_mode":"auto",
                    "name_mode":"default"}
        vbox = gtk.VBox(homogeneous=False,
                        spacing=5)
        self.add(vbox)

        self.pf = ProfileFrame(new_data)
        vbox.pack_start(self.pf, expand=False, fill=False)
        self.pf.show()
        if self.package == "wireless_tools":
            new_data["remote"] = self.data["remote"]
            _type = self.data["encryption"]
            self.wf = WirelessFrame(new_data,
                                    self.iface,
                                    package=self.package,
                                    connection="new",
                                    is_new=True,
                                    with_list=False,
                                    select_type=_type)
            vbox.pack_start(self.wf, expand=False, fill=False)
            self.wf.show()

        self.expander = gtk.Expander(_("Other Settings"))
        self.expander.set_expanded(False)
        vbox2 = gtk.VBox()
        self.expander.add(vbox2)
        vbox.pack_start(self.expander, expand=False, fill=False)
        self.expander.show()

        self.nf = NetworkFrame(new_data)
        vbox2.pack_start(self.nf, expand=False, fill=False)
        self.nf.show()

        self.nsf = NameServerFrame(new_data)
        vbox2.pack_start(self.nsf, expand=False, fill=False)
        self.nsf.show()

        vbox2.show()

        buttons = gtk.HBox(homogeneous=False,
                           spacing=6)
        self.save_btn = gtk.Button(_("Save"))
        self.save_and_connect_btn = gtk.Button(_("Save & Connect"))
        self.cancel_btn = gtk.Button(_("Cancel"))
        buttons.pack_end(self.save_and_connect_btn,
                         expand=False, fill=False)
        buttons.pack_end(self.save_btn, expand=False, fill=False)
        buttons.pack_end(self.cancel_btn, expand=False, fill=False)
        buttons.show_all()
        vbox.pack_end(buttons, expand=False, fill=False)
        vbox.show()
    def _listen_signals(self):
        self.save_and_connect_btn.connect("clicked", self.save, True)
        self.save_btn.connect("clicked", self.save, False)
        self.cancel_btn.connect("clicked", self.cancel)
    def cancel(self, widget):
        self.destroy()
    def save(self, widget, to_connect):
        data = self.collect_data()
        try:
            self.iface.updateConnection(self.package,
                                        data["name"],
                                        data)
        except Exception, e:
            print "Exception:", unicode(e)
        if to_connect:
            self.iface.connect(self.package, data["name"])
        self.destroy()
    def collect_data(self):
        data = {}
        self.pf.collect_data(data)
        self.nf.collect_data(data)
        self.nsf.collect_data(data)
        if self.package == "wireless_tools":
            self.wf.collect_data(data)
        return data
