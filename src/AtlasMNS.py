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
import signal
import ripe.atlas.cousteau
import ssl
import socket
import sys

import AtlasMNSLogger


# ###### Scheduler database columns #########################################
ExperimentSchedule_Identifier=0
ExperimentSchedule_State=1
ExperimentSchedule_LastChange=2
ExperimentSchedule_AgentMeasurementTime=3
ExperimentSchedule_AgentHostIP=4
ExperimentSchedule_AgentTrafficClass=5
ExperimentSchedule_AgentFromIP=6
ExperimentSchedule_ProbeID=7
ExperimentSchedule_ProbeMeasurementID=8
ExperimentSchedule_ProbeCost=9
ExperimentSchedule_ProbeHostIP=10
ExperimentSchedule_ProbeFromIP=11
ExperimentSchedule_Info=12


# ###### Signal handler #####################################################
breakDetected = False
def signalHandler(signalNumber, frame):
   global breakDetected
   breakDetected = True


# ###### AtlasMNS class #####################################################
class AtlasMNS:

   # ###### Constructor #####################################################
   def __init__(self):
      # ====== Set defaults =================================================
      self.configuration = {
         'scheduler_dbserver':   'localhost',
         'scheduler_dbport':     '5432',
         'scheduler_dbuser':     'scheduler',
         'scheduler_dbpassword': None,
         'scheduler_database':   'atlasmsdb',
         'scheduler_cafile':     'None',

         'results_dbserver':     'localhost',
         'results_dbport':       '27017',
         'results_dbuser':       'importer',
         'results_dbpassword':   None,
         'results_database':     'atlasmnsdb',
         'results_cafile':       'None',

         'atlas_api_key':        None
      }
      signal.signal(signal.SIGINT, signalHandler)
      signal.signal(signal.SIGTERM, signalHandler)


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
            'url_path': '/api/v2/anchors'
         }
      )
      result = collections.namedtuple('Result', 'success response')
      (result.success, result.response) = atlas_request.get()

      return (result.success == True)


   # ###### Start RIPE Atlas measurement ####################################
   def startRIPEAtlasMeasurement(self, source, measurement):
      AtlasMNSLogger.trace('Creating ' + measurement.measurement_type + ' measurement for ' +
                           'Probe #' + str(source.get_value()) + ' to ' + str(measurement.target) + ' ...')
      atlas_request = ripe.atlas.cousteau.AtlasCreateRequest(
         start_time   = datetime.datetime.utcnow(),
         key          = self.configuration['atlas_api_key'],
         sources      = [ source ],
         measurements = [ measurement ],
         is_oneoff    = True
      )
      ( is_success, response ) = atlas_request.create()
      if is_success:
         measurementID = response['measurements'][0]
         AtlasMNSLogger.trace('Created ' + measurement.measurement_type + ' measurement: ' +
                              'Probe #' + str(source.get_value()) + ' to ' + str(measurement.target) +
                              ' -> Measurement #' + str(measurementID))
         return measurementID
      else:
         AtlasMNSLogger.warning('Creating ' + measurement.measurement_type + ' measurement for ' +
                                'Probe #' + str(source.get_value()) + ' to ' + str(measurement.target) +
                                ' failed: ' + str(response))
         return None


   # ###### Stop RIPE Atlas measurement #####################################
   def stopRIPEAtlasMeasurement(self, measurementID):
      atlas_request = ripe.atlas.cousteau.AtlasStopRequest(
         key    = self.configuration['atlas_api_key'],
         msm_id = measurementID
      )
      ( is_success, response ) = atlas_request.create()
      if is_success:
         AtlasMNSLogger.trace('Stopped Measurement #' + str(measurementID))
         return True
      else:
         AtlasMNSLogger.warning('Stopping Measurement #' + str(measurementID) +
                                ' failed: ' + str(response))
         return False


   # ###### Create RIPE Atlas Ping measurement ##############################
   def createRIPEAtlasPingMeasurement(self, probeID, targetAddress, description):
      source = ripe.atlas.cousteau.AtlasSource(
         type      = 'probes',
         value     = str(probeID),
         requested = 1
      )
      # Attributes documentation:
      # https://atlas.ripe.net/docs/api/v2/manual/measurements/types/base_attributes.html
      # https://atlas.ripe.net/docs/api/v2/reference/#!/measurements/Ping_Type_Measurement_List_GET
      measurement = ripe.atlas.cousteau.Ping(
         af          = targetAddress.version,
         target      = str(targetAddress),
         description = description,
         is_oneoff   = True,
         packets     = 1,
         paris       = 1,
         size        = 16   # size without IP and ICMP headers
      )
      return self.startRIPEAtlasMeasurement(source, measurement)


   # ###### Create RIPE Atlas Traceroute measurement ########################
   def createRIPEAtlasTracerouteMeasurement(self, probeID, targetAddress, description):
      source = ripe.atlas.cousteau.AtlasSource(
         type      = 'probes',
         value     = str(probeID),
         requested = 1
      )
      # Attributes documentation:
      # https://atlas.ripe.net/docs/api/v2/manual/measurements/types/base_attributes.html
      # https://atlas.ripe.net/docs/api/v2/reference/#!/measurements/Traceroute_Type_Measurement_List_GET
      measurement = ripe.atlas.cousteau.Traceroute(
         af          = targetAddress.version,
         target      = str(targetAddress),
         description = description,
         protocol    = 'ICMP',
         is_oneoff   = True,
         packets     = 1,
         paris       = 1,
         size        = 16   # size without IP and ICMP headers
      )
      return self.startRIPEAtlasMeasurement(source, measurement)


   # ###### Obtain measurement results ######################################
   def downloadRIPEAtlasMeasurementResults(self, measurementID):
      AtlasMNSLogger.trace('Downloading results for Measurement #' +
                           str(measurementID) + ' ...')
      (is_success, results) = ripe.atlas.cousteau.AtlasResultsRequest(
         msm_id = measurementID
      ).create()
      if is_success:
         return (True, results)
      else:
         AtlasMNSLogger.warning('Downloading results for Measurement #' +
                                str(measurementID) + ' failed: ' + str(results))
         return (False, None)


   # ###### Print measurement results #######################################
   def printRIPEAtlasMeasurementResults(self, results):
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
         if self.configuration['scheduler_cafile'] == 'IGNORE':   # Ignore TLS certificate
            AtlasMNSLogger.warning('TLS certificate check for PostgreSQL scheduler database is turned off!')
            self.scheduler_dbConnection = psycopg2.connect(host=str(self.configuration['scheduler_dbserver']),
                                                           port=str(self.configuration['scheduler_dbport']),
                                                           user=str(self.configuration['scheduler_dbuser']),
                                                           password=str(self.configuration['scheduler_dbpassword']),
                                                           dbname=str(self.configuration['scheduler_database']),
                                                           sslmode='require')
         elif self.configuration['scheduler_cafile'] == 'None':   # Use default CA settings
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


   # ###### Query schedule from scheduler database ##########################
   def querySchedule(self):
      # ====== Query database ===============================================
      AtlasMNSLogger.trace('Querying schedule ...')
      try:
         self.scheduler_dbCursor.execute("""
SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
FROM ExperimentSchedule
ORDER BY LastChange ASC;
""")
         table = self.scheduler_dbCursor.fetchall()
      except Exception as e:
         AtlasMNSLogger.warning('Failed to query schedule: ' + str(e))
         return []

      # ====== Provide result as list of dictionaries =======================
      schedule = []
      for row in table:
         schedule.append({
            'Identifier':           row[0],
            'State':                row[1],
            'LastChange':           row[2],
            'AgentMeasurementTime': row[3],
            'AgentHostIP':          row[4],
            'AgentTrafficClass':    row[5],
            'AgentFromIP':          row[6],
            'ProbeID':              row[7],
            'ProbeMeasurementID':   row[8],
            'ProbeCost':            row[9],
            'ProbeHostIP':          row[10],
            'ProbeFromIP':          row[11],
            'Info':                 row[12]
         })
      print(schedule)
      return schedule


   # ###### Update schedule in scheduler database ###########################
   def updateScheduledEntry(self, scheduledEntry):
      AtlasMNSLogger.trace('Updating scheduled entry ...')
      try:
         self.scheduler_dbCursor.execute(
            """
            UPDATE ExperimentSchedule
            SET
               State=%s,LastChange=NOW(),AgentHostIP=%s,AgentTrafficClass=%s, AgentFromIP=%s,ProbeID=%s,ProbeMeasurementID=%s,ProbeCost=%s,ProbeHostIP=%s,ProbeFromIP=%s,Info=%s
            WHERE
               Identifier = %s;
            """,  [
               scheduledEntry['State'],
               scheduledEntry['AgentHostIP'],
               scheduledEntry['AgentTrafficClass'],
               scheduledEntry['AgentFromIP'],
               scheduledEntry['ProbeID'],
               scheduledEntry['ProbeMeasurementID'],
               scheduledEntry['ProbeCost'],
               scheduledEntry['ProbeHostIP'],
               scheduledEntry['ProbeFromIP'],
               scheduledEntry['Info'],
               scheduledEntry['Identifier']
            ] )
         self.scheduler_dbConnection.commit()
      except Exception as e:
         AtlasMNSLogger.warning('Failed to update schedule: ' + str(e))
         self.scheduler_dbConnection.rollback()
         return False


   # ###### Connect to MongoDB results database #############################
   def connectToResultsDB(self):
      AtlasMNSLogger.info('Connecting to MongoDB results database at ' + self.configuration['results_dbserver'] + ' ...')
      try:
         if self.configuration['results_cafile'] == 'IGNORE':   # Ignore TLS certificate
            AtlasMNSLogger.warning('TLS certificate check for MongoDB results database is turned off!')
            results_dbConnection = pymongo.MongoClient(host=str(self.configuration['results_dbserver']),
                                                       port=int(self.configuration['results_dbport']),
                                                       ssl=True, ssl_cert_reqs=ssl.CERT_NONE)
         elif self.configuration['results_cafile'] == 'None':   # Use default CA settings
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


   # ###### Connect to MongoDB results database #############################
   def importResults(self, scheduledEntry, results):
      experiment = {
         'timestamp':            datetime.datetime.utcnow(),
         'identifier':           scheduledEntry['Identifier'],
         'agentMeasurementTime': scheduledEntry['AgentMeasurementTime'],
         'agentHostIP':          scheduledEntry['AgentHostIP'],
         'agentTrafficClass':    scheduledEntry['AgentTrafficClass'],
         'agentFromIP':          scheduledEntry['AgentFromIP'],
         'probeID':              scheduledEntry['ProbeID'],
         'probeMeasurementID':   scheduledEntry['ProbeMeasurementID'],
         'probeCost':            scheduledEntry['ProbeCost'],
         'probeHostIP':          scheduledEntry['ProbeHostIP'],
         'probeFromIP':          scheduledEntry['ProbeFromIP']
      }
      try:
         self.results_db['ripeatlastraceroute'].insert(results)
         self.results_db['atlasmns'].insert(experiment)
         return True
      except Exception as e:
         AtlasMNSLogger.error('Unable to import results: ' + str(e))
         return False
