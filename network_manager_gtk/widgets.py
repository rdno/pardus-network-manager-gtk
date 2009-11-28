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
import pango
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

class WifiItemHolder(gtk.ScrolledWindow):
    """holder for wifi connections
    """

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
            self.remove(self.get_child())

gobject.type_register(WifiItemHolder)

class NewWifiConnectionItem(gtk.Table):
    """new wifi connection
    """
    def __init__(self,
                 device_id,
                 connection):
        """init
        Arguments:
        - `device_id`: connection device
        - `connection`: scanRemote callback dict
                        example: {'remote':'ESSID Name',
                                  'quality':'60',
                                  'quality_max':'100'
                                  'encryption':'wpa-psk',
                                  ...}
        """
        gtk.Table.__init__(self, rows=2, columns=4)
        self._device_id = device_id
        self._connection = connection;
        self._create_ui();
    def _create_ui(self):
        """creates UI
        """
        frac = float(self._connection['quality'])/ \
               float(self._connection['quality_max'])
        per = self._connection['quality']
        self._quality_bar = gtk.ProgressBar()
        self._quality_bar.set_fraction(frac)
        self._quality_bar.set_text(_("%d%%") % int(per))

        self._name_txt = gtk.Label(self._connection['remote'])
        self._name_txt.set_alignment(0.0 , 0.5)

        self._encrypt_txt = gtk.Label(self._connection['encryption'])
        self._encrypt_txt.set_alignment(0.0 , 0.5)

        self._connect_btn = gtk.Button(_("Connect"))

        self.attach(self._quality_bar, 0, 1, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self._name_txt, 1, 2, 0, 1,
                    gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._encrypt_txt, 1, 2, 1, 2,
                    gtk.SHRINK, gtk.SHRINK)
        self.attach(self._connect_btn, 2, 3, 0, 2,
                    gtk.SHRINK, gtk.SHRINK)

gobject.type_register(NewWifiConnectionItem)

class NewConnectionWindow(gtk.Window):
    """show new connections as a list
    """

    def __init__(self, iface):
        """init
        Arguments:
        - `iface`: NetworkIface
        """
        gtk.Window.__init__(self)
        self._iface = iface
        self.set_title(_("New Connection"))
        self._package = "wireless_tools"
        self._devices = self._iface.devices(self._package).keys()
        self._create_ui();
        self._cons = [] #connections
        self.scan()
    def _create_ui(self):
        """creates ui
        """
        self._ui = gtk.VBox()
        self.add(self._ui)

        self._refresh_btn = gtk.Button("")
        self._refresh_btn.connect("clicked", self.scan)
        self._ui.add(self._refresh_btn)

        self._list= gtk.VBox()
        self._ui.add(self._list)
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
        self._set_scanning(True)
        d = self._devices[0] #TODO:more than one device support
        self._iface.scanRemote(d, self._package,
                               self._scan_callback)
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
    def _show_list(self, connections):
        """show list

        Arguments:
        - `connections`: connections array
        """
        d = self._devices[0]
        #remove old ones
        map(self._list.remove, self._cons)
        self._cons = [NewWifiConnectionItem(d, x)
                      for x in connections]
        #add new ones
        map(self._list.add, self._cons)
        self.show_all()

gobject.type_register(NewConnectionWindow)

class dummy_data_creator(object):
    """create
    """

    def __init__(self,
                 device,
                 device_name,
                 essid=None):
        """init
        Arguments:
        - `device`:
        - `essid`:
        """
        self._wireless = False
        self._device = device
        self._device_name = device_name
        if essid is not None:
            self._essid = essid
            self._wireless = True
    def get(self):
        """get data
        """
        data = {}
        if self._wireless:
            data["name"] = self._essid
        else:
            data["name"] = "Kablo" #TODO: what?
        data["device_id"] = self._device
        data["device_name"] = self._device_name
        #Network Settings
        data["net_mode"] = "auto"
        data["net_address"] = ""
        data["net_mask"] = ""
        data["net_gateway"] = ""
        #Name Server Settings
        data["name_mode"] = "default"
        data["name_server"] = ""
        return data

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
        self._xml.signal_connect("on_new_clicked",
                                 self.show_news)
        self._window = self._xml.get_widget("window_main")
        self._holder = self._xml.get_widget("holder")
        self.iface = NetworkIface()
    def show_news(self, widget):
        a = NewConnectionWindow(self.iface)
        a.show()
    def brand_new(self, widget):
        """deneme

        Arguments:

        - `widget`:
        """
        pack = "net_tools"
        device = self.iface.devices(pack).keys()[0]
        name = self.iface.devices(pack)[device]
        a = EditInterface(pack,
                          "",
                          is_new=True,
                          new_data=dummy_data_creator(device, name).get())
        a.getWindow().show()

    def getWindow(self):
        """returns window
        """
        return self._window
    def getHolder(self):
        """returns holder
        """
        return self._holder

