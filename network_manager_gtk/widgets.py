# -*- coding: utf-8 -*-
"""includes Network Manager gtk's widgets

ConnectionWidget - A special widget contains connection related stuff
ProfilesHolder - Holds Profile List 
WifiItemHolder - holder for wifi connections (for EditWindow)
NewWifiConnectionItem - new wifi connection item
                        (for NewConnectionWindow)
NewEthernetConnectionItem - new ethernet connection item
                            (for NewConnectionWindow)
EditWindowFrame - Base Edit Window Frame
ProfileFrame - Edit Window > Profile Frame
NetworkFrame - Edit Window > Network Settings Frame
NameServerFrame - Edit Window > Name Server Frame
WirelessFrame - Edit Settings Window > WirelessFrame

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

from translation import _, bind_glade_domain
from backend import NetworkIface

import pygtk
pygtk.require('2.0')
import pango
import gtk
import gobject
from gtk import glade

class ConnectionWidget(gtk.Table):
    """A special widget contains connection related stuff"""
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
        self._create_ui()
    def _create_ui(self):
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
        self.set_mode(self._state.split(' '))
    def set_mode(self, args):
        """sets _info label text
        and is _on or not
        Arguments:
        - `args`: [state, detail]
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
            self._info.set_markup(states[args[0]]+':'+
                                  '<span color="green">'+
                                  args[1] +
                                  '</span>')
    def connect_signals(self, callback):
        """connect widgets signals
        returns {'action':(toggle | edit | delete)
                 'package':package_name,
                 'connection':connection_name}
        Arguments:
        - `callback`: callback function
        """
        self.check_btn.connect("pressed", callback,
                              {"action":"toggle",
                               "package":self._package_name,
                               "connection":self._connection_name})
        self.edit_btn.connect("clicked", callback,
                              {"action":"edit",
                               "package":self._package_name,
                               "connection":self._connection_name})
        self.delete_btn.connect("clicked", callback,
                              {"action":"delete",
                               "package":self._package_name,
                               "connection":self._connection_name})

gobject.type_register(ConnectionWidget)

class ProfilesHolder(gtk.ScrolledWindow):
    """Holds Profile List"""
    def __init__(self):
        """init"""
        gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.set_policy(gtk.POLICY_NEVER,
                        gtk.POLICY_AUTOMATIC)
        self._vbox = gtk.VBox(homogeneous=False,
                              spacing=10)
        self.add_with_viewport(self._vbox)
        self._profiles = {}
    def set_connection_signal(self, callback):
        """sets default callback for ConnectionWidget
        """
        self._callback = callback
    def add_profile(self, package, connection, state):
        """add profiles to vbox
        """
        con_wg = ConnectionWidget(package,
                                  connection,
                                  state)
        con_wg.connect_signals(self._callback)
        self._vbox.pack_start(con_wg, expand=False, fill=False)
        if not self._profiles.has_key(package):
            self._profiles[package] = {}
        self._profiles[package][connection] = {"state":state,
                                               "widget":con_wg}
        self._vbox.show_all()
    def update_profile(self, package, connection, state):
        """update connection state
        """
        c = self._profiles[package][connection]
        c["state"] = state
        c["widget"].set_mode(state)
    def remove_profile(self, package, connection):
        """remove profile
        """
        c = self._profiles[package][connection]
        self._vbox.remove(c["widget"])

gobject.type_register(ProfilesHolder)

class WifiItemHolder(gtk.ScrolledWindow):
    """holder for wifi connections (for EditWindow)"""
    def __init__(self):
        """init
        """
        gtk.ScrolledWindow.__init__(self)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.set_policy(gtk.POLICY_NEVER,
                        gtk.POLICY_AUTOMATIC)
    def setup_view(self):
        self.store = gtk.ListStore(str, str)
        column = lambda x, y:gtk.TreeViewColumn(x,
                                                gtk.CellRendererText(),
                                                text=y)
        self.view = gtk.TreeView(self.store)
        self.view.append_column(column(_("Name"), 0))
        self.view.append_column(column(_("Quality"), 1))
    def get_active(self):
        cursor = self.view.get_cursor()
        if cursor[0]:
            data = self.data[cursor[0][0]]
            return data
        return None
    def listen_change(self, handler):
        self.view.connect("cursor-changed", handler,
                          {"get_connection":self.get_active})
    def getConnections(self, data):
        self.set_scanning(False)
        self.items = []
        self.data = []
        self.setup_view()
        for remote in data:
            self.store.append([remote["remote"],
                               _("%d%%") % int(remote["quality"])])
            self.data.append(remote)
        self.add_with_viewport(self.view)
        self.show_all()
    def set_scanning(self, is_scanning):
        if is_scanning:
            if self.get_child():
                self.remove(self.get_child())
            self.scan_lb = gtk.Label(_("Scanning..."))
            self.add_with_viewport(self.scan_lb)
            self.show_all()
        else:
            if self.get_child():
                self.remove(self.get_child())

