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
#  Copyright (C) 2015-2019 by Thomas Dreibholz
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

import collections
import configparser
import datetime
import io
import ipaddress
import os
import psycopg2
import pymongo
import re
import shutil
import ripe.atlas.cousteau
import ssl
import socket
import sys

import AtlasMNSLogger


class AtlasMNS:

   # ###### Constructor #####################################################
   def __init__(self):
      # ====== Set defaults =================================================
      self.configuration = {
         'scheduler_dbserver':   "localhost",
         'scheduler_dbport':     "5432",
         'scheduler_dbuser':     "scheduler",
         'scheduler_dbpassword': None,
         'scheduler_database':   "atlasmsdb",
         'scheduler_cafile':     "None",

         'results_dbserver':     "localhost",
         'results_dbport':       "27017",
         'results_dbuser':       "importer",
         'results_dbpassword':   None,
         'results_database':     "atlasmnsdb",
         'results_cafile':       "None",

         'atlas_api_key':        None
      }


   # ###### Load configuration ##############################################
   def loadConfiguration(self, configFileName):
      parsedConfigFile = configparser.RawConfigParser()
      parsedConfigFile.optionxform = str   # Make it case-sensitive!
      try:
         parsedConfigFile.readfp(io.StringIO(u'[root]\n' + open(configFileName, 'r').read()))
      except Exception as e:
         AtlasMNSLogger.error('Unable to read database configuration file' +  configFileName + ': ' + str(e))
         return False

      for parameterName in parsedConfigFile.options('root'):
         parameterValue = parsedConfigFile.get('root', parameterName)

         if parameterName == 'scheduler_dbserver':
            self.configuration['scheduler_dbserver'] = parameterValue
         elif parameterName == 'scheduler_dbport':
            self.configuration['scheduler_dbport'] = parameterValue
         elif parameterName == 'scheduler_dbuser':
            self.configuration['scheduler_dbuser'] = parameterValue
         elif parameterName == 'scheduler_dbpassword':
            self.configuration['scheduler_dbpassword'] = parameterValue
         elif parameterName == 'scheduler_database':
            self.configuration['scheduler_database'] = parameterValue
         elif parameterName == 'scheduler_cafile':
            self.configuration['scheduler_cafile'] = parameterValue

         elif parameterName == 'results_dbserver':
            self.configuration['results_dbserver'] = parameterValue
         elif parameterName == 'results_dbport':
            self.configuration['results_dbport'] = parameterValue
         elif parameterName == 'results_dbuser':
            self.configuration['results_dbuser'] = parameterValue
         elif parameterName == 'results_dbpassword':
            self.configuration['results_dbpassword'] = parameterValue
         elif parameterName == 'results_database':
            self.configuration['results_database'] = parameterValue
         elif parameterName == 'results_cafile':
            self.configuration['results_cafile'] = parameterValue

         elif parameterName == 'atlas_api_key':
            self.configuration['atlas_api_key'] = parameterValue

         else:
            AtlasMNSLogger.warning('Unknown parameter ' + parameterName + ' is ignored!')

      return True


   # ###### Connect to RIPE Atlas ###########################################
   def connectToRIPEAtlas(self):
      AtlasMNSLogger.info('Connecting to the RIPE Atlas server ...')

      if ((self.configuration['atlas_api_key'] == None) or
          (self.configuration['atlas_api_key'] == 'PROVIDE_ATLAS_API_KEY_HERE')):
         AtlasMNSLogger.error('No RIPE Atlas API Key specified!')
         return False

      atlas_request = ripe.atlas.cousteau.AtlasRequest(
         **{
            "url_path": "/api/v2/anchors"
         }
      )
      result = collections.namedtuple('Result', 'success response')
      (result.success, result.response) = atlas_request.get()

      return (result.success == True)


   # ###### Create Ping measurement #########################################
   def createRIPEAtlasPingMeasurement(self, probeID, targetAddress, description):
      measurement = ping4 = ripe.atlas.cousteau.Ping(
         af          = targetAddress.version,
         target      = str(targetAddress),
         description = description
      )
      source = ripe.atlas.cousteau.AtlasSource(
         type      = 'probes',
         value     = str(probeID),
         requested = 1
      )
      AtlasMNSLogger.trace("Creating Ping measurement: Probe #" +
                           str(probeID) + " to " + str(targetAddress))
      atlas_request = ripe.atlas.cousteau.AtlasCreateRequest(
         start_time   = datetime.datetime.utcnow(),
         key          = self.configuration['atlas_api_key'],
         measurements = [ measurement ],
         sources      = [ source ],
         is_oneoff    = True
      )
      ( is_success, response ) = atlas_request.create()
      if is_success:
         measurementID = response['measurements'][0]
         AtlasMNSLogger.trace("Created Ping measurement: Probe #" +
                              str(probeID) + " to " + str(targetAddress) +
                              " -> Measurement #" + str(measurementID))
         return measurementID
      else:
         AtlasMNSLogger.warning("Creating Ping measurement: Probe #" +
                                str(probeID) + " to " + str(targetAddress) +
                                " failed: " + str(response))
         return False


   # ###### Obtain measurement results ######################################
   def downloadMeasurementResults(self, measurementID):
      (is_success, results) = ripe.atlas.cousteau.AtlasResultsRequest(
         msm_id = measurementID
      ).create()
      if is_success:
         return results
         for result in results:
            probeID = int(result['prb_id'])
            probeIDs.add(probeID)
            print('- Result from Probe #' + str(probeID))
            print('  ', result)
      else:
         AtlasMNSLogger.warning("Obtaining results for Measurement #" +
                                str(measurementID) + " failed: " + str(results))
         return None


   # ###### Print measurement results #######################################
   def printMeasurementResults(self, results):
      probeIDs = set()
      print('Results:')
      for result in results:
         probeID = int(result['prb_id'])
         probeIDs.add(probeID)
         print('- Result from Probe #' + str(probeID))
         print('  ', result)
      print('Metadata:')
      for probeID in probeIDs:
         print('- Metadata for Probe #' + str(probeID))
         probe  = ripe.atlas.cousteau.Probe(id = probeID)
         print('  ', probe.country_code, probe.address_v4, probe.asn_v4, probe.address_v6, probe.asn_v6)


   # ###### Connect to PostgreSQL scheduler database ########################
   def connectToSchedulerDB(self):
      AtlasMNSLogger.info('Connecting to the PostgreSQL scheduler database at ' + self.configuration['scheduler_dbserver'] + ' ...')
      self.scheduler_dbCursor = None
      try:
         if self.configuration['scheduler_cafile'] == "IGNORE":   # Ignore TLS certificate
            AtlasMNSLogger.warning('TLS certificate check for PostgreSQL scheduler database is turned off!')
            self.scheduler_dbConnection = psycopg2.connect(host=str(self.configuration['scheduler_dbserver']),
                                                           port=str(self.configuration['scheduler_dbport']),
                                                           user=str(self.configuration['scheduler_dbuser']),
                                                           password=str(self.configuration['scheduler_dbpassword']),
                                                           dbname=str(self.configuration['scheduler_database']),
                                                           sslmode='require')
         elif self.configuration['scheduler_cafile'] == "None":   # Use default CA settings
            self.scheduler_dbConnection = psycopg2.connect(host=str(self.configuration['scheduler_dbserver']),
                                                           port=str(self.configuration['scheduler_dbport']),
                                                           user=str(self.configuration['scheduler_dbuser']),
                                                           password=str(self.configuration['scheduler_dbpassword']),
                                                           dbname=str(self.configuration['scheduler_database']),
                                                           sslmode='verify-ca')
         else:   # Use given CA
            self.scheduler_dbConnection = psycopg2.connect(host=str(self.configuration['scheduler_dbserver']),
                                                           port=str(self.configuration['scheduler_dbport']),
                                                           user=str(self.configuration['scheduler_dbuser']),
                                                           password=str(self.configuration['scheduler_dbpassword']),
                                                           dbname=str(self.configuration['scheduler_database']),
                                                           sslmode='verify-ca',
                                                           sslrootcert=self.configuration['scheduler_cafile'])
         self.scheduler_dbConnection.autocommit = False
      except Exception as e:
         AtlasMNSLogger.error('Unable to connect to the PostgreSQL scheduler database at ' +
               self.configuration['scheduler_dbserver'] + ': ' + str(e))
         return False

      self.scheduler_dbCursor = self.scheduler_dbConnection.cursor()
      return True


   # ###### Connect to MongoDB results database #############################
   def connectToResultsDB(self):
      AtlasMNSLogger.info('Connecting to MongoDB results database at ' + self.configuration['results_dbserver'] + ' ...')
      try:
         if self.configuration['results_cafile'] == "IGNORE":   # Ignore TLS certificate
            AtlasMNSLogger.warning('TLS certificate check for MongoDB results database is turned off!')
            results_dbConnection = pymongo.MongoClient(host=str(self.configuration['results_dbserver']),
                                                       port=int(self.configuration['results_dbport']),
                                                       ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
         elif self.configuration['results_cafile'] == "None":   # Use default CA settings
            results_dbConnection = pymongo.MongoClient(host=str(self.configuration['results_dbserver']),
                                                       port=int(self.configuration['results_dbport']),
                                                       ssl=True, ssl_cert_reqs=ssl.CERT_REQUIRED)
         else:   # Use given CA, requires PyMongo >= 3.4!
            results_dbConnection = pymongo.MongoClient(host=str(self.configuration['results_dbserver']),
                                                       port=int(self.configuration['results_dbport']),
                                                       ssl=True, ssl_cert_reqs=ssl.CERT_REQUIRED,
                                                       ssl_ca_certs=self.configuration['results_cafile'])
         self.results_db = results_dbConnection[str(self.configuration['results_database'])]
         self.results_db.authenticate(str(self.configuration['results_dbuser']),
                                      str(self.configuration['results_dbpassword']),
                                      mechanism='SCRAM-SHA-1')
      except Exception as e:
         AtlasMNSLogger.error('Unable to connect to the MongoDB results database at ' +
               self.configuration['results_dbserver'] + ': ' + str(e))
         return False

      return True
