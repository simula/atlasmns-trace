// =================================================================
//          #     #                 #     #
//          ##    #   ####   #####  ##    #  ######   #####
//          # #   #  #    #  #    # # #   #  #          #
//          #  #  #  #    #  #    # #  #  #  #####      #
//          #   # #  #    #  #####  #   # #  #          #
//          #    ##  #    #  #   #  #    ##  #          #
//          #     #   ####   #    # #     #  ######     #
//
//       ---   The NorNet Testbed for Multi-Homed Systems  ---
//                       https://www.nntb.no
// =================================================================
//
// High-Performance Connectivity Tracer (HiPerConTracer)
// Copyright (C) 2015-2019 by Thomas Dreibholz
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
// Contact: dreibh@simula.no

#include <iostream>
#include <vector>
#include <fstream>

#include <boost/format.hpp>
#include <boost/program_options.hpp>
#include <boost/asio/ip/address.hpp>

#include <pqxx/pqxx>

#include <hipercontracer/logger.h>
#include <hipercontracer/service.h>
#include <hipercontracer/traceroute.h>
#include <hipercontracer/ping.h>
#include <hipercontracer/resultswriter.h>


// ###### Main program ######################################################
int main(int argc, char** argv)
{
   // ====== Define options =================================================
   boost::program_options::options_description configurationFileOptions;
   std::string schedulerDBServer;
   uint16_t    schedulerDBPort;
   std::string schedulerDBUser;
   std::string schedulerDBPassword;
   std::string schedulerDatabase;
   std::string schedulerCAFile;
   configurationFileOptions.add_options()
      ( "scheduler_dbserver",   boost::program_options::value<std::string>(&schedulerDBServer)->default_value(std::string("localhost")),  "Scheduler database server name" )
      ( "scheduler_dbport",     boost::program_options::value<uint16_t>(&schedulerDBPort)->default_value(5432),                           "Scheduler database server port" )
      ( "scheduler_dbuser",     boost::program_options::value<std::string>(&schedulerDBUser)->default_value(std::string("scheduler")),    "Scheduler database user name" )
      ( "scheduler_dbpassword", boost::program_options::value<std::string>(&schedulerDBPassword),                                         "Scheduler database password" )
      ( "scheduler_database",   boost::program_options::value<std::string>(&schedulerDatabase)->default_value(std::string("atlasmnsdb")), "Scheduler database name" )
      ( "scheduler_cafile",     boost::program_options::value<std::string>(&schedulerCAFile),                                             "Scheduler server CA file" )
      ;

   std::string  configurationFileName;
   unsigned int logLevel;
   boost::program_options::options_description commandLineOptions;
   commandLineOptions.add_options()
      ( "help,h",
           "Print help message" )
      ( "loglevel",
           boost::program_options::value<unsigned int>(&logLevel)->default_value(boost::log::trivial::severity_level::info),
           "Set logging level" )
      ( "config-file,c",
           boost::program_options::value<std::string>(&configurationFileName),
           "Configuration file" )
    ;
   commandLineOptions.add(configurationFileOptions);
   boost::program_options::positional_options_description positionalOptions;
   positionalOptions.add("config-file", -1);

   // ====== Handle command-line arguments ==================================
   boost::program_options::variables_map vm;
   try {
      boost::program_options::store(boost::program_options::command_line_parser(argc, argv).
                                       options(commandLineOptions).
                                       positional(positionalOptions).
                                       run(), vm);
      boost::program_options::notify(vm);
   }
   catch(std::exception& e) {
      std::cerr << "ERROR: Bad parameter: " << e.what() << std::endl;
      return 1;
   }

   if(vm.count("help")) {
       std::cerr << "Usage: " << argv[0] << " parameters" << std::endl
                 << commandLineOptions << configurationFileOptions;
       return 1;
   }

   // ====== Handle configuration-file arguments ============================
   if(vm.count("config-file")) {
      std::ifstream configurationFileStream(configurationFileName.c_str());
      if(!configurationFileStream) {
          std::cerr << "ERROR: Unable to open configuration file " << configurationFileName << std::endl;
          return 1;
      }
      try {
         boost::program_options::store(boost::program_options::parse_config_file(
                                          configurationFileStream, configurationFileOptions,
                                          true /* allow_unregistered */), vm);
         boost::program_options::notify(vm);
      }
      catch(std::exception& e) {
         std::cerr << "ERROR: Bad parameter in configuration file "
                   << configurationFileName << ": " << e.what() << std::endl;
         return 1;
      }
   }

   // ====== Initialize =====================================================
   initialiseLogger(logLevel);
   try {
      pqxx::connection schedulerDBConnection(
         "host="     + schedulerDBServer                                 + " "
         "port="     + boost::str(boost::format("%d") % schedulerDBPort) + " "
         "user="     + schedulerDBUser     + " "
         "password=" + schedulerDBPassword + " "
         "dbname="   + schedulerDatabase);
      pqxx::work schedulerDBTransaction(schedulerDBConnection);


      boost::asio::ip::address sourceAddress = boost::asio::ip::address_v4::from_string("10.1.1.1");

      try {
         pqxx::result result = schedulerDBTransaction.exec(
            "SELECT * "
            "FROM ExperimentSchedule "
            "WHERE "
               "State = 'agent_scheduled' AND "
               "AgentHostIP = " + schedulerDBTransaction.quote(sourceAddress.to_string()) + " "
            "ORDER BY LastChange ASC");
         for (auto row : result) {
            std::cout << "- "  << row["AgentHostIP"].c_str() << " -> " << row["ProbeHostIP"].c_str() << std::endl;
         }
      }
      catch (const std::exception &e) {
         HPCT_LOG(warning) << "Unable to query scheduler database: " << e.what();
         return 1;
      }

   }
   catch (const std::exception &e) {
      HPCT_LOG(warning) << "Unable to connect to scheduler database: " << e.what();
      return 1;
   }

   return 0;
}
