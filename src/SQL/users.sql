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


REVOKE ALL ON DATABASE atlasmnsdb FROM agent;
REVOKE ALL ON Ping FROM agent;
REVOKE ALL ON Traceroute FROM agent;
DROP ROLE agent;
CREATE ROLE agent WITH LOGIN ENCRYPTED PASSWORD '!agent!';
GRANT CONNECT ON DATABASE atlasmnsdb TO agent;
GRANT SELECT ON TABLE ExperimentSchedule TO agent;
GRANT UPDATE ON TABLE ExperimentSchedule TO agent;

REVOKE ALL ON DATABASE atlasmnsdb FROM scheduler;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM scheduler;
DROP ROLE scheduler;
CREATE ROLE scheduler WITH LOGIN ENCRYPTED PASSWORD '!scheduler!';
GRANT CONNECT ON DATABASE atlasmnsdb TO scheduler;
GRANT INSERT ON TABLE ExperimentSchedule TO scheduler;
GRANT SELECT ON TABLE ExperimentSchedule TO scheduler;

REVOKE ALL ON DATABASE atlasmnsdb FROM maintainer;
DROP ROLE maintainer;
CREATE ROLE maintainer WITH LOGIN ENCRYPTED PASSWORD '!maintainer!';
GRANT CONNECT ON DATABASE atlasmnsdb TO maintainer;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO maintainer;
