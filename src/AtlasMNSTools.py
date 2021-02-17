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


import datetime
import ipaddress


TheEpoch = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)

# ###### Convert datetime object to microseconds time stamp #################
def timeStampToDatetime(ts):
   dt = TheEpoch + datetime.timedelta(microseconds = ts)
   return dt


# ###### Convert datetime object to microseconds time stamp #################
def datatimeToTimeStamp(dt):
   diff = dt - TheEpoch
   ts = diff.days * (24 * 60 * 60 * 1000000)
   ts = ts + diff.seconds * 1000000
   ts = ts + diff.microseconds
   return ts


# ###### Convert IP address to binary #######################################
def ipAddressToBinary(address):
   return address.packed


# ###### Convert binary to IP address #######################################
def binaryToIPAddress(binary):
   return ipaddress.ip_address(binary)


# ###### Return string of value, or empty string for None type ##############
def valueOrNoneString(value):
   if value != None:
      return str(value)
   else:
      return ''
