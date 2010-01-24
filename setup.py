#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name="pardus-network-manager-gtk",
      version="0.1.2",
      packages = ["network_manager_gtk", "asma.addons"],
      scripts = ["network-manager-gtk.py"],
      description= "Pardus Network Manager's gtk port",
      author="Rıdvan Örsvuran",
      author_email="flasherdn@gmail.com"
)
