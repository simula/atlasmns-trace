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

import collections
import configparser
import datetime
import io
import ipaddress
import os
import psycopg2
import pymongo
import re
import ripe.atlas.cousteau
import shutil
import signal
import socket
import ssl
import sys

import AtlasMNSLogger
import AtlasMNSTools


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
         'scheduler_dbuser':     'atlasmnsscheduler',
         'scheduler_dbpassword': None,
         'scheduler_database':   'atlasmsdb',
         'scheduler_cafile':     'None',

         'results_dbserver':     'localhost',
         'results_dbport':       '27017',
         'results_dbuser':       'atlasmnsimporter',
         'results_dbpassword':   None,
         'results_database':     'atlasmnsdb',
         'results_cafile':       'None',

         'atlas_api_key':        None
      }
      self.scheduler_dbConnection = None
      self.scheduler_dbCursor     = None
      self.results_dbConnection   = None
      self.results_db             = None
      signal.signal(signal.SIGINT, signalHandler)
      signal.signal(signal.SIGTERM, signalHandler)


   # ###### Load configuration ##############################################
   def loadConfiguration(self, configFileName):
      parsedConfigFile = configparser.RawConfigParser()
      parsedConfigFile.optionxform = str   # Make it case-sensitive!
      try:
         parsedConfigFile.readfp(io.StringIO(u'[root]\n' + open(configFileName, 'r').read()))
      except Exception as e:
         AtlasMNSLogger.error('Unable to read database configuration file ' +  configFileName + ': ' + str(e))
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
         key          = self.configuration['atlas_api_key'],
         sources      = [ source ],
         measurements = [ measurement ],
         is_oneoff    = True
      )

      # ====== Success ======================================================
      ( is_success, response ) = atlas_request.create()
      if is_success:
         measurementID = response['measurements'][0]
         AtlasMNSLogger.trace('Created ' + measurement.measurement_type + ' measurement: ' +
                              'Probe #' + str(source.get_value()) + ' to ' + str(measurement.target) +
                              ' -> Measurement #' + str(measurementID))
         return ( measurementID, None )

      # ====== Failure ======================================================
      else:
         # ====== Check for recoverable failure =============================
         detail = None
         try:
            detail = str(response['error']['errors'][0]['detail'])
         except:
            pass
         if ((detail != None) and (detail.find('We do not allow more than ') == 0)):
            AtlasMNSLogger.trace('Retry again later: ' + detail)
            return ( None, None )

         # ====== Non-recoverable failure ===================================
         AtlasMNSLogger.warning('Creating ' + measurement.measurement_type + ' measurement for ' +
                                'Probe #' + str(source.get_value()) + ' to ' + str(measurement.target) +
                                ' failed: ' + str(response))
         return ( None, response )


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
      is_oneoff = True
      packets   = 1
      size      = 16

      try:
         measurement = ripe.atlas.cousteau.Ping(
            af          = targetAddress.version,
            target      = str(targetAddress),
            description = description,
            is_oneoff   = is_oneoff,
            packets     = packets,
            paris       = 1,
            size        = size   # size without IP and ICMP headers
         )
         ( measurementID, info ) = self.startRIPEAtlasMeasurement(source, measurement)
      except Exception as e:
         measurementID = None
         info          = str(e)
         AtlasMNSLogger.warning('Creating Ping experiment failed: ' + info)

      # Cost calculation:
      # https://atlas.ripe.net/docs/credits/
      if measurementID != None:
         costs = packets * (int(size / 1500) + 1)
         if is_oneoff:
            costs = 2 * costs
      else:
         costs = 0
      return ( measurementID, costs, info )


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
      is_oneoff = True
      packets   = 1
      size      = 16

      try:
         measurement = ripe.atlas.cousteau.Traceroute(
            af          = targetAddress.version,
            target      = str(targetAddress),
            description = description,
            protocol    = 'ICMP',
            is_oneoff   = is_oneoff,
            packets     = packets,
            paris       = 1,
            size        = size   # size without IP and ICMP headers
         )
         ( measurementID, info ) = self.startRIPEAtlasMeasurement(source, measurement)
      except Exception as e:
         measurementID = None
         info          = str(e)
         AtlasMNSLogger.warning('Creating Traceroute experiment failed: ' + info)

      # Cost calculation:
      # https://atlas.ripe.net/docs/credits/
      if measurementID != None:
         costs = 10 * packets * (int(size / 1500) + 1)
         if is_oneoff:
            costs = 2 * costs
      else:
         costs = 0
      return ( measurementID, costs, info )


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
      self.scheduler_dbCursor     = None
      self.scheduler_dbConnection = None
      try:
         # ====== Connect to server =========================================
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

         # ====== Configure some settings ===================================
         self.scheduler_dbConnection.autocommit = False
         self.scheduler_dbCursor = self.scheduler_dbConnection.cursor()
         self.scheduler_dbCursor.execute("""
               SET SESSION idle_in_transaction_session_timeout = '1min';
               SET SESSION statement_timeout = '30s';
            """)
         self.scheduler_dbConnection.commit()

      except psycopg2.Error as e:
         AtlasMNSLogger.error('Unable to connect to the PostgreSQL scheduler database at ' +
               self.configuration['scheduler_dbserver'] + ': ' + str(e).strip())
         return False

      return True

   # ###### Query schedule from scheduler database ##########################
   def queryScheduleFromParams(self, parameters, total, limit, kind, identifiers=None):
      # ====== Query database ===============================================
      AtlasMNSLogger.trace('Querying schedule ...')
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
            if identifiers != None:
               self.scheduler_dbCursor.execute("""
                  SELECT * FROM ExperimentSchedule
                  WHERE
                     Identifier IN %(Identifiers)s
                  """, {
                     'Identifiers': identifiers
                  })
            else:
                if limit and kind:
                    query = self.scheduler_dbCursor.mogrify(
                        """SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                        FROM ExperimentSchedule
                        WHERE AgentHostIP IN %s
                           AND AgentTrafficClass IN %s
                           AND AgentFromIP IN %s
                           AND ProbeID IN %s
                           AND State = %s
                        ORDER BY Identifier DESC LIMIT %s
                        """, (parameters['agentHostIP'],parameters['agentTrafficClass'], parameters['agentFromIP'], parameters['probeID'], kind, limit, )
                    )
                elif limit and not kind:
                    query = self.scheduler_dbCursor.mogrify(
                        """SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                        FROM ExperimentSchedule
                        WHERE AgentHostIP IN %s
                           AND AgentTrafficClass IN %s
                           AND AgentFromIP IN %s
                           AND ProbeID IN %s
                        ORDER BY Identifier DESC LIMIT %s
                        """, (parameters['agentHostIP'],parameters['agentTrafficClass'], parameters['agentFromIP'], parameters['probeID'], limit, )
                    )
                elif kind and not limit:
                    query = self.scheduler_dbCursor.mogrify(
                        """SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                        FROM ExperimentSchedule
                        WHERE AgentHostIP IN %s
                           AND AgentTrafficClass IN %s
                           AND AgentFromIP IN %s
                           AND ProbeID IN %s
                           AND State = %s
                        ORDER BY Identifier DESC
                        """, (parameters['agentHostIP'],parameters['agentTrafficClass'], parameters['agentFromIP'], parameters['probeID'], kind, )
                    )
                else:
                    query = self.scheduler_dbCursor.mogrify(
                        """SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                        FROM ExperimentSchedule
                        WHERE AgentHostIP IN %s 
                           AND AgentTrafficClass IN %s
                           AND AgentFromIP IN %s
                           AND ProbeID IN %s
                        ORDER BY Identifier DESC LIMIT %s
                        """, (parameters['agentHostIP'],parameters['agentTrafficClass'], parameters['agentFromIP'], parameters['probeID'], total, ) 
                    )
            self.scheduler_dbCursor.execute(query)
            table = self.scheduler_dbCursor.fetchall()
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               AtlasMNSLogger.warning('Failed to query schedule: ' + str(e).strip())
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
      return schedule


   # ###### Query schedule from scheduler database ##########################
   def querySchedule(self, limit, kind, identifier = None):
      # ====== Query database ===============================================
      AtlasMNSLogger.trace('Querying schedule ...')
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
            if identifier != None:
               self.scheduler_dbCursor.execute("""
                  SELECT * FROM ExperimentSchedule
                  WHERE
                     Identifier = %(Identifier)s
                  """, {
                     'Identifier': int(identifier)
                  })
            else:
                if limit and kind:
                    self.scheduler_dbCursor.execute("""
                      SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                      FROM ExperimentSchedule
                      WHERE State = %(state)s
                      ORDER BY Identifier DESC
                      LIMIT %(limit)s;
                      """,{'limit': int(limit), 'state': str(kind) })

                elif limit and not kind:
                    self.scheduler_dbCursor.execute("""
                      SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                      FROM ExperimentSchedule
                      ORDER BY Identifier DESC
                      LIMIT %(limit)s;
                      """,{'limit': int(limit)})

                elif kind and not limit:
                    self.scheduler_dbCursor.execute("""
                      SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                      FROM ExperimentSchedule
                      WHERE State = %(state)s
                      ORDER BY LastChange ASC;
                      """,{'state': str(kind)})

                else:
                    self.scheduler_dbCursor.execute("""
                      SELECT Identifier,State,LastChange,AgentMeasurementTime,AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID,ProbeMeasurementID,ProbeCost,ProbeHostIP,ProbeFromIP,Info
                      FROM ExperimentSchedule
                      ORDER BY LastChange ASC;
                      """)
 

            table = self.scheduler_dbCursor.fetchall()
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               AtlasMNSLogger.warning('Failed to query schedule: ' + str(e).strip())
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
      # print(schedule)
      return schedule


   # ###### Add measurement run #############################################
   def addMeasurementRun(self, agentHostIP, agentTrafficClass, agentFromIP, probeID, insert):
     # Measurement is finished ? We can run new one
     scheduled = False
     find = False
     identifier = 0
     state = None
     use = False
     try:
         self.scheduler_dbCursor.execute("""
               SELECT Identifier,State FROM  ExperimentSchedule
               WHERE AgentHostIP = %(AgentHostIP)s
                 AND AgentTrafficClass = %(AgentTrafficClass)s
                 AND AgentFromIP = %(AgentFromIP)s
                 AND ProbeID = %(ProbeID)s
                 ORDER BY Identifier ASC
               """, {
                  'AgentHostIP':       str(agentHostIP),
                  'AgentTrafficClass': int(agentTrafficClass),
                  'AgentFromIP':       str(agentFromIP),
                  'ProbeID':           int(probeID)
               })
         table = self.scheduler_dbCursor.fetchall()
         if table:
             find = True
             for row in table:
                 identifier = row[0]
                 state = row[1]
                 if state == "scheduled":
                     scheduled = True
                     break
     except psycopg2.Error as e:
         self.connectToSchedulerDB()
         print('Unable to check measurement: ' + str(e).strip())
         return False

     if scheduled:
         if identifier != 0:
             print('==> [Duplicate]', agentHostIP, agentTrafficClass, agentFromIP, probeID, ' Measurement ' + str(identifier) + ' state is ' + state)  
         return False
     
     if find:
         if state != 'finished':
             print('==> [Done]', agentHostIP, agentTrafficClass, agentFromIP, probeID, ' Measurement ' + str(identifier) + ' state is ' + state)
             return False
         else:
             use = True

     if not find or use:
     #if not find:
         for stage in [ 1, 2 ]:
             try:
                 if self.scheduler_dbCursor == None:
                     raise psycopg2.Error('Disconnected from database')
                 if insert:
                     print('==> [Insertion]', agentHostIP, agentTrafficClass, agentFromIP, probeID)
                     self.scheduler_dbCursor.execute("""
                       INSERT INTO ExperimentSchedule (AgentHostIP,AgentTrafficClass,AgentFromIP,ProbeID)
                       VALUES (%(AgentHostIP)s,%(AgentTrafficClass)s,%(AgentFromIP)s,%(ProbeID)s)
                        """, {
                            'AgentHostIP':       str(agentHostIP),
                            'AgentTrafficClass': int(agentTrafficClass),
                            'AgentFromIP':       str(agentFromIP),
                            'ProbeID':           int(probeID)
                     })
                     self.scheduler_dbConnection.commit()
                 else:
                     print('==> [Dry Run]', agentHostIP, agentTrafficClass, agentFromIP, probeID)
                 break
             except psycopg2.Error as e:
                 self.connectToSchedulerDB()
                 if stage == 2:
                     print('Unable to add measurement run: ' + str(e).strip())
                     return False

     return True


   # ###### Remove measurement run ##########################################
   def removeMeasurementRun(self, agentHostIP, agentTrafficClass, agentFromIP, probeID):
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
            self.scheduler_dbCursor.execute("""
               DELETE FROM ExperimentSchedule
               WHERE
                  AgentHostIP = %(AgentHostIP)s AND
                  AgentTrafficClass = %(AgentTrafficClass)s AND
                  AgentFromIP = %(AgentFromIP)s AND
                  ProbeID = %(ProbeID)s
                  AND state = 'scheduled'
               """, {
                  'AgentHostIP':       str(agentHostIP),
                  'AgentTrafficClass': int(agentTrafficClass),
                  'AgentFromIP':       str(agentFromIP),
                  'ProbeID':           int(probeID)
               })
            self.scheduler_dbConnection.commit()
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               print('Unable to list measurement runs: ' + str(e).strip())
               return False

      return True


   # ###### Query agents from scheduler database ############################
   def queryAgents(self):
      # ====== Query database ===============================================
      AtlasMNSLogger.trace('Querying agents ...')
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
            self.scheduler_dbCursor.execute("""
               SELECT AgentHostIP,AgentHostName,LastSeen,Location FROM AgentLastSeen
               ORDER BY AgentHostName,AgentHostIP
               """)
            table = self.scheduler_dbCursor.fetchall()
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               AtlasMNSLogger.warning('Failed to query agents: ' + str(e).strip())
               return []

      # ====== Provide result as list of dictionaries =======================
      agents = []
      for row in table:
         agents.append({
            'AgentHostIP':     row[0],
            'AgentHostName':   row[1],
            'LastSeen':        row[2],
            'Location':        row[3]
         })
      # print(agents)
      return agents


   # ###### Purge agents #######################################################
   def purgeAgents(self, seconds = 24*3600):
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
            self.scheduler_dbCursor.execute("""
               DELETE FROM AgentLastSeen
               WHERE
                  LastSeen < (NOW() - INTERVAL %(Interval)s)
               """, {
                  'Interval': str(str(seconds) + ' SECONDS')
               })
            self.scheduler_dbConnection.commit()
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               print('Unable to purge agents: ' + str(e).strip())
               return


   # ###### Update schedule in scheduler database ###########################
   def updateScheduledEntry(self, scheduledEntry):
      AtlasMNSLogger.trace('Updating scheduled entry ...')
      for stage in [ 1, 2 ]:
         try:
            if self.scheduler_dbCursor == None:
               raise psycopg2.Error('Disconnected from database')
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
            break
         except psycopg2.Error as e:
            self.connectToSchedulerDB()
            if stage == 2:
               AtlasMNSLogger.warning('Failed to update schedule: ' + str(e).strip())
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


   # ###### Import results ##################################################
   def importResults(self, scheduledEntry, results):
      experiment = {
         'timestamp':            AtlasMNSTools.datatimeToTimeStamp(datetime.datetime.utcnow()),   # Ensure microseconds precision!
         'identifier':           scheduledEntry['Identifier'],
         'agentMeasurementTime': AtlasMNSTools.datatimeToTimeStamp(scheduledEntry['AgentMeasurementTime']),   # Ensure microseconds precision!
         'agentHostIP':          scheduledEntry['AgentHostIP'],
         'agentTrafficClass':    scheduledEntry['AgentTrafficClass'],
         'agentFromIP':          scheduledEntry['AgentFromIP'],
         'probeID':              scheduledEntry['ProbeID'],
         'probeMeasurementID':   scheduledEntry['ProbeMeasurementID'],
         'probeCost':            scheduledEntry['ProbeCost'],
         'probeHostIP':          scheduledEntry['ProbeHostIP'],
         'probeFromIP':          scheduledEntry['ProbeFromIP']
      }
      # print(experiment)
      try:
         self.results_db['ripeatlastraceroute'].insert(results)
         self.results_db['atlasmns'].insert(experiment)
         return True
      except Exception as e:
         AtlasMNSLogger.error('Unable to import results: ' + str(e))
         return False


   # ###### Dump RIPE Atlas result ##########################################
   def dumpRIPEAtlasResult(self, result):
      # print(result)
      try:
         print('Probe #' + str(result['prb_id']) + ': ' +
               result['src_addr'] + ' (' + result['from'] + ') -> ' + result['dst_addr'])
         for hop in result['result']:
            sys.stdout.write('   - ' + '{0:>2d}'.format(hop['hop']) + ': ')
            for run in hop['result']:
               try:
                  router = run['from']
                  rtt    = '{0:1.3f} ms'.format(run['rtt'])
               except:
                  router = '*'   # run['x']=='*'
                  rtt    = 'N/A   '
               sys.stdout.write('{0:>20s} {1:>11s}'.format(router, rtt) + '   ')
            sys.stdout.write('\n')
      except Exception as e:
         print('Bad result: ' + str(e))


   # ###### Dump HiPerConTracer result ######################################
   def dumpHiPerConTracerResult(self, result):
      # print(result)
      try:
         print(str(AtlasMNSTools.binaryToIPAddress(result['source'])) +
               '/0x{0:02x}'.format(result['tc']) +
               ' -> ' + str(AtlasMNSTools.binaryToIPAddress(result['destination'])) +
               ', round ' + str(1 + result['round']))
         n = 1
         for hop in result['hops']:
            rtt    = '{0:1.3f} ms'.format(hop['rtt'] / 1000.0)   # Note: stored RTT is in microseconds!
            print('   - ' +
                  '{0:>2d}: {1:>20s} {2:>11s} {3:>3d}'.format(
                     n, str(AtlasMNSTools.binaryToIPAddress(hop['hop'])),
                     rtt, hop['status']))
            n = n + 1
      except Exception as e:
         print('Bad result: ' + str(e))


   # ###### Query results ###################################################
   def queryResults(self, identifier):
      try:
         # ====== Find experiment ==============================================
         experiments = self.results_db['atlasmns'].find( { 'identifier': { '$eq': identifier }} )
         myExperiment = None
         for experiment in experiments:
            if myExperiment == None:
               myExperiment = experiment
            else:
               print('WARNING: Multiple experiments found! Something is wrong!')
               myExperiment = experiment
         if myExperiment == None:
            return [ False, None, None, None ]

         myProbeMeasurementID   = myExperiment['probeMeasurementID']
         myAgentMeasurementTime = myExperiment['agentMeasurementTime']

         # ====== Find RIPE Atlas results =======================================
         ripeAtlasResults = self.results_db['ripeatlastraceroute'].find( { 'msm_id': { '$eq': myProbeMeasurementID }} )

         # ====== Find HiPerConTracer results ===================================
         hiPerConTracerResults = self.results_db['traceroute'].find( { 'timestamp': { '$eq': myAgentMeasurementTime }} )

         return [ True, myExperiment, ripeAtlasResults, hiPerConTracerResults ]

      except Exception as e:
         AtlasMNSLogger.error('Unable to query results: ' + str(e))
         return [ False, None, None, None ]