# --- Edit Window Sections (in ui: frame)

class EditSection(object):
    def __init__(self, parent):
        super(EditSection, self).__init__()
        self.get = parent.get
        self.signal_connect = parent._xml.signal_connect
        self.parent = parent
    def if_available_set(self, data, key, method):
        """if DATA dictionary has KEY execute METHOD with
        arg:data[key]"""
        if data.has_key(key):
            method(data[key])
    def get_text_of(self, name):
        """gets text from widget in unicode"""
        return unicode(self.get(name).get_text())
    def collect_data(self, data):
        """collect data from ui and append datas to
        given(data) dictionary"""
        pass

class ProfileSection(EditSection):
    def __init__(self, parent):
        super(ProfileSection, self).__init__(parent)
    def insert_data_and_show(self, data):
        self.if_available_set(data, "name",
                              self.get("profilename").set_text)
        self.if_available_set(data, "device_name",
                              self.get("device_name_label").set_text)
        self.device_id = data["device_id"]
        #TODO:more than one device support
    def collect_data(self, data):
        super(ProfileSection, self).collect_data(data)
        data["name"] = self.get_text_of("profilename")
        data["device_id"] = unicode(self.device_id)

class NetworkSettingsSection(EditSection):
    def __init__(self, parent):
        super(NetworkSettingsSection, self).__init__(parent)
    def _on_type_changed(self, widget):
        if widget is self.get("dhcp_rb"):
            self.set_manual_network(False)
        else:
            self.set_manual_network(True)
    def set_manual_network(self, state):
        self.get("address").set_sensitive(state)
        self.get("address_lb").set_sensitive(state)
        self.get("networkmask").set_sensitive(state)
        self.get("networkmask_lb").set_sensitive(state)
        self.get("gateway").set_sensitive(state)
        self.get("gateway_lb").set_sensitive(state)
        # custom things
        self.get("custom_gateway").set_sensitive(not state)
        self.get("custom_address").set_sensitive(not state)
        if not state:
            self._on_custom_address(self.get("custom_address"))
            self._on_custom_gateway(self.get("custom_gateway"))
    def _on_custom_address(self, widget):
        state = widget.get_active()
        self.get("address").set_sensitive(state)
        self.get("address_lb").set_sensitive(state)
        self.get("networkmask").set_sensitive(state)
        self.get("networkmask_lb").set_sensitive(state)
    def _on_custom_gateway(self, widget):
        state = widget.get_active()
        self.get("gateway").set_sensitive(state)
        self.get("gateway_lb").set_sensitive(state)
    def listen_signals(self):
        self.signal_connect("on_dhcp_rb_clicked",
                            self._on_type_changed)
        self.signal_connect("on_manual_rb_clicked",
                             self._on_type_changed)
        self.signal_connect("on_custom_gateway_toggled",
                            self._on_custom_gateway)
        self.signal_connect("on_custom_address_toggled",
                            self._on_custom_address)
    def insert_data_and_show(self, data):
        if data.has_key("net_mode"):
            self.listen_signals()
            if data["net_mode"] == "auto":
                self.get("dhcp_rb").set_active(True)
                self.set_manual_network(False)
                if self.is_custom(data, "net_gateway"):
                    self.get("custom_gateway").set_active(True)
                if self.is_custom(data, "net_address"):
                    self.get("custom_address").set_active(True)
            else:
                self.get("manual_rb").set_active(False)
                self.set_manual_network(True)

        self.if_available_set(data, "net_address",
                              self.get("address").set_text)
        self.if_available_set(data, "net_mask",
                              self.get("networkmask").set_text)
        self.if_available_set(data, "net_gateway",
                              self.get("gateway").set_text)
    def is_custom(self, data, key):
        if data.has_key(key):
            if data[key] != "":
                return True
        return False
    def collect_data(self, data):
        super(NetworkSettingsSection, self).collect_data(data)
        data["net_mode"] = u"auto"
        data["net_address"] = u""
        data["net_mask"] = u""
        data["net_gateway"] = u""
        if self.get("manual_rb").get_active():
            data["net_mode"] = u"manual"
        if self.get("address").state == gtk.STATE_NORMAL:
            data["net_address"] = self.get_text_of("address")
            data["net_mask"] = self.get_text_of("networkmask")
        if self.get("gateway").state == gtk.STATE_NORMAL:
            data["net_gateway"] = self.get_text_of("gateway")

class NameServerSection(EditSection):
    def __init__(self, parent):
        super(NameServerSection, self).__init__(parent)
    def set_custom_name(self, state):
        self.get("ns_custom_text").set_sensitive(state)
    def _on_type_changed(self, widget):
        if widget is self.get("ns_custom_rb"):
            self.set_custom_name(True)
        else:
            self.set_custom_name(False)
    def listen_signals(self):
        self.signal_connect("on_ns_default_rb_clicked",
                            self._on_type_changed)
        self.signal_connect("on_ns_custom_rb_clicked",
                            self._on_type_changed)
        self.signal_connect("on_ns_auto_rb_clicked",
                            self._on_type_changed)
    def insert_data_and_show(self, data):
        self.listen_signals()
        if data.has_key("name_mode"):
            if data["name_mode"] == "default":
                self.get("ns_default_rb").set_active(True)
                self.set_custom_name(False)
            elif data["name_mode"] == "auto":
                self.get("ns_auto_rb").set_active(True)
                self.set_custom_name(False)
            elif data["name_mode"] == "custom":
                self.get("ns_custom_rb").set_active(True)
                self.set_custom_name(True)
        self.if_available_set(data, "name_server",
                              self.get("ns_custom_text").set_text)
    def collect_data(self, data):
        super(NameServerSection, self).collect_data(data)
        data["name_mode"] = u"default"
        data["name_server"] = u""
        if self.get("ns_auto_rb").get_active():
            data["name_mode"] = u"auto"
        if self.get("ns_custom_rb").get_active():
            data["name_mode"] = u"custom"
            data["name_server"] = self.get_text_of("ns_custom_text")

class WirelessSection(EditSection):
    def __init__(self, parent):
        super(WirelessSection, self).__init__(parent)
        self.iface = parent.iface
        self.package = parent._package
        self.connection = parent._connection
        self.is_new = parent.is_new
    # --- Password related
    def show_password(self, state):
        if not state:
            self.get("hidepass_cb").hide()
            self.get("pass_text").hide()
            self.get("pass_lb").hide()
        else:
            self.get("hidepass_cb").show()
            self.get("pass_text").show()
            self.get("pass_lb").show()
    def hide_password(self, widget):
        visibility = not widget.get_active()
        self.get("pass_text").set_visibility(visibility)
    # end Password related
    def scan(self, widget=None):
        self.get("scan_btn").hide()
        self.wifiitems.set_scanning(True)
        self.iface.scanRemote(self.device , self.package, self.wifilist)
    def security_types_changed(self, widget):
        index = widget.get_active()
        if index == 0:
            self.show_password(False)
        else:
            self.show_password(True)
    def listen_signals(self):
        self.signal_connect("on_security_types_changed",
                            self.security_types_changed)
        self.signal_connect("on_hidepass_cb_toggled",
                            self.hide_password)
    def set_security_types_style(self):
        ##Security Type ComboBox
        model = gtk.ListStore(str)
        security_types = self.get("security_types")
        security_types.set_model(model)
        cell = gtk.CellRendererText()
        security_types.pack_start(cell)
        security_types.add_attribute(cell,'text',0)
    def prepare_security_types(self, authType):
        self.set_security_types_style()
        noauth = _("No Authentication")
        self._authMethods = [("none", noauth)]
        append_to_types = self.get("security_types").append_text
        append_to_types(noauth)
        self.get("security_types").set_active(0)
        index = 1
        self.with_password = False
        for name, desc in self.iface.authMethods(self.package):
            append_to_types(desc)
            self._authMethods.append((name, desc))
            if name == authType:
                self.get("security_types").set_active(index)
                self.with_password = True
            index += 1
    def on_wifi_clicked(self, widget, callback_data):
        data = callback_data["get_connection"]()
        self.get("essid_text").set_text(data["remote"])
        for index, method in enumerate(self._authMethods):
            if method[0] == data["encryption"]:
                self.get("security_types").set_active(index)
    def wifilist(self, package, exception, args):
        self.get("scan_btn").show()
        self.signal_connect("on_scan_btn_clicked",
                            self.scan)
        if not exception:
            self.wifiitems.getConnections(args[0])
            self.wifiitems.listen_change(self.on_wifi_clicked)
        else:
            print exception
    def insert_data_and_show(self, data, caps):
        self.listen_signals()
        self.device = data["device_id"]
        self.if_available_set(data, "remote",
                              self.get("essid_text").set_text)
        modes = caps["modes"].split(",")
        if ("auth" in modes) and (not self.is_new):
            authType = self.iface.authType(self.package,
                                           self.connection)
            self.prepare_security_types(authType)
            self.get("hidepass_cb").set_active(True)
            if self.with_password:
                authType = self.iface.authType(self.package,
                                               self.connection)
                authInfo = self.iface.authInfo(self.package,
                                               self.connection)
                authParams = self.iface.authParameters(self.package,
                                                       authType)
                if len(authParams) == 1:
                    password = authInfo.values()[0]
                    self.get("pass_text").set_text(password)
                elif len(authParams) > 1:
                    print "\nTODO:Dynamic WEP support"
            self.show_password(self.with_password)
        if self.is_new:
            pass
        self.wifiitems = WifiItemHolder()
        self.get("wireless_table").attach(self.wifiitems,
                                          0, 1, 0, 3,
                                          gtk.EXPAND|gtk.FILL,
                                          gtk.EXPAND|gtk.FILL)
        self.scan()
    def collect_data(self, data):
        super(WirelessSection, self).collect_data(data)
        data["remote"] = self.get_text_of("essid_text")
        data["apmac"] = u"" #i think it is Access Point MAC

        #Security
        data["auth"] = unicode(self._authMethods[
                self.get("security_types").get_active()][0])
        if data["auth"] != u"none":
            params = self.iface.authParameters("wireless_tools",
                                               data["auth"])
            if len(params) == 1:
                key = "auth_%s" % params[0][0]
                data[key] = self.get_text_of("pass_text")
            else:
                print "TODO:Dynamic WEP Support"


