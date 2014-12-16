# This file is part of Seastorm
# Copyright 2014 Jakob Kallin

import os
from os.path import join

def watch(watchPath, emit):
  lastModified = {}
  
  def poll():
    # Check existing files for changes.
    try:
      for filename in os.listdir(watchPath):
        filePath = join(watchPath, filename)
        if os.path.isfile(filePath):
          fileTime = os.stat(filePath).st_mtime
          if filename not in lastModified or fileTime > lastModified[filename]:
            emit(filename)
          
          lastModified[filename] = fileTime
    except:
      # Ignore errors and let the next poll try again. This can happen if the
      # file folder is deleted, causing `listdir` to fail.
      pass
    
    # Check if previously existing files have been removed.
    for filename in lastModified.keys():
      filePath = join(watchPath, filename)
      if not os.path.isfile(filePath):
        emit(filename)
        lastModified.pop(filename, None)
  
  return poll