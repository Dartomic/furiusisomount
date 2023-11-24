#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import locale
import gettext
from gettext import gettext as _
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import globals
import filehash
import time
import threading
import messagebox
import aboutbox
import log
import os
import subprocess
import imageaction

class MainWindow:
    drop_targets = [('text/plain', 0, 3)]
    
    def __init__(self, parameter):
        # Localization
        locale.setlocale(locale.LC_ALL, '')
        gettext.textdomain(globals.assembly_name)
        gettext.bindtextdomain(globals.assembly_name, globals.locale_directory)

        # Set the Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file(globals.application_interface)
        self.create_settings_directory()
        self.create_settings_file()
        log.write(globals.mount_log, _('Application started...'))
        self.set_storage_lists()
        self.set_history_entry()
        self.set_mounted_image_treeview()
        self.set_icons_and_text()
        self.load_mount_history()
        self.load_previously_mounted_images()

        self.builder.connect_signals({
            'button_checksum_clicked': self.button_checksum_clicked,
            'button_browse_clicked': self.button_browse_clicked,
            'button_about_clicked': self.button_about_clicked,
            'button_view_log_clicked': self.button_view_log_clicked,
            'button_delete_log_clicked': self.button_delete_log_clicked,
            'button_mount_clicked': self.button_mount_clicked,
            'comboentry_image_key_release': self.comboentry_image_key_release,
            'comboentry_image_changed': self.comboentry_image_changed,
            'treeview_mounted_images_cursor_changed': self.treeview_mounted_images_cursor_changed,
            'button_unmount_clicked': self.button_unmount_clicked,
            'button_burn_clicked': self.button_burn_clicked,
            'treeview_mounted_images_drag_data_recieved': self.treeview_mounted_images_drag_data_recieved,
            'treeview_mounted_images_row_activated': self.treeview_mounted_images_row_activated,
            'destroy': self.destroy
        })
        if parameter:
            try:
                imageaction.mount(parameter, self.image_storage, self.history_storage, self.history_array, self.builder.get_object('radiobutton_fuse').get_active())
            except OSError as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nOS error: ') + str(e), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nUnexpected error: ') + str(e), Gtk.MessageType.ERROR)

    # Function definitions for each of the handlers listed above
    def load_previously_mounted_images(self):
        if os.path.exists(globals.mount_list):
            try:
                with open(globals.mount_list, 'r') as file_previous_images:
                    previous_image_history = file_previous_images.readlines()
                    for line in previous_image_history:
                        previous_image = line.strip().split(',')
                        self.image_storage.append([previous_image[0], previous_image[1], previous_image[2]])
                os.remove(globals.mount_list)
            except IOError as e:
                log.write(globals.mount_log, _('Error loading history.\nOS error(%s): %s' % (e.errno, e.strerror)))
            except Exception as e:
                log.write(globals.mount_log, _('Error loading history.\nUnexpected error: %s' % str(e)))

    def load_mount_history(self):
        self.history_array = []
        if os.path.exists(globals.history_list):
            try:
                with open(globals.history_list, 'r') as file_history:
                    self.mount_history = file_history.readlines()
                    for line in self.mount_history:
                        self.history_storage.append([line.strip()])
                        self.history_array.append(line.strip())
            except IOError as e:
                log.write(globals.mount_log, _('Error loading history.\nOS error(%s): %s' % (e.errno, e.strerror)))
            except Exception as e:
                log.write(globals.mount_log, _('Error loading history.\nUnexpected error: %s' % str(e)))

    def create_settings_directory(self):
        # Create settings directory if not present
        if not os.path.exists(globals.settings_directory):
            try:
                os.mkdir(globals.settings_directory)
            except OSError as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error creating settings directory.\nOS error(%s): %s' % (e.errno, e.strerror)), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error creating settings directory.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def create_settings_file(self):
        # Create the setting file if it doesn't exist
        if not os.path.exists(globals.settings_file):
            try:
                with open(globals.settings_file, 'w') as settings_object:
                    mount_point_setting = '[mount_options]\nmount_point: %s' % globals.home_directory
                    settings_object.write(mount_point_setting)
                    log.write(globals.mount_log, _('New settings file created at %s' % globals.settings_file))
            except OSError as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error creating settings file.\nOS error(%s): %s' % (e.errno, e.strerror)), Gtk.MessageType.ERROR)
            except Exception as e:
                messagebox.show(self.builder.get_object('main_window'), _('Error creating settings file.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def set_icons_and_text(self):
        # Set the Icons and Text
        main_window = self.builder.get_object('main_window')
        main_window.set_title(f'{globals.assembly_title} {globals.assembly_version}')

        # Set button images and labels
        browse_button = self.builder.get_object('button_browse')
        browse_button.set_image(Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.MENU))
        browse_button.set_label(_('Browse...'))

        mount_button = self.builder.get_object('button_mount')
        mount_button.set_image(Gtk.Image.new_from_icon_name("drive-harddisk", Gtk.IconSize.MENU))
        mount_button.set_label(_('Mount'))

        checksum_button = self.builder.get_object('button_checksum')
        checksum_image = Gtk.Image.new_from_file(globals.image_checksum_button)
        checksum_button.set_image(checksum_image)
        checksum_button.set_label(_('Checksum'))

        burn_button = self.builder.get_object('button_burn')
        burn_image = Gtk.Image.new_from_file(globals.image_burn_button)
        burn_button.set_image(burn_image)
        burn_button.set_label(_('Burn'))

        unmount_button = self.builder.get_object('button_unmount')
        unmount_button.set_image(Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.MENU))
        unmount_button.set_label(_('Unmount'))

        # Set labels
        self.builder.get_object('button_view_log').set_label(_('View Log'))
        self.builder.get_object('button_delete_log').set_label(_('Delete Log'))
        self.builder.get_object('label_select_image').set_label(_('Select Image'))
        self.builder.get_object('label_selected_image').set_label(_('No Image Selected'))
        self.builder.get_object('progressbar_hash').set_text(_('No Checksum Generated'))
        self.builder.get_object('label_selected_mount_point').set_label(_('No Mount Point Selected'))
        self.builder.get_object('frame_mounted_images').set_label(_('Mounted Images:'))
        self.builder.get_object('label_drag_prompt').set_label(_('Drag image files into above window to quickly mount'))

        # Modify font descriptions
        pango_desc = Pango.FontDescription('8')
        self.builder.get_object('label_selected_image').modify_font(pango_desc)
        self.builder.get_object('progressbar_hash').modify_font(pango_desc)
        self.builder.get_object('label_selected_mount_point').modify_font(pango_desc)
        self.builder.get_object('label_drag_prompt').modify_font(pango_desc)

    def set_mounted_image_treeview(self):
        # Set treeview for images
        self.treeview = self.builder.get_object('treeview_mounted_images')

        # Use CSS for font styling instead of modify_font
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"* { font-family: 'sans'; font-size: 8pt; }")
        context = self.treeview.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.treeview.set_model(self.image_storage)

        # Create columns
        renderer_text = Gtk.CellRendererText()
        self.column_mount_point = Gtk.TreeViewColumn(_('Mount Point'), renderer_text, text=0)
        self.column_image_file = Gtk.TreeViewColumn(_('Image File'), renderer_text, text=1)
        self.column_fuse = Gtk.TreeViewColumn('Fuse', renderer_text, text=2)

        # Add sorting
        self.column_mount_point.set_sort_column_id(0)
        self.column_image_file.set_sort_column_id(1)

        # Append columns
        self.treeview.append_column(self.column_mount_point)
        self.treeview.append_column(self.column_image_file)
        self.treeview.append_column(self.column_fuse)

        # Set Drag and Drop
        # Ensure self.drop_targets is correctly defined as a list of Gtk.TargetEntry objects
        # Example:
        # self.drop_targets = [Gtk.TargetEntry.new("text/plain", Gtk.TargetFlags.OTHER_APP, 0)]
        target_entries = [Gtk.TargetEntry.new(target, flags, info) for target, flags, info in self.drop_targets]
        self.treeview.drag_dest_set(Gtk.DestDefaults.ALL, target_entries, Gdk.DragAction.DEFAULT | Gdk.DragAction.COPY)

    def set_history_entry(self):
        # Set entry for history
        comboentry_image = self.builder.get_object('comboentry_image')
        comboentry_image.set_model(self.history_storage)
        comboentry_image.set_entry_text_column(0)

    def set_storage_lists(self):
        # Set storage
        self.image_storage = Gtk.ListStore(str, str, str)  # Mounted image storage
        self.history_storage = Gtk.ListStore(str)

    def comboentry_image_key_release(self, comboentry, event):
        key = Gdk.keyval_name(event.keyval)
        if key == 'Return':
            self.verify_image()

    def comboentry_image_changed(self, comboentry):
        if self.builder.get_object('comboentry_image').get_active() != -1:
            self.verify_image()

    def button_browse_clicked(self, button):
        self.select_and_verify_image()

    def button_checksum_clicked(self, button):
        # Compute the checksum on an independent thread
        self.abort = False
        if self.builder.get_object('button_checksum').get_label() == _('Checksum'):
            selected_image = self.builder.get_object('label_selected_image').get_label()
            self.builder.get_object('button_checksum').set_label(_('Cancel'))

            GLib.idle_add(self.gtk_iteration)
            checksum = filehash.checksum()
            log.write(globals.mount_log, _('Checksum generation started...'))
            if self.builder.get_object('radiobutton_md5').get_active():
                threading.Thread(target=checksum.computemd5, args=(selected_image,)).start()
            else:
                threading.Thread(target=checksum.computesha1, args=(selected_image,)).start()

            while checksum.hash == _('Calculating, please wait...'):
                if self.abort:
                    self.builder.get_object('progressbar_hash').set_text(_('No Checksum Generated'))
                    self.builder.get_object('progressbar_hash').set_fraction(0)
                    break
                GLib.idle_add(self.gtk_iteration)
                time.sleep(0.1)
                self.builder.get_object('progressbar_hash').set_fraction(checksum.progress)
                self.builder.get_object('progressbar_hash').set_text(checksum.hash)
            if not self.abort:
                log.write(globals.mount_log, _('%s:%s' % (selected_image, checksum.hash)))
        else:  # Cancel
            self.abort = True
            log.write(globals.mount_log, _('Checksum generation aborted!'))
            self.builder.get_object('button_checksum').set_label(_('Checksum'))

    def select_and_verify_image(self):
        if self.select_image():
            self.verify_image()

    def select_image(self):
        is_file_selected = False
        dialog = Gtk.FileChooserDialog(_('Open Image..'),
                       None,
                       Gtk.FileChooserAction.OPEN,
                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            comboentry_image = self.builder.get_object('comboentry_image')
            comboentry_image.get_child().set_text(dialog.get_filename())
            is_file_selected = True
        dialog.destroy()
        return is_file_selected

    def verify_image(self, image=''):
        if image == '':
            comboentry_image = self.builder.get_object('comboentry_image')
            selected_file = comboentry_image.get_active_text()
        else:
            selected_file = image
        # First, ensure that the file exists
        if not os.path.exists(selected_file):
            messagebox.show(self.builder.get_object('main_window'), _('File not found. \nPlease check source exists.'), Gtk.MessageType.ERROR)
            self.builder.get_object('label_selected_image').set_label(_('No Image Selected'))
            self.builder.get_object('button_mount').set_sensitive(False)
            self.builder.get_object('button_checksum').set_sensitive(False)
            self.builder.get_object('button_burn').set_sensitive(False)
            return False
        # Next, ensure it's a supported image
        if selected_file.lower().endswith(('.iso', '.img', '.bin', '.mdf', '.nrg')):
            self.builder.get_object('label_selected_image').set_label(selected_file)
            self.builder.get_object('button_mount').set_sensitive(True)
            self.builder.get_object('button_checksum').set_sensitive(True)
            self.builder.get_object('button_burn').set_sensitive(True)
            # Loop method only supports ISO and IMG, so...
            if selected_file.lower().endswith(('.iso', '.img')):
                self.builder.get_object('radiobutton_loop').set_sensitive(True)
            else:
                self.builder.get_object('radiobutton_loop').set_sensitive(False)
                self.builder.get_object('radiobutton_fuse').set_active(True)
            return True
        messagebox.show(self.builder.get_object('main_window'), _('File does not appear to be a compatible Image. \nPlease check source.'), Gtk.MessageType.ERROR)
        self.builder.get_object('label_selected_image').set_label(_('No Image Selected'))
        self.builder.get_object('button_mount').set_sensitive(False)
        self.builder.get_object('button_checksum').set_sensitive(False)
        self.builder.get_object('button_burn').set_sensitive(False)
        return False


    def button_view_log_clicked(self, button):
        if os.path.exists(globals.mount_log):
            subprocess.Popen(['xdg-open', globals.mount_log])
        else:
            messagebox.show(self.builder.get_object('main_window'), _('%s not found.' % globals.mount_log), Gtk.MessageType.INFO)

    def button_delete_log_clicked(self, button):
        if os.path.exists(globals.mount_log):
            response = messagebox.show(self.builder.get_object('main_window'), _('Are you sure you wish to delete the log?'), Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO)
            if response == Gtk.ResponseType.YES:
                try:
                    os.remove(globals.mount_log)
                except OSError as e:
                    log.write(globals.mount_log, _('Error deleting log.\nOS error(%s): %s' % (e.errno, e.strerror)))
                except Exception as e:
                    log.write(globals.mount_log, _('Error deleting log.\nUnexpected error: %s' % str(e)))

    def button_mount_clicked(self, button):
        try:
            label_selected_image = self.builder.get_object('label_selected_image').get_label()
            radiobutton_fuse = self.builder.get_object('radiobutton_fuse').get_active()
            imageaction.mount(label_selected_image, self.image_storage, self.history_storage, self.history_array, radiobutton_fuse)
        except OSError as e:
            messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nOS error(%s): %s' % (e.errno, e.strerror)), Gtk.MessageType.ERROR)
        except Exception as e:
            messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def treeview_mounted_images_cursor_changed(self, treeview):
        # First get the tree view selection
        self.mounted_image_selection = self.treeview.get_selection()
        # Get the TreeModel and TreeIter of our selection
        (self.model, self.iter) = self.mounted_image_selection.get_selected()
        label_selected_mount_point = self.builder.get_object('label_selected_mount_point')
        label_selected_mount_point.set_label(self.model.get_value(self.iter, 0))
        self.is_mounted_image_fuse = self.model.get_value(self.iter, 2)
        # Allow user to unmount
        self.builder.get_object('button_unmount').set_sensitive(True)

    def button_unmount_clicked(self, button):
        try:
            label_selected_mount_point = self.builder.get_object('label_selected_mount_point').get_label()
            imageaction.unmount(label_selected_mount_point, self.is_mounted_image_fuse, self.image_storage, self.iter)
            self.builder.get_object('label_selected_mount_point').set_label(_('No Mount Point Selected'))
            self.builder.get_object('button_unmount').set_sensitive(False)
        except Exception as e:
            messagebox.show(self.builder.get_object('main_window'), _('Error unmounting image.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def button_burn_clicked(self, button):
        try:
            label_selected_image = self.builder.get_object('label_selected_image').get_label()
            radiobutton_brasero = self.builder.get_object('radiobutton_brasero').get_active()
            imageaction.burn(label_selected_image, radiobutton_brasero)
        except Exception as e:
            messagebox.show(self.builder.get_object('main_window'), _('Error burning image.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def button_about_clicked(self, button):
        aboutbox.show(self.builder.get_object('main_window'))

    def treeview_mounted_images_drag_data_recieved(self, widget, context, x, y, selection, info, timestamp):
        files = selection.get_data().decode().split('\n')
        for file in files:
            if not file:
                continue

            file = file.strip().replace('%20', ' ')
            if file.startswith('file:///') and os.path.isfile(file[7:]):
                if self.verify_image(file[7:]):
                    try:
                        label_selected_image = self.builder.get_object('label_selected_image').get_label()
                        radiobutton_fuse = self.builder.get_object('radiobutton_fuse').get_active()
                        imageaction.mount(label_selected_image, self.image_storage, self.history_storage, self.history_array, radiobutton_fuse)
                    except OSError as e:
                        messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nOS error(%s): %s' % (e.errno, e.strerror)), Gtk.MessageType.ERROR)
                    except Exception as e:
                        messagebox.show(self.builder.get_object('main_window'), _('Error mounting image.\nUnexpected error: %s' % str(e)), Gtk.MessageType.ERROR)

    def treeview_mounted_images_row_activated(self, treeview, path, column):
        label_selected_mount_point = self.builder.get_object('label_selected_mount_point').get_label()
        imageaction.browse(label_selected_mount_point)

    def destroy(self, window):
        self.image_storage.foreach(self.clean_up)
        log.write(globals.mount_log, _('Application closed!'))
        Gtk.main_quit()

    def clean_up(self, model, path, iter):
        response = messagebox.show(self.builder.get_object('main_window'), _('%s is still mounted.\nDo you wish to unmount it before exiting?' % model.get_value(iter, 1)), Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO)
        if response == Gtk.ResponseType.YES:
            try:
                imageaction.unmount(model.get_value(iter, 0), model.get_value(iter, 2), self.image_storage, iter, True)
            except Exception as e:
                log.write(globals.mount_log, _('Error unmounting image.\nUnexpected error: %s' % str(e)))
        else: # Write the history to file for loading later
            try:
                with open(globals.mount_list, 'a') as mount_file:
                    string = '%s,%s,%s' % (model.get_value(iter, 0), model.get_value(iter, 1), model.get_value(iter, 2))
                    mount_file.write('%s\n' % string)
            except IOError as e:
                log.write(globals.mount_log, _('Error saving unmounted images to file.\nOS error(%s): %s' % (e.errno, e.strerror)))
            except Exception as e:
                log.write(globals.mount_log, _('Error saving unmounted images to file\nUnexpected error: %s' % str(e)))
        return False

def gtk_iteration():
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)

if __name__ == '__main__':
    parameter = ''
    if len(sys.argv) > 1:
        parameter = sys.argv[1]
    app = MainWindow(parameter)
    Gtk.main()






