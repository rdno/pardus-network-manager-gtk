import pygtk
pygtk.require('2.0')
import gtk, gobject

from backend import NetworkIface

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
        if self._state[0:2] == "up":
            self.check_btn.set_active(True)
        self._label = gtk.Label(self._connection_name)
        self._info = gtk.Label(self._state)
        self._label.set_alignment(0.0, 0.5)
        self._info.set_alignment(0.0, 0.5)
        self.edit_btn = gtk.Button("Edit")
        self.edit_btn.show()
        self.attach(self.check_btn, 0, 1, 0, 2, gtk.SHRINK, gtk.SHRINK)
        self.attach(self._label, 1 , 2, 0, 1, gtk.EXPAND|gtk.FILL, gtk.SHRINK)
        self.attach(self._info, 1 , 2, 1, 2, gtk.EXPAND|gtk.FILL,  gtk.SHRINK)
        self.attach(self.edit_btn, 2, 3, 0, 2, gtk.SHRINK, gtk.SHRINK)
    def connectSignals(self, click_signal, edit_signal):
        """connect widgets signals
        Arguments:
        - `click_signal`:
        - `edit_signal`:
        """
        self.check_btn.connect("clicked", click_signal,
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
        builder = gtk.Builder()
        builder.add_from_file("ui/main.glade")
        builder.connect_signals({"on_window_main_destroy" : gtk.main_quit })
        self.window = builder.get_object("window_main")
        self.showConnections()
    def _onConnectionClicked(self, widget, callback_data):
        self.iface.toggle(callback_data['package'],
                          callback_data['connection'])
    def _onConnectionEdit(self, widget, callback_data):
        print "TODO"
    def showConnections(self):
        """show connection on gui
        """
        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        for package in self.iface.packages():
            for connection in self.iface.connections(package):
                state = self.iface.info(package, connection)[u"state"]
                con_wg = ConnectionWidget(package,
                                          connection,
                                          state)
                con_wg.connectSignals(self._onConnectionClicked,
                                      self._onConnectionEdit)
                self.vbox.add(con_wg)

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