# end Edit Window Sections

class EditInterface(object):
    """Imports edit window glade
    """

    def __init__(self,
                 package,
                 connection="",
                 is_new=False,
                 new_data={}):
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
        self.listen_signals()
        self.is_new = is_new
        self.new_data = new_data
        self.insertData()
    def apply(self, widget):
        data = self.collect_data()
        try:
            self.iface.updateConnection(self._package,
                                        data["name"],
                                        data)
        except Exception, e:
            print "Exception:", unicode(e)

        if not self.name == data["name"]:
            self.iface.deleteConnection(self._package, self.name)
        if self.is_up:
            self.iface.connect(self._package, self.name)
        self.getWindow().destroy()
    def cancel(self, widget):
        self.getWindow().destroy()
    def listen_signals(self):
        self._xml.signal_connect("apply_btn_clicked",
                                 self.apply)
        self._xml.signal_connect("cancel_btn_clicked",
                                 self.cancel)
    def insertData(self):
        """show preferences
        """
        if not self.is_new:
            data = self.iface.info(self._package,
                                   self._connection)
        else:
            data = self.new_data
        self.name = data["name"]
        self.is_up = False
        if data.has_key("state"):
            if data["state"][0:2] == "up":
                self.is_up = True
        #Profile Frame
        self.profile_frame = ProfileSection(self)
        self.profile_frame.insert_data_and_show(data)
        #Network Settings Frame
        self.network_frame = NetworkSettingsSection(self)
        self.network_frame.insert_data_and_show(data)
        #Name Servers Frame
        self.name_frame = NameServerSection(self)
        self.name_frame.insert_data_and_show(data)
        # Wireless Frame
        if self._package == "wireless_tools":
            caps = self.iface.capabilities(self._package)
            self.wireless_frame = WirelessSection(self)
            self.wireless_frame.insert_data_and_show(data, caps)
        else:
            self.get("wireless_frame").hide()

    def collect_data(self):
        data = {}
        self.profile_frame.collect_data(data)
        self.network_frame.collect_data(data)
        self.name_frame.collect_data(data)
        if self._package == "wireless_tools":
            self.wireless_frame.collect_data(data)
        return data
    def getWindow(self):
        """returns window
        """
        return self.get("window_edit")