gobject.type_register(WifiItemHolder)

class NewWifiConnectionItem(gtk.Table):
    """new wifi connection item (for NewConnectionWindow)"""
    def __init__(self,
                 device_id,
                 connection,
                 auth_type):
        """init
        Arguments:
        - `device_id`: connection device
        - `connection`: scanRemote callback dict
                        example: {'remote':'ESSID Name',
                                  'quality':'60',
                                  'quality_max':'100'
                                  'encryption':'wpa-psk',
                                  ...}
        - `auth_type`: wpa-psk -> WPA Ortak Anahtar
        """
        gtk.Table.__init__(self, rows=3, columns=3)
        self._device_id = device_id
        self._connection = connection
        self._type = auth_type
        self._create_ui()
    def _create_ui(self):
        """creates UI
        """
        frac = float(self._connection['quality'])/ \
               float(self._connection['quality_max'])
        per = self._connection['quality']
        self._quality_bar = gtk.ProgressBar()
        self._quality_bar.set_fraction(frac)
        self._quality_bar.set_text(_("%d%%") % int(per))

        self._name_txt = gtk.Label("")
        self._name_txt.set_markup("<span color='blue'>" +
                                  self._connection['remote']
                                  + "</span>")
        self._name_txt.set_alignment(0.0 , 0.5)

        self._encrypt_txt = gtk.Label(self._type)
        self._encrypt_txt.set_alignment(0.0 , 0.5)

        self._connect_btn = gtk.Button(_("Connect"))


        self.set_row_spacings(5)
        self.set_col_spacings(5)
        self.attach(self._quality_bar, 0, 1, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self._name_txt, 1, 2, 0, 1,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._encrypt_txt, 1, 2, 1, 2,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._connect_btn, 2, 3, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(gtk.HSeparator(), 0, 3, 2, 3,
                    gtk.FILL, gtk.SHRINK)
    def on_connect(self, func):
        """on connect button clicked

        Arguments:
        - `func`: callback function
        """
        self._connect_btn.connect("clicked",
                                  func,
                                  {"connection":self._connection,
                                   "device": self._device_id,
                                   "package": "wireless_tools"})

gobject.type_register(NewWifiConnectionItem)

class NewEthernetConnectionItem(gtk.Table):
    """new ethernet connection item (for NewConnectionWindow)"""
    def __init__(self, device_id, device_name):
        """init

        Arguments:
        - `device_id`: device id
        - `device_name`: device name to show user
        """
        gtk.Table.__init__(self, rows=3, columns=2)
        self._device_id = device_id
        self._device_name = device_name
        self._create_ui()
    def _create_ui(self):
        """creates ui
        """
        self._name_lb = gtk.Label("")
        self._name_lb.set_markup("<span color='blue'>" +
                                  _("Ethernet")
                                  + "</span>")
        self._name_lb.set_alignment(0.0, 0.5)

        self._device_name_lb = gtk.Label(self._device_name)
        self._device_name_lb.set_alignment(0.0, 0.5)

        self._connect_btn = gtk.Button(_("Connect"))

        self.set_row_spacings(5)
        self.set_col_spacings(5)
        self.attach(self._name_lb, 0, 1, 0, 1,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._device_name_lb, 0, 1, 1, 2,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._connect_btn, 2, 3, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(gtk.HSeparator(), 0, 3, 2, 3,
                    gtk.FILL, gtk.SHRINK)
    def on_connect(self, func):
        """on connect button clicked

        Arguments:
        - `func`:callback function
        """
        self._connect_btn.connect("clicked",
                                  func,
                                  {"connection":"",
                                   "device":self._device_id,
                                   "package":"net_tools"})
class EditWindowFrame(gtk.Frame):
    """Base EditWindowFrame"""
    def __init__(self, data):
        """init

        Arguments:
        - `data`: iface.info
        """
        gtk.Frame.__init__(self)
        self._create_ui()
        self._listen_signals()
        self._insert_data(data)
    def _create_ui(self):
        """creates ui elements
        """
        pass
    def _listen_signals(self):
        """listens some signals
        """
        pass
    def _insert_data(self, data):
        """inserts data

        Arguments:
        - `data`:data to insert
        """
        pass
    def if_available_set(self, data, key, method):
        """if DATA dictionary has KEY execute METHOD with
        arg:data[key]"""
        if data.has_key(key):
            method(data[key])
    def get_text_of(self, name):
        """gets text from widget in unicode"""
        return unicode(name.get_text())
    def collect_data(self, data):
        """collect data from ui and append datas to
        given(data) dictionary"""
        pass
    def _rb_callback(self, widget, data):
        """RadioButton callback

        Arguments:
        - `widget`: widget
        - `data`: callback data
        """
        #if custom selected enable them
        for i in data["enable"]:
            i.set_sensitive(data["is_custom"])
        #if custom selected disable them
        for j in data["disable"]:
            j.set_sensitive(not data["is_custom"])
    def set_rb_signal(self, rb_list, custom_rb,
                      on_custom_enable,
                      on_custom_disable = []):
        """Sets RadioButton signals
        and adjust behaviour

        Arguments:
        - `rb_list`: RadioButton list
        - `custom_rb`: RadioButton labeled Custom
        - `on_custom_enable`: List of widgets to enable
                              if custom selected
        - `on_custom_disable`: List of widgets to disable
                               if custom selected
        """
        for i in rb_list:
            i.connect("clicked", self._rb_callback,
                      {"is_custom":i == custom_rb,
                       "enable":on_custom_enable,
                       "disable":on_custom_disable})
class ProfileFrame(EditWindowFrame):
    """Edit Window > Profile Frame"""
    def __init__(self, data):
        EditWindowFrame.__init__(self, data)
    def _create_ui(self):
        self.set_label(_("<b>Profile</b>"))
        self.get_label_widget().set_use_markup(True)

        profile_lb = gtk.Label(_("Profile Name:"))
        self._profile_name = gtk.Entry()

        self._device_name_lb = gtk.Label("")
        self._device_name_lb.set_ellipsize(pango.ELLIPSIZE_MIDDLE)

        #structure
        hbox = gtk.HBox(homogeneous=False,
                        spacing=5)
        self.add(hbox)
        hbox.pack_start(profile_lb, expand=False)
        hbox.pack_start(self._profile_name)
        hbox.pack_start(self._device_name_lb)
        self.show_all()
    def _insert_data(self, data):
        self.if_available_set(data, "name",
                              self._profile_name.set_text)
        self.if_available_set(data, "device_name",
                              self._device_name_lb.set_text)
        self.device_id = data["device_id"]
        #TODO:more than one device support
    def collect_data(self, data):
        data["name"] = self.get_text_of(self._profile_name)
        data["device_id"] = unicode(self.device_id)

class NetworkFrame(EditWindowFrame):
    """Edit Window > Network Settings Frame
    """

    def __init__(self, data):
        EditWindowFrame.__init__(self, data)
    def _create_ui(self):
        self.set_label(_("<b>Network Settings</b>"))
        self.get_label_widget().set_use_markup(True)

        self._dhcp_rb = gtk.RadioButton(label=_("Use DHCP"))
        self._custom_rb = gtk.RadioButton(group=self._dhcp_rb,
                                          label=_("Use Manual Settings")
                                          )
        self._address_lb = gtk.Label(_("Address:"))
        self._address_lb.set_alignment(1.0, 0.5)
        self._mask_lb = gtk.Label(_("Network Mask:"))
        self._mask_lb.set_alignment(1.0, 0.5)
        self._gateway_lb = gtk.Label(_("Default Gateway:"))
        self._gateway_lb.set_alignment(1.0, 0.5)

        self._address_txt = gtk.Entry()
        self._mask_txt = gtk.Entry()
        self._gateway_txt = gtk.Entry()

        custom = _("Custom")
        self._custom_add_cb = gtk.CheckButton(label=custom)
        self._custom_gate_cb = gtk.CheckButton(label=custom)

        #structure
        table = gtk.Table(rows=4, columns=4)
        self.add(table)

        table.attach(self._dhcp_rb, 0, 1 , 0, 1,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._custom_rb, 0, 1 , 1, 2,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._address_lb, 1, 2 , 1, 2,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._mask_lb, 1, 2 , 2, 3,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._gateway_lb, 1, 2 , 3, 4,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._address_txt, 2, 3 , 1, 2,
                     gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        table.attach(self._mask_txt, 2, 3, 2, 3,
                     gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        table.attach(self._gateway_txt, 2, 3 , 3, 4,
                     gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        table.attach(self._custom_add_cb, 3, 4 , 1, 2,
                     gtk.FILL, gtk.SHRINK)
        table.attach(self._custom_gate_cb, 3, 4 , 3, 4,
                     gtk.FILL, gtk.SHRINK)
        self.show_all()
    def _listen_signals(self):
        self._rb_list = [self._dhcp_rb, self._custom_rb]
        self._on_custom_enable = [self._address_lb,
                                  self._address_txt,
                                  self._mask_lb,
                                  self._mask_txt,
                                  self._gateway_lb,
                                  self._gateway_txt]
        self._on_custom_disable = [self._custom_add_cb,
                                   self._custom_gate_cb]
        self.set_rb_signal(self._rb_list,
                           self._custom_rb,
                           self._on_custom_enable,
                           self._on_custom_disable)
        self._custom_gate_cb.connect("clicked", self._on_custom)
        self._custom_add_cb.connect("clicked", self._on_custom)
    def _insert_data(self, data):
        if data.has_key("net_mode"):
            if data["net_mode"] == "auto":
                self._dhcp_rb.set_active(True)
                self._rb_callback(self._dhcp_rb,
                                  {"is_custom":False,
                                   "enable":self._on_custom_enable,
                                   "disable":self._on_custom_disable})
                if self.is_custom(data, "net_gateway"):
                    self._custom_gate_cb.set_active(True)
                if self.is_custom(data, "net_address"):
                    self._custom_add_cb.set_active(True)
            else:
                self._custom_rb.set_active(False)

        self.if_available_set(data, "net_address",
                              self._address_txt.set_text)
        self.if_available_set(data, "net_mask",
                              self._mask_txt.set_text)
        self.if_available_set(data, "net_gateway",
                              self._gateway_txt.set_text)
    def _on_custom(self, widget):
        if widget is self._custom_add_cb:
            widgets = self._on_custom_enable[0:4]
        else:
            widgets = self._on_custom_enable[4:]
        for x in widgets:
            x.set_sensitive(widget.get_active())
    def _rb_callback(self, widget, data):
        EditWindowFrame._rb_callback(self, widget, data)
        if not data["is_custom"]:
            if self._custom_add_cb.get_active():
                for x in data["enable"][0:4]:
                    x.set_sensitive(True)
            if self._custom_gate_cb.get_active():
                for x in data["enable"][4:]:
                    x.set_sensitive(True)
    def is_custom(self, data, key):
        if data.has_key(key):
            if data[key] != "":
                return True
        return False
    def collect_data(self, data):
        data["net_mode"] = u"auto"
        data["net_address"] = u""
        data["net_mask"] = u""
        data["net_gateway"] = u""
        if self._custom_rb.get_active():
            data["net_mode"] = u"manual"
        if self._address_txt.state == gtk.STATE_NORMAL:
            data["net_address"] = self.get_text_of(self._address_txt)
            data["net_mask"] = self.get_text_of(self._mask_txt)
        if self._gateway_txt.state == gtk.STATE_NORMAL:
            data["net_gateway"] = self.get_text_of(self._gateway_txt)

class NameServerFrame(EditWindowFrame):
    """Edit Window > Name Server Frame"""
    def __init__(self, data):
        EditWindowFrame.__init__(self, data)
    def _create_ui(self):
        self.set_label(_("<b>Name Servers</b>"))
        self.get_label_widget().set_use_markup(True)

        self._default_rb = gtk.RadioButton(label=_("Default"))

        self._auto_rb = gtk.RadioButton(group=self._default_rb,
                                        label=_("Automatic"))

        self._custom_rb = gtk.RadioButton(group=self._default_rb,
                                          label=_("Custom"))
        self._custom_txt = gtk.Entry()

        #structure
        hbox = gtk.HBox(homogeneous=False,
                        spacing=5)
        self.add(hbox)
        hbox.pack_start(self._default_rb, expand=False)
        hbox.pack_start(self._auto_rb, expand=False)
        hbox.pack_start(self._custom_rb, expand=False)
        hbox.pack_start(self._custom_txt, expand=True)
        self.show_all()
    def _listen_signals(self):
        self.set_rb_signal(rb_list=[self._default_rb,
                            self._auto_rb,
                            self._custom_rb],
                           custom_rb=self._custom_rb,
                           on_custom_enable=[self._custom_txt])
    def _insert_data(self, data):
        if data.has_key("name_mode"):
            self._custom_txt.set_sensitive(False)
            if data["name_mode"] == "default":
                self._default_rb.set_active(True)
            elif data["name_mode"] == "auto":
                self._auto_rb.set_active(True)
            elif data["name_mode"] == "custom":
                self._custom_rb.set_active(True)
                self._custom_txt.set_sensitive(True)
        self.if_available_set(data, "name_server",
                              self._custom_txt.set_text)
    def collect_data(self, data):
        data["name_mode"] = u"default"
        data["name_server"] = u""
        if self._auto_rb.get_active():
            data["name_mode"] = u"auto"
        if self._custom_rb.get_active():
            data["name_mode"] = u"custom"
            data["name_server"] = self.get_text_of(self._custom_txt)

class WirelessFrame(EditWindowFrame):
    """Edit Settings Window > WirelessFrame"""
    def __init__(self, data, iface,
                 package=None,connection=None,
                 with_list=True, is_new=False,
                 select_type="none"):
        self.iface = iface
        self.package = package
        self.connection = connection
        self.with_list = with_list
        self.is_new = is_new
        self.select_type = select_type
        EditWindowFrame.__init__(self, data)
    def _create_ui(self):
        self.set_label(_("<b>Wireless</b>"))
        self.get_label_widget().set_use_markup(True)

        self._essid_lb = gtk.Label(_("ESSID:"))
        self._essid_lb.set_alignment(1.0, 0.5)

        self._essid_txt = gtk.Entry()

        self._security_lb = gtk.Label(_("Security Type:"))
        self._security_lb.set_alignment(1.0, 0.5)

        self._security_types = gtk.combo_box_new_text()
        self._authMethods = [{"name":"none",
                              "desc":_("No Authentication")}]
        self._security_types.append_text(self._authMethods[0]["desc"])
        for name, desc in self.iface.authMethods(self.package):
            self._authMethods.append({"name":name, "desc":desc})
            self._security_types.append_text(desc)
        self._set_current_security_type(_("No Authentication"))
        self._pass_lb = gtk.Label(_("Password:"))
        self._pass_lb.set_alignment(1.0, 0.5)

        self._pass_txt = gtk.Entry()
        self._pass_txt.set_visibility(False)

        self._hide_cb = gtk.CheckButton(_("Hide Password"))
        self._hide_cb.set_active(True)

        if self.with_list:
            table = gtk.Table(rows=4, columns=3)

            self._wifiholder = WifiItemHolder()
            self._scan_btn = gtk.Button(_("Scan"))

            table.attach(self._essid_lb, 1, 2, 0, 1,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._essid_txt, 2, 3, 0, 1,
                         gtk.EXPAND | gtk.FILL, gtk.SHRINK)
            table.attach(self._security_lb, 1, 2, 1, 2,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._security_types, 2, 3, 1, 2,
                         gtk.EXPAND | gtk.FILL, gtk.SHRINK)
            table.attach(self._pass_lb, 1, 2, 2, 3,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._pass_txt, 2, 3, 2, 3,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._hide_cb, 1, 3, 3, 4,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._wifiholder, 0, 1, 0, 3,
                         gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL)
            table.attach(self._scan_btn, 0, 1, 3, 4,
                         gtk.FILL, gtk.SHRINK)
            self._wifiholder.show()
        else:
            table = gtk.Table(rows=4, columns=2)

            table.attach(self._essid_lb, 0, 1, 0, 1,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._essid_txt, 1, 2, 0, 1,
                         gtk.EXPAND | gtk.FILL, gtk.SHRINK)
            table.attach(self._security_lb, 0, 1, 1, 2,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._security_types, 1, 2, 1, 2,
                         gtk.EXPAND | gtk.FILL, gtk.SHRINK)
            table.attach(self._pass_lb, 0, 1, 2, 3,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._pass_txt, 1, 2, 2, 3,
                         gtk.FILL, gtk.SHRINK)
            table.attach(self._hide_cb, 0, 2, 3, 4,
                         gtk.FILL, gtk.SHRINK)
        self.add(table)
        table.show()
        self._essid_lb.show()
        self._essid_txt.show()
        self._security_lb.show()
        self._security_types.show()
    def _listen_signals(self):
        self._hide_cb.connect("clicked", self._on_hide_pass)
        self._security_types.connect("changed", self._on_sec_changed)
    def _insert_data(self, data):
        self.device = data["device_id"]
        self.if_available_set(data, "remote",
                              self._essid_txt.set_text)
        caps = self.iface.capabilities(self.package)
        modes = caps["modes"].split(",")
        if self.with_list:
            self.scan()
        if "auth" in modes:
            if not self.is_new:
                authType = self.iface.authType(self.package,
                                               self.connection)
                self._set_current_security_type(authType)
                self._show_password(False)
                if (not authType == "none") & (not authType == ""):
                    info = self.iface.authInfo(self.package,
                                               self.connection)
                    params = self.iface.authParameters(self.package,
                                                       authType)
                    if len(params) == 1:
                        password = info.values()[0]
                        self._pass_txt.set_text(password)
                    elif len(params) > 1:
                        print "\nTODO:Dynamic WEP Support"
                    self._show_password(True)
                else:
                    self._security_types.set_active(0)
                    self._show_password(False)
            else:
                self._set_current_security_type(self.select_type)
    def _on_hide_pass(self, widget):
        self._pass_txt.set_visibility(not widget.get_active())
    def _on_sec_changed(self, widget):
        self._show_password(not widget.get_active() == 0)
    def _show_password(self, state):
        if not state:
            self._hide_cb.hide()
            self._pass_txt.hide()
            self._pass_lb.hide()
        else:
            self._hide_cb.show()
            self._pass_txt.show()
            self._pass_lb.show()
    def _get_current_security_type(self):
        w = self._security_types
        current =  w.get_model()[w.get_active()][0]
        for x in self._authMethods:
            if x["desc"] == current:
                return x["name"]
    def _set_current_security_type(self, name):
        for i, x in enumerate(self._authMethods):
            if x["name"] == name:
                self._security_types.set_active(i)
                break
    def scan(self, widget=None):
        self._scan_btn.hide()
        self._wifiholder.set_scanning(True)
        self.iface.scanRemote(self.device ,
                              self.package,
                              self.listwifi)
    def listwifi(self, package, exception, args):
        self._scan_btn.show()
        self._scan_btn.connect("clicked",
                               self.scan)
        if not exception:
            self._wifiholder.getConnections(args[0])
            self._wifiholder.listen_change(self.on_wifi_clicked)
        else:
            print exception
    def on_wifi_clicked(self, widget, callback_data):
        data = callback_data["get_connection"]()
        self._essid_txt.set_text(data["remote"])
        self._set_current_security_type(data["encryption"])
    def collect_data(self, data):
        data["remote"] = self.get_text_of(self._essid_txt)
        data["apmac"] = u"" #i think it is Access Point MAC
        #Security
        data["auth"] = unicode(self._get_current_security_type())
        if data["auth"] != u"none":
            params = self.iface.authParameters("wireless_tools",
                                               data["auth"])
            if len(params) == 1:
                key = "auth_%s" % params[0][0]
                data[key] = self.get_text_of(self._pass_txt)
            else:
                print "TODO:Dynamic WEP Support"
