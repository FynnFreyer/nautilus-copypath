# ----------------------------------------------------------------------------------------
# nautilus-copypath - Quickly copy file paths to the clipboard from Nautilus.
# Copyright (C) Ronen Lapushner 2017-2018.
# Distributed under the GPL-v3+ license. See LICENSE for more information
# ----------------------------------------------------------------------------------------

import os

from dataclasses import dataclass
from platform import system
from typing import Union

import gi

gi.require_version('Nautilus', '4.0')
gi.require_version('Gdk', '4.0')

from gi.repository import Nautilus, GObject, Gdk


@dataclass  # gives nice default __repr__
class CopyPathExtensionSettings:
    """
    Configuration object for the nautilus-copypath extension.
    Can be automatically populated from ``NAUTILUS_COPYPATH_*`` environment variables.
    """

    @staticmethod
    def __cast_env_var(name: str, default=None) -> Union[str, bool, None]:
        """
        Try to cast the value of ${name} to a python object.

        :param name: The name of the environment variable. E.g., "``NAUTILUS_COPYPATH_WINPATH``".
        :param default: Optionally, a default value if the environment variable is not set. Standard is ``None``.
        :return: The value of the environment variable. Will be cast to bool for integers and certain strings.
        """

        value = os.environ.get(name, default=default)

        # define a mapping for common boolean keywords
        cast_map = {
            'true': True,
            'yes': True,
            'y': True,
            'false': False,
            'no': False,
            'n': False,
        }

        # if the env var is defined, i.e. different from the default
        if value != default:
            # we try two different casts to boolean
            # first we cast to bool via int, if this fails,
            # secondly we fall back to our cast map,
            # otherwise just return the string
            try:
                value = bool(int(value))
            except ValueError:
                try:
                    value = cast_map[value.lower()]
                except KeyError:
                    pass

        return value

    def __init__(self):
        is_windows = system() == 'Windows'
        self.winpath = self.__cast_env_var('NAUTILUS_COPYPATH_WINPATH', default=is_windows)
        self.sanitize_paths = self.__cast_env_var('NAUTILUS_COPYPATH_SANITIZE_PATHS', default=True)
        self.quote_paths = self.__cast_env_var('NAUTILUS_COPYPATH_QUOTE_PATHS', default=False)

    winpath: bool
    """
    Whether to assume Windows-style paths. Default is determined by result of ``platform.system()``.

    Controlled by the ``NAUTILUS_COPYPATH_WINPATH`` environment variable.
    """

    sanitize_paths: bool = True
    """
    Whether to escape paths. Defaults to true.

    Controlled by the ``NAUTILUS_COPYPATH_SANITIZE_PATHS`` environment variable.
    """

    quote_paths: bool = False
    """
    Whether to surround paths with quotes. Defaults to false.

    Controlled by the ``NAUTILUS_COPYPATH_QUOTE_PATHS`` environment variable.
    """


class CopyPathExtension(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        # Initialize clipboard
        self.clipboard = Gdk.Display.get_default().get_clipboard()
        self.config = CopyPathExtensionSettings()

    def __sanitize_path(self, path):
        # Replace spaces and parenthesis with their Linux-compatible equivalents. 
        return path.replace(' ', '\\ ').replace('(', '\\(').replace(')', '\\)')

    def __copy_files_path(self, menu, files):
        pathstr = None

        # Get the paths for all the files.
        # Also, strip any protocol headers, if required.
        paths = [fileinfo.get_location().get_path()
                 for fileinfo in files]

        if self.config.sanitize_paths:
            paths = [self.__sanitize_path(path) for path in paths]

        # Append to the path string
        if len(files) > 1:
            pathstr = '\n'.join(paths)
        elif len(files) == 1:
            pathstr = paths[0]

        # Set clipboard text
        if pathstr is not None:
            self.clipboard.set(pathstr)

    def __copy_dir_path(self, menu, path):
        if path is not None:
            pathstr = path.get_location().get_path()
            if self.config.sanitize_paths:
                pathstr = self.__sanitize_path(pathstr)
            self.clipboard.set(pathstr)

    def get_file_items(self, files):
        # If there are many items to copy, change the label
        # to reflect that.
        if len(files) > 1:
            item_label = 'Copy Paths'
        else:
            item_label = 'Copy Path'

        item_copy_path = Nautilus.MenuItem(
            name='PathUtils::CopyPath',
            label=item_label,
            tip='Copy the full path to the clipboard'
        )
        item_copy_path.connect('activate', self.__copy_files_path, files)

        return item_copy_path,

    def get_background_items(self, file):
        item_copy_dir_path = Nautilus.MenuItem(
            name='PathUtils::CopyCurrentDirPath',
            label='Copy Directory Path',
            tip='''Copy the current directory's path to the clipboard'''
        )

        item_copy_dir_path.connect('activate', self.__copy_dir_path, file)

        return item_copy_dir_path,
