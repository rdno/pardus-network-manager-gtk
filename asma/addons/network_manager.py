# -*- coding: utf-8 -*-
#
# Rıdvan Örsvuran (C) 2010
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
from asma.addon import AsmaAddon
from network_manager_gtk import NetworkManager
from network_manager_gtk.translation import _
class NetworkManagerAddon(AsmaAddon):
    """Network Manager Asma addon"""
    def __init__(self):
        """init the variables"""
        super(NetworkManagerAddon, self).__init__()
        self._uuid = "62e6a90b-52cc-4cba-86eb-56894fa7d893"
        self._icon_name = "applications-internet"
        self._label = _("Network Manager")
        self._widget = NetworkManager 
