-- STEP 2: Create Schema
-- sudo -u postgres psql atlasmnsdb <schema.sql
--
-- =================================================================
--          #     #                 #     #
--          ##    #   ####   #####  ##    #  ######   #####
--          # #   #  #    #  #    # # #   #  #          #
--          #  #  #  #    #  #    # #  #  #  #####      #
--          #   # #  #    #  #####  #   # #  #          #
--          #    ##  #    #  #   #  #    ##  #          #
--          #     #   ####   #    # #     #  ######     #
--
--       ---   The NorNet Testbed for Multi-Homed Systems  ---
--                       https://www.nntb.no
-- =================================================================
--
-- High-Performance Connectivity Tracer (HiPerConTracer)
-- Copyright (C) 2015-2019 by Thomas Dreibholz
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.
--
-- Contact: dreibh@simula.no


-- ###### AtlasMNSStatus ####################################################
CREATE TYPE AtlasMNSStatus AS ENUM (
   'scheduled',
   --  The experiment is scheduled, but no RIPE Atlas measurement created.
   -- Next state: atlas_scheduled.

   'atlas_scheduled',
   -- A RIPE Atlas measurement is created. MeasurementID is set to the
   -- ID of this measurement.
   -- Next state: agent_scheduled OR failed.

   'agent_scheduled',
   -- The RIPE Atlas measurement is finished, ProbeHostIP and ProbeRouterIP
   -- are set. The corresponding Agent instance can schedule the reverse
   -- measurement.
   -- Next state: agent_completed OR failed.
   
   'agent_completed',
   -- The Agent has completed the measurement. The scheduler has not yet
   -- written the result of the experiment.
   -- Next state: finished.

   'failed',
   -- The experiment has failed. Info may be set to some information about
   -- the failure. Final state.

   'finished'
   -- The experiment has succeded. Final state.
);


-- ###### Experiment Schedule ###############################################
DROP TABLE IF EXISTS ExperimentSchedule;
CREATE TABLE ExperimentSchedule (
   Identifier        SERIAL UNIQUE,

   State             AtlasMNSStatus   NOT NULL DEFAULT 'scheduled',
   LastChange        TIMESTAMP        NOT NULL DEFAULT NOW(),

   AgentHostIP       INET             NOT NULL,
   AgentTrafficClass SMALLINT         NOT NULL DEFAULT 0,
   AgentRouterIP     INET             NOT NULL,

   MeasurementID     INTEGER          DEFAULT NULL,
   ProbeID           INTEGER          DEFAULT NULL,
   ProbeHostIP       INET             DEFAULT NULL,
   ProbeRouterIP     INET             DEFAULT NULL,
   
   Info              CHAR(128)        DEFAULT NULL,

   PRIMARY KEY (Identifier)
   -- UNIQUE (AgentHostIP,AgentTrafficClass,AgentRouterIP,ProbeID)
);

DROP INDEX IF EXISTS ExperimentSchedule_LastChange_Index;
CREATE INDEX ExperimentSchedule_LastChange_Index ON ExperimentSchedule ( LastChange );
