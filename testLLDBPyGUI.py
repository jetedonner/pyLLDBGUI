#!/usr/bin/env python3

from inspect import getfile

import os

import lldb
from lldbsuite.test.decorators import *
from lldbsuite.test.lldbtest import *
import lldbsuite.test.lldbutil as lldbutil

# Assuming you have an instance of the class
class_instance = TestBase()

# Get the file path of the module defining the class
module_path = getfile(class_instance.__class__)
print(f"Path of module defining TestBase: {module_path}")