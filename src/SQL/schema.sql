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


-- ###### Experiment Schedule ###############################################
DROP TABLE IF EXISTS ExperimentSchedule;
CREATE TABLE ExperimentSchedule (
   TimeStamp         TIMESTAMP        NOT NULL DEFAULT NOW(),

   AgentHostIP       INET             NOT NULL,
   AgentTrafficClass SMALLINT NOT NULL DEFAULT 0,
   AgentRouterIP     INET             NOT NULL,

   MeasurementID     INTEGER          DEFAULT NULL,
   ProbeID           INTEGER          DEFAULT NULL,
   ProbeHostIP       INET             DEFAULT NULL,
   ProbeRouterIP     INET             DEFAULT NULL,

   State             SMALLINT         NOT NULL DEFAULT 0,

   PRIMARY KEY (TimeStamp, AgentHostIP, AgentTrafficClass)
);
