#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is part of PyFuriusIsoMount. Copyright 2008 Dean Harris (marcus_furius@hotmail.com)
#
# PyFuriusIsoMount is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyFuriusIsoMount is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyFuriusIsoMount.  If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import os.path
import globals
from gettext import gettext as _

def show(parent):
    """
    Show an about dialog box
    """
    dlg = Gtk.AboutDialog()
    dlg.set_transient_for(parent)

    # Set credit information
    dlg.set_program_name(globals.assembly_title)
    dlg.set_version(globals.assembly_version)
    dlg.set_website(globals.assembly_website)
    dlg.set_translator_credits(_('translator-credits...')) # Truncated for brevity
    dlg.set_comments(globals.assembly_description)

    dlg.set_authors([
        _('Developer:'),
        'Dean Harris <marcus_furius@hotmail.com>',
    ])

    # Set logo
    if os.path.exists(globals.about_image):
        dlg.set_logo(GdkPixbuf.Pixbuf.new_from_file(globals.about_image))

    # Load the licence from the disk if possible
    if os.path.exists(globals.glp_license):
        with open(globals.glp_license) as license_file:
            dlg.set_license(license_file.read())
        dlg.set_wrap_license(True)

    dlg.run()
    dlg.destroy()
