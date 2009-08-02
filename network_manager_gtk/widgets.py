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
        self.get  = self._xml.get_widget
        self.listenSignals()
        self.insertData()

        # is wireless ?
        if self._package != "wireless_tools":
            self.get("wireless_frame").hide()
    def on_net_changed(self, widget):
        if widget is self.get("dhcp_rb"):
            self.setManualNetwork(False)
        else:
            self.setManualNetwork(True)
    def on_ns_changed(self, widget):
        if widget is self.get("ns_custom_rb"):
            self.setCustomNameServer(True)
        else:
            self.setCustomNameServer(False)
    def on_changepass(self, widget):
        self.show_password(True)
        authType = self.iface.authType(self._package,
                                       self._connection)
        authInfo = self.iface.authInfo(self._package,
                                       self._connection)
        authParams = self.iface.authParameters(self._package,
                                               authType)
        if len(authParams) == 1:
            password = authInfo.values()[0]
            self.get("pass_text").set_text(password)
            self.get("hidepass_cb").set_active(True)
        elif len(authParams) > 1:
            print "TODO:learn what is securityDialog"
            print "--> at svn-24515 / base.py line:474\n"
    def on_hidepass(self, widget):
        visibility = not widget.get_active()
        self.get("pass_text").set_visibility(visibility)
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
        self._xml.signal_connect("on_changepass_btn_clicked",
                                 self.on_changepass)
        self._xml.signal_connect("on_hidepass_cb_toggled",
                                 self.on_hidepass)

    def setSecurityTypesStyle(self):
        ##Security Type ComboBox
        model = gtk.ListStore(str)
        security_types = self.get("security_types")
        security_types.set_model(model)
        cell = gtk.CellRendererText()
        security_types.pack_start(cell)
        security_types.add_attribute(cell,'text',0)

    def setManualNetwork(self, state):
        self.get("address").set_sensitive(state)
        self.get("address_lb").set_sensitive(state)
        self.get("networkmask").set_sensitive(state)
        self.get("networkmask_lb").set_sensitive(state)
        self.get("gateway").set_sensitive(state)
        self.get("gateway_lb").set_sensitive(state)
    def setCustomNameServer(self, state):
        self.get("ns_custom_text").set_sensitive(state)

    def insertData(self):
        """show preferences
        """
        data = self.iface.info(self._package,
                               self._connection)
        caps = self.iface.capabilities(self._package)
        #Profile Frame
        self.get("profilename").set_text(data[u"name"])
        self.if_available_set(data, "device_name",
                              self.get("device_name_label").set_text)
        #TODO:more than one device support

        #Network Settings Frame
        if data.has_key("net_mode"):
            if data["net_mode"] == "auto":
                self.get("dhcp_rb").set_active(True)
                self.setManualNetwork(False)
            else:
                self.get("manual_rb").set_active(False)
                self.setManualNetwork(True)

        self.if_available_set(data, "net_address",
                              self.get("address").set_text)
        self.if_available_set(data, "net_mask",
                              self.get("networkmask").set_text)
        self.if_available_set(data, "net_gateway",
                              self.get("gateway").set_text)

        #Name Servers Frame
        if data.has_key("name_mode"):
            if data["name_mode"] == "default":
                self.get("ns_default_rb").set_active(True)
                self.setCustomNameServer(False)
            elif data["name_mode"] == "auto":
                self.get("ns_auto_rb").set_active(True)
                self.setCustomNameServer(False)
            elif data["name_mode"] == "custom":
                self.get("ns_custom_rb").set_active(True)
                self.setCustomNameServer(True)
        self.if_available_set(data, "name_server",
                              self.get("ns_custom_text").set_text)
        # Wireless Frame
        self.if_available_set(data, "remote",
                              self.get("essid_text").set_text)
        modes = caps["modes"].split(",")
        if "auth" in modes:
            authType = self.iface.authType(self._package,
                                           self._connection)
            self.setSecurityTypesStyle()
            noauth = _("No Authentication")
            self._authMethods = [(0, "none", noauth)]
            append_to_types = self.get("security_types").append_text
            append_to_types(noauth)
            self.get("security_types").set_active(0)
            index = 1
            with_password = False
            for name, desc in self.iface.authMethods(self._package):
                append_to_types(desc)
                self._authMethods.append((index, name, desc))
                if name == authType:
                    self.get("security_types").set_active(index)
                    with_password = True
                index += 1
            if with_password:
               self.show_password("hidden")

    def show_password(self, state):
        if (state == False) | (state == "hidden"):
            self.get("hidepass_cb").hide()
            self.get("pass_text").hide()
            self.get("pass_lb").hide()
        elif state == True:
            self.get("hidepass_cb").show()
            self.get("pass_text").show()
            self.get("pass_lb").show()
        if state == "hidden":
            self.get("changepass_btn").show()
        else:
            self.get("changepass_btn").hide()

    def if_available_set(self, data, key, method):
        if data.has_key(key):
            method(data[key])

    def getWindow(self):
        """returns window
        """
        return self.get("window_edit")

