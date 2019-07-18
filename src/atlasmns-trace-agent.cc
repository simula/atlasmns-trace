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

#include <fstream>
#include <iostream>
#include <vector>

#include <boost/format.hpp>
#include <boost/asio/ip/address.hpp>
#include <boost/program_options.hpp>

#include <pqxx/pqxx>

#include <hipercontracer/logger.h>
#include <hipercontracer/resultswriter.h>
#include <hipercontracer/service.h>
#include <hipercontracer/tools.h>
#include <hipercontracer/traceroute.h>


static std::set<ResultsWriter*>                     ResultsWriterSet;
static std::map<boost::asio::ip::address, Service*> ServiceSet;
static boost::asio::io_service                      IOService;
static boost::asio::signal_set                      Signals(IOService, SIGINT, SIGTERM);
static boost::posix_time::milliseconds              CleanupTimerInterval(250);
static boost::asio::deadline_timer                  CleanupTimer(IOService, CleanupTimerInterval);


// ###### Signal handler ####################################################
static void signalHandler(const boost::system::error_code& error, int signal_number)
{
   if(error != boost::asio::error::operation_aborted) {
      puts("\n*** Shutting down! ***\n");   // Avoids a false positive from Helgrind.
      for(std::map<boost::asio::ip::address, Service*>::iterator serviceIterator = ServiceSet.begin();
          serviceIterator != ServiceSet.end(); serviceIterator++) {
         Service* service = serviceIterator->second;
         service->requestStop();
      }
   }
}


// ###### Check whether services can be cleaned up ##########################
static void tryCleanup(const boost::system::error_code& errorCode)
{
   bool finished = true;
   for(std::map<boost::asio::ip::address, Service*>::iterator serviceIterator = ServiceSet.begin();
       serviceIterator != ServiceSet.end(); serviceIterator++) {
      Service* service = serviceIterator->second;
      if(!service->joinable()) {
         finished = false;
         break;
      }
   }

   if(!finished) {
      CleanupTimer.expires_at(CleanupTimer.expires_at() + CleanupTimerInterval);
      CleanupTimer.async_wait(tryCleanup);
   }
   else {
      Signals.cancel();
   }
}



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
      ( "scheduler_dbserver",
           boost::program_options::value<std::string>(&schedulerDBServer)->default_value(std::string("localhost")),
           "Scheduler database server name" )
      ( "scheduler_dbport",
           boost::program_options::value<uint16_t>(&schedulerDBPort)->default_value(5432),
           "Scheduler database server port" )
      ( "scheduler_dbuser",
           boost::program_options::value<std::string>(&schedulerDBUser)->default_value(std::string("scheduler")),
           "Scheduler database user name" )
      ( "scheduler_dbpassword",
           boost::program_options::value<std::string>(&schedulerDBPassword),
        "Scheduler database password" )
      ( "scheduler_database",
           boost::program_options::value<std::string>(&schedulerDatabase)->default_value(std::string("atlasmnsdb")),
           "Scheduler database name" )
      ( "scheduler_cafile",
           boost::program_options::value<std::string>(&schedulerCAFile),
           "Scheduler server CA file" )
      ;

   unsigned int       logLevel;
   std::string        user;
   std::string        configurationFileName;

   unsigned long long tracerouteInterval;
   unsigned int       tracerouteExpiration;
   unsigned int       tracerouteRounds;
   unsigned int       tracerouteInitialMaxTTL;
   unsigned int       tracerouteFinalMaxTTL;
   unsigned int       tracerouteIncrementMaxTTL;

   unsigned int       resultsTransactionLength;
   std::string        resultsDirectory;

   boost::program_options::options_description commandLineOptions;
   commandLineOptions.add_options()
      ( "help,h",
           "Print help message" )

      ( "loglevel",
           boost::program_options::value<unsigned int>(&logLevel)->default_value(boost::log::trivial::severity_level::trace),
           "Set logging level" )
      ( "user",
           boost::program_options::value<std::string>(&user),
           "User" )
      ( "config-file",
           boost::program_options::value<std::string>(&configurationFileName),
           "Configuration file" )

      ( "source,S",
           boost::program_options::value<std::vector<std::string>>(),
           "Source address" )

      ( "tracerouteinterval",
           boost::program_options::value<unsigned long long>(&tracerouteInterval)->default_value(10000),
           "Traceroute interval in ms" )
      ( "tracerouteduration",
           boost::program_options::value<unsigned int>(&tracerouteExpiration)->default_value(3000),
           "Traceroute duration in ms" )
      ( "tracerouterounds",
           boost::program_options::value<unsigned int>(&tracerouteRounds)->default_value(1),
           "Traceroute rounds" )
      ( "tracerouteinitialmaxttl",
           boost::program_options::value<unsigned int>(&tracerouteInitialMaxTTL)->default_value(6),
           "Traceroute initial maximum TTL value" )
      ( "traceroutefinalmaxttl",
           boost::program_options::value<unsigned int>(&tracerouteFinalMaxTTL)->default_value(36),
           "Traceroute final maximum TTL value" )
      ( "tracerouteincrementmaxttl",
           boost::program_options::value<unsigned int>(&tracerouteIncrementMaxTTL)->default_value(6),
           "Traceroute increment maximum TTL value" )

      ( "resultsdirectory,R",
           boost::program_options::value<std::string>(&resultsDirectory)->default_value(std::string()),
           "Results directory" )
      ( "resultstransactionlength",
           boost::program_options::value<unsigned int>(&resultsTransactionLength)->default_value(60),
           "Results directory in s" )
    ;
   commandLineOptions.add(configurationFileOptions);
   boost::program_options::positional_options_description positionalOptions;
   positionalOptions.add("config-file", -1);


   // ====== Handle command-line arguments ==================================
   boost::program_options::variables_map vm;
   try {
      boost::program_options::store(boost::program_options::command_line_parser(argc, argv).
                                       style(
                                          boost::program_options::command_line_style::style_t::default_style|
                                          boost::program_options::command_line_style::style_t::allow_long_disguise
                                       ).
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
                 << commandLineOptions;
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


   // ====== Handle configuration-file arguments ============================
   std::set<boost::asio::ip::address> sourceAddressArray;
   if(vm.count("source")) {
      const std::vector<std::string>& sourceAddressVector = vm["source"].as<std::vector<std::string>>();
      for(std::vector<std::string>::const_iterator iterator = sourceAddressVector.begin();
          iterator != sourceAddressVector.end(); iterator++) {
         try {
            const boost::asio::ip::address sourceAddress = boost::asio::ip::address::from_string(*iterator);
            sourceAddressArray.insert(sourceAddress);
         }
         catch(std::exception& e) {
            std::cerr << "ERROR: Bad source " << *iterator << ": " << e.what() << std::endl;
            return 1;
         }
      }
   }
   else {
      std::cerr << "ERROR: No source address(es) given!" << std::endl;
      return 1;
   }


   // ====== Initialize =====================================================
   initialiseLogger(logLevel);
   const passwd* pw = getUser(user.c_str());

   std::srand(std::time(0));
   tracerouteExpiration      = std::min(std::max(1000U, tracerouteExpiration),   60000U);
   tracerouteInitialMaxTTL   = std::min(std::max(1U, tracerouteInitialMaxTTL),   255U);
   tracerouteFinalMaxTTL     = std::min(std::max(1U, tracerouteFinalMaxTTL),     255U);
   tracerouteIncrementMaxTTL = std::min(std::max(1U, tracerouteIncrementMaxTTL), 255U);
   if(!resultsDirectory.empty()) {
      HPCT_LOG(info) << "Results Output:" << std::endl
                     << "* Results Directory  = " << resultsDirectory         << std::endl
                     << "* Transaction Length = " << resultsTransactionLength << " s";
   }
   HPCT_LOG(info) << "Traceroute Service:" << std:: endl
                  << "* Expiration         = " << tracerouteExpiration      << " ms" << std::endl
                  << "* Rounds             = " << tracerouteRounds          << std::endl
                  << "* Initial MaxTTL     = " << tracerouteInitialMaxTTL   << std::endl
                  << "* Final MaxTTL       = " << tracerouteFinalMaxTTL     << std::endl
                  << "* Increment MaxTTL   = " << tracerouteIncrementMaxTTL;


   // ====== Start service threads ==========================================
   for(std::set<boost::asio::ip::address>::const_iterator sourceAddressIterator = sourceAddressArray.begin();
       sourceAddressIterator != sourceAddressArray.end(); sourceAddressIterator++) {
      const boost::asio::ip::address& sourceAddress = *sourceAddressIterator;
      HPCT_LOG(info) << "Source: " << sourceAddress;

      try {
         Service* service = new Traceroute(ResultsWriter::makeResultsWriter(
                                              ResultsWriterSet, sourceAddress, "Traceroute",
                                              resultsDirectory.c_str(), resultsTransactionLength,
                                              (pw != NULL) ? pw->pw_uid : 0, (pw != NULL) ? pw->pw_gid : 0),
                                           0, true,
                                           sourceAddress, std::set<AddressWithTrafficClass>(),
                                           tracerouteInterval, tracerouteExpiration,
                                           tracerouteRounds,
                                           tracerouteInitialMaxTTL, tracerouteFinalMaxTTL,
                                           tracerouteIncrementMaxTTL);
         if(service->start() == false) {
            ::exit(1);
         }
         ServiceSet.insert(std::pair<boost::asio::ip::address, Service*>(sourceAddress, service));
      }
      catch (std::exception& e) {
         HPCT_LOG(fatal) << "ERROR: Cannot create Traceroute service - " << e.what();
         ::exit(1);
      }
   }


   // ====== Reduce privileges ==============================================
   reducePrivileges(pw);

   // ====== Wait for termination signal ====================================
   Signals.async_wait(signalHandler);
   CleanupTimer.async_wait(tryCleanup);


   // ====== Prepare scheduler database connection ==========================
   try {
      pqxx::lazyconnection schedulerDBConnection(
         "host="     + schedulerDBServer                                 + " "
         "port="     + boost::str(boost::format("%d") % schedulerDBPort) + " "
         "user="     + schedulerDBUser     + " "
         "password=" + schedulerDBPassword + " "
         "dbname="   + schedulerDatabase);


      // ====== Main loop ===================================================
      do {
         try {
            // ====== Query scheduled measurements ==========================
            pqxx::work schedulerDBTransaction(schedulerDBConnection);
            std::string allSourcesString = "( ";
            for(std::set<boost::asio::ip::address>::const_iterator sourceArrayIterator = sourceAddressArray.begin();
               sourceArrayIterator != sourceAddressArray.end(); sourceArrayIterator++) {
               const boost::asio::ip::address& sourceAddress = *sourceArrayIterator;
               allSourcesString = allSourcesString +
                  ((sourceArrayIterator == sourceAddressArray.begin()) ? "" : ", ") +
                  schedulerDBTransaction.quote(sourceAddress.to_string());
            }

            allSourcesString = allSourcesString + ')';

            // ====== Perform scheduled measurements ========================
            pqxx::result result = schedulerDBTransaction.exec(
               "SELECT MeasurementID, AgentHostIP, AgentTrafficClass, ProbeID, ProbeRouterIP, ProbeHostIP "
               "FROM ExperimentSchedule "
               "WHERE "
                  "State = 'agent_scheduled' AND "
                  "AgentHostIP IN " + allSourcesString + " "
               "ORDER BY LastChange ASC");

            for (auto row : result) {
               const boost::asio::ip::address sourceAddress      = boost::asio::ip::address::from_string(row["AgentHostIP"].c_str());
               const uint8_t                  trafficClass       = atoi(row["AgentTrafficClass"].c_str());
               const boost::asio::ip::address destinationAddress = boost::asio::ip::address::from_string(row["ProbeRouterIP"].c_str());
               const AddressWithTrafficClass  destination(destinationAddress, trafficClass);

               Service* service = ServiceSet[sourceAddress];
               if(service->addDestination(destination)) {
                  HPCT_LOG(debug) << "Queued " << destination << " from " << sourceAddress;
                  schedulerDBTransaction.exec(
                     "UPDATE ExperimentSchedule "
                     "SET "
                        "State = 'agent_completed'"
                     "WHERE "
                        "MeasurementID = " + schedulerDBTransaction.quote(row["MeasurementID"].c_str()));
               }
            }

            schedulerDBTransaction.commit();
         }
         catch (const std::exception &e) {
            HPCT_LOG(warning) << "Unable to communicate with scheduler database: " << e.what();
            return 1;
         }

         puts("r1");
        IOService.run_one();
         puts("r2");

      } while(!IOService.stopped());
   }
   catch (const std::exception &e) {
      HPCT_LOG(warning) << "Unable to connect to scheduler database: " << e.what();
      return 1;
   }


   IOService.run();


   // ====== Shut down service threads ======================================
   for(std::map<boost::asio::ip::address, Service*>::iterator serviceIterator = ServiceSet.begin(); serviceIterator != ServiceSet.end(); serviceIterator++) {
      Service* service = serviceIterator->second;
      service->join();
      delete service;
   }
   for(std::set<ResultsWriter*>::iterator resultsWriterIterator = ResultsWriterSet.begin(); resultsWriterIterator != ResultsWriterSet.end(); resultsWriterIterator++) {
      delete *resultsWriterIterator;
   }

   return 0;
}
