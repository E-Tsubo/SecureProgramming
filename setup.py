# -*- coding: utf-8 -*-

# python setup.py py2exe

from distutils.core import setup
import py2exe

option = {
  "compressed"    :1,
  "optimize"      :2,
  "bundle_files"  :1
}

setup(
  options = {
    "py2exe"      :option
  },

  console = [
    {"script"     :"processMonitor.py"},
    {"script"     :"KeyLogger.py"}
  ],

  zipfile = None
)
