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

APP_NAME="network_manager_gtk"
LOCALE_DIR= "locale"
trans = gettext.translation(APP_NAME, LOCALE_DIR, fallback=False)
_ = trans.ugettext
def bind_glade_domain():
    from gtk import glade
    glade.bindtextdomain(APP_NAME, LOCALE_DIR)
    glade.textdomain(APP_NAME)
