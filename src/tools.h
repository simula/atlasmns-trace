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

#include <chrono>


// ###### Convert time point to string (in UTC time) ########################
template<class clock>
   std::string timePointToStringUTC(const std::chrono::time_point<clock> timePoint)
{
   const std::chrono::microseconds us = std::chrono::duration_cast<std::chrono::microseconds>(timePoint.time_since_epoch());
   const time_t                    tt = std::chrono::system_clock::to_time_t(timePoint);
   tm                              localTime;
   std::stringstream               ss;

   gmtime_r(&tt, &localTime);
   ss << std::put_time(&localTime, "%Y%m%dT%H%M%S.") << (us.count() % 1000000);
   return ss.str();
}


// ###### Randomise std::chrono::duration value #############################
template<class rep, class period = std::ratio<1>>
   std::chrono::duration<rep, period> randomiseInterval(const std::chrono::duration<rep, period>& avg, const double variance)
{
   // Get random value from [avg - variance*avg, avg + variance*avg]:
   const double r = rand() / (double)RAND_MAX;
   const rep    v = avg.count() +
      (2 * r * (variance * avg.count()) - (variance * avg.count()));
   return std::chrono::duration<rep, period>(v);
}
