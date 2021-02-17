#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#  =================================================================
#           #     #                 #     #
#           ##    #   ####   #####  ##    #  ######   #####
#           # #   #  #    #  #    # # #   #  #          #
#           #  #  #  #    #  #    # #  #  #  #####      #
#           #   # #  #    #  #####  #   # #  #          #
#           #    ##  #    #  #   #  #    ##  #          #
#           #     #   ####   #    # #     #  ######     #
#
#        ---   The NorNet Testbed for Multi-Homed Systems  ---
#                        https://www.nntb.no
#  =================================================================
#
#  High-Performance Connectivity Tracer (HiPerConTracer)
#  Copyright (C) 2015-2021 by Thomas Dreibholz
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  Contact: dreibh@simula.no


import atexit
import colorlog
import datetime
import logging
import logging.config
import lzma
import os


TRACE    = logging.DEBUG - 1
DEBUG    = logging.DEBUG
INFO     = logging.INFO
WARNING  = logging.WARNING
ERROR    = logging.ERROR
CRITICAL = logging.CRITICAL


# ###### Custom log level "TRACE" ###########################################
logging.addLevelName(TRACE, 'TRACE')

def trace(self, message, *args, **kwargs):
    self.log(TRACE, message, *args, **kwargs)
logging.Logger.trace = trace


# ###### Compressing log rotator ############################################
def CompressingRotator(source, dest):
   os.rename(source, dest)
   f_in = open(dest, 'rb')
   f_out = lzma.LZMAFile('%s.xz' % dest, 'wb')
   f_out.writelines(f_in)
   f_out.close()
   f_in.close()
   os.remove(dest)


# ###### Custom formatter with timestamp in microseconds ####################
class MicrosecondsTimestampLogFormatter(colorlog.ColoredFormatter):
   def formatTime(self, record, datefmt = None):
      t = datetime.datetime.fromtimestamp(record.created)
      if datefmt:
          s = t.strftime(datefmt)
      else:
          s = t.strftime("%Y-%m-%d %H:%M:%S.%f")
      return s


# ###### Logger class #######################################################
class AtlasMNSLogger:
   # ###### Constructor #####################################################
   def __init__(self,
                logLevel       = TRACE,
                logDirectory   = None,
                logFile        = None,
                logCompression = True):

      self.logFileName    = None
      self.logCompression = False

      if ((logDirectory != None) and (logFile != None)):
         self.logFileName    = os.path.join(logDirectory, logFile)
         self.logCompression = logCompression
         loggingHandler = {
            'level': 'TRACE',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'standard',
            'filename': self.logFileName,
            'when': 'S',
            'interval': 24*3600
         }
      else:
         loggingHandler = {
            'level': 'TRACE',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
         }

      self.loggingConfiguration = {
         'version': 1,
         'handlers': {
            'default': loggingHandler
         },
         'formatters': {
            'standard': {
               '()': MicrosecondsTimestampLogFormatter,
               'fmt': '%(log_color)s[%(asctime)s][%(levelname)s]: %(message)s',
               'style': '%',
               'datefmt': '%Y-%m-%d %H:%M:%S.%f',
               'log_colors': { 'TRACE':    'white',    # 37
                               'DEBUG':    'cyan',     # 36
                               'INFO':     'blue',     # 34
                               'WARNING':  'yellow',   # 33
                               'ERROR':    'red',      # 31
                               'CRITICAL': 'white,bg_red' }
            },
         },
         'root': {
            'level': 'TRACE',
            'handlers': ['default'],
         }
      }

      logging.config.dictConfig(self.loggingConfiguration)
      self.logger = logging.getLogger()
      if self.logCompression == True:
         for handler in self.logger.handlers[:]:
            handler.rotator = CompressingRotator

      atexit.register(self.cleanup)


   # ###### Destructor ######################################################
   def cleanup(self):
      self.doRollover(True)
      if self.logCompression == True:
         print('DEL: ' + self.logFileName)
         os.unlink(self.logFileName)


   # ###### Perform log rollover ############################################
   def doRollover(self, onlyIfCompressing = False):
     if ((onlyIfCompressing == False) or (self.logCompression == True)):
         for handler in self.logger.handlers[:]:
            if hasattr(handler, 'doRollover'):
               handler.doRollover()


# ###### Create log entry ###################################################
def log(level, message, *args, **kwargs):
   logging.getLogger().log(level, message, *args, **kwargs)

# ###### Create log entry ###################################################
def trace(message, *args, **kwargs):
   logging.getLogger().trace(*args, message, **kwargs)

# ###### Create log entry ###################################################
def debug(message, *args, **kwargs):
   logging.getLogger().debug(*args, message, **kwargs)

# ###### Create log entry ###################################################
def info(message, *args, **kwargs):
   logging.getLogger().info(*args, message, **kwargs)

# ###### Create log entry ###################################################
def warning(message, *args, **kwargs):
   logging.getLogger().warning(*args, message, **kwargs)

# ###### Create log entry ###################################################
def error(message, *args, **kwargs):
   logging.getLogger().error(*args, message, **kwargs)

# ###### Create log entry ###################################################
def critical(message, *args, **kwargs):
   logging.getLogger().critical(*args, message, **kwargs)
