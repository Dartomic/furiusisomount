#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

def show(parent_window, message, message_type=Gtk.MessageType.INFO, buttons_type=Gtk.ButtonsType.OK):
    dialog = Gtk.MessageDialog(parent_window, Gtk.DialogFlags.MODAL, message_type, buttons_type, message)
    response = dialog.run()
    dialog.destroy()
    return response
