-- STEP 4: Create Users
-- sudo -u postgres psql atlasmnsdb <users.sql
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


-- ##########################################################
-- !!! IMPORTANT: Change the passwords before deployment! !!!
-- ##########################################################


REVOKE ALL ON DATABASE atlasmnsdb FROM atlasmnsagent;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM atlasmnsagent;
DROP ROLE atlasmnsagent;
CREATE ROLE atlasmnsagent WITH LOGIN ENCRYPTED PASSWORD '!agent!';
GRANT CONNECT ON DATABASE atlasmnsdb TO atlasmnsagent;
GRANT SELECT, UPDATE ON TABLE ExperimentSchedule TO atlasmnsagent;
GRANT USAGE, SELECT ON SEQUENCE ExperimentSchedule_Identifier_Seq TO atlasmnsagent;
GRANT SELECT, UPDATE ON TABLE AgentLastSeen TO atlasmnsagent;

REVOKE ALL ON DATABASE atlasmnsdb FROM atlasmnsscheduler;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM atlasmnsscheduler;
DROP ROLE atlasmnsscheduler;
CREATE ROLE atlasmnsscheduler WITH LOGIN ENCRYPTED PASSWORD '!scheduler!';
GRANT CONNECT ON DATABASE atlasmnsdb TO atlasmnsscheduler;
GRANT INSERT, UPDATE, SELECT, DELETE ON ExperimentSchedule TO atlasmnsscheduler;
GRANT USAGE, SELECT ON SEQUENCE ExperimentSchedule_Identifier_Seq TO atlasmnsscheduler;

REVOKE ALL ON DATABASE atlasmnsdb FROM atlasmnsmaintainer;
DROP ROLE atlasmnsmaintainer;
CREATE ROLE atlasmnsmaintainer WITH LOGIN ENCRYPTED PASSWORD '!maintainer!';
GRANT CONNECT ON DATABASE atlasmnsdb TO atlasmnsmaintainer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO atlasmnsmaintainer;
