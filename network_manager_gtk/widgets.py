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

from translation import _, bind_glade_domain
from backend import NetworkIface

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gtk import glade

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
        gtk.Table.__init__(self, rows=2, columns=4)
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
        self.delete_btn = gtk.Button(_('Delete'))
        self.attach(self.check_btn, 0, 1, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self._label, 1 , 2, 0, 1,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._info, 1 , 2, 1, 2,
                    gtk.EXPAND|gtk.FILL,  gtk.SHRINK)
        self.attach(self.edit_btn, 2, 3, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self.delete_btn, 3, 4, 0, 2,
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
    def connectSignals(self, click_signal, edit_signal, delete_signal):
        """connect widgets signals
        Arguments:
        - `click_signal`: toggle connection signal
        - `edit_signal`:  edit signal
        - `delete_signal`: delete signal
        """
        self.check_btn.connect("pressed", click_signal,
                              {"package":self._package_name,
                               "connection":self._connection_name})
        self.edit_btn.connect("clicked", edit_signal,
                              {"package":self._package_name,
                               "connection":self._connection_name})
        self.delete_btn.connect("clicked", delete_signal,
                              {"package":self._package_name,
                               "connection":self._connection_name})

gobject.type_register(ConnectionWidget)

class MainInterface(object):
    """Imports main window glade
    """

    def __init__(self):
        """import glade
        """
        bind_glade_domain()
        self._xml = glade.XML("ui/main.glade")
        self._xml.signal_connect("on_window_main_destroy",
                                gtk.main_quit)
        self._window = self._xml.get_widget("window_main")
        self._holder = self._xml.get_widget("holder")
    def getWindow(self):
        """returns window
        """
        return self._window
    def getHolder(self):
        """returns holder
        """
        return self._holder

class EditInterface(object):
    """Imports edit window glade
    """

    def __init__(self, package, connection):
        """init
        Arguments:
        - `package`:
        - `connection`:
        """
        bind_glade_domain()
        self.iface = NetworkIface()
        self._package = package
        self._connection = connection
        self._xml = glade.XML("ui/edit.glade")
        self.getWidgets()
        self.listenSignals()
        self.insertData()

        # is wireless ?
        if self._package != "wireless_tools":
            self._wifi.hide()
    def on_net_changed(self, widget):
        if widget is self._dhcp_rb:
            self.setManualNetwork(False)
        else:
            self.setManualNetwork(True)
    def on_ns_changed(self, widget):
        if widget is self._ns_custom:
            self.setCustomNameServer(True)
        else:
            self.setCustomNameServer(False)
    def listenSignals(self):
        self._xml.signal_connect("on_dhcp_rb_clicked",
                                 self.on_net_changed)
        self._xml.signal_connect("on_manual_rb_clicked",
                                 self.on_net_changed)
        self._xml.signal_connect("on_ns_default_rb_clicked",
                                 self.on_ns_changed)
        self._xml.signal_connect("on_ns_custom_rb_clicked",
                                 self.on_ns_changed)
        self._xml.signal_connect("on_ns_auto_rb_clicked",
                                 self.on_ns_changed)
    def getWidgets(self):
        get  = self._xml.get_widget
        self._wifi = get("wireless_frame")
        self._window = get("window_edit")
        #Profile Frame
        self._profiletxt = get("profilename")
        self._devicename = get("device_name_label")
        #Network Settings Frame
        self._dhcp_rb = get("dhcp_rb")
        self._manual_rb = get("manual_rb")
        self._address = get("address")
        self._address_lb = get("address_lb")
        self._networkmask = get("networkmask")
        self._networkmask_lb = get("networkmask_lb")
        self._gateway = get("gateway")
        self._gateway_lb = get("gateway_lb")
        #Name Servers Frame
        self._ns_custom = get("ns_custom_rb")
        self._ns_default = get("ns_default_rb")
        self._ns_auto = get("ns_auto_rb")
        self._ns_custom_txt = get("ns_custom_text")

    def setManualNetwork(self, state):
        self._address.set_sensitive(state)
        self._address_lb.set_sensitive(state)
        self._networkmask.set_sensitive(state)
        self._networkmask_lb.set_sensitive(state)
        self._gateway.set_sensitive(state)
        self._gateway_lb.set_sensitive(state)
    def setCustomNameServer(self, state):
        self._ns_custom_txt.set_sensitive(state)

    def insertData(self):
        """show preferences
        """
        data = self.iface.info(self._package,
                               self._connection)
        #Profile Frame
        self._profiletxt.set_text(data[u"name"])
        self.if_available_set(data, "device_name",
                              self._devicename.set_text)
        #TODO:more than one device support

        #Network Settings Frame
        if data.has_key("net_mode"):
            if data["net_mode"] == "auto":
                self._dhcp_rb.set_active(True)
                self.setManualNetwork(False)
            else:
                self._manual_rb.set_active(False)
                self.setManualNetwork(True)

        self.if_available_set(data, "net_address",
                              self._address.set_text)
        self.if_available_set(data, "net_mask",
                              self._networkmask.set_text)
        self.if_available_set(data, "net_gateway",
                              self._gateway.set_text)

        #Name Servers Frame
        if data.has_key("name_mode"):
            if data["name_mode"] == "default":
                self._ns_default.set_active(True)
                self.setCustomNameServer(False)
            elif data["name_mode"] == "auto":
                self._ns_auto.set_active(True)
                self.setCustomNameServer(False)
            elif data["name_mode"] == "custom":
                self._ns_custom.set_active(True)
                self.setCustomNameServer(True)
        self.if_available_set(data, "name_server",
                              self._ns_custom_txt.set_text)
        print data

    def if_available_set(self, data, key, method):
        if data.has_key(key):
            method(data[key])

    def getWindow(self):
        """returns window
        """
        return self._window

