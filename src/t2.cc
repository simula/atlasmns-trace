#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <iomanip>
#include <chrono>
#include <functional>
#include <iostream>

// #include <boost/bind.hpp>
// #include <boost/function.hpp>


void t1(double a, int b, const char* c)
{
   printf("%1.6f: %d <%s>\n", a, b, c);
}


// ###### Convert time point to string (in UTC time) ########################
template<class clock> std::string timePointToStringUTC(const std::chrono::time_point<clock> timePoint)
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



int main(int argc, char** argv)
{
   std::function<void(double, int)> f1 = std::bind(&t1, std::placeholders::_1, std::placeholders::_2, "TEST");
   std::function<void(double, int)> f2 = nullptr;

   f1(3.14156, 1234);
   // f2(1.23456, 8888);


   const std::chrono::system_clock::time_point timePoint = std::chrono::system_clock::now();
   const std::chrono::microseconds             us = std::chrono::duration_cast<std::chrono::microseconds>(timePoint.time_since_epoch());
   const time_t                                tt = std::chrono::system_clock::to_time_t(timePoint);
   tm                                          localTime;
   std::stringstream                           ss;

   localtime_r(&tt, &localTime);
   ss << std::put_time(&localTime, "%Y%m%dT%H%M%S.") << (us.count() % 1000000)
      << " " << std::put_time(&localTime, "%Z");
   std::cout << ss.str() << std::endl;

   std::cout << timePointToStringUTC(std::chrono::system_clock::now()) << std::endl;

   std::srand(std::time(0));

   double       s = 0;
   unsigned int n = 0;
   for(unsigned int i = 0; i < 1000000; i++) {
      std::chrono::seconds lastSeenUpdateInterval = randomiseInterval(std::chrono::seconds(3600), 0.50);
      s += lastSeenUpdateInterval.count();
      n++;
//       std::cout << " interval=" << lastSeenUpdateInterval.count() << std::endl;
   }
   std::cout << " avgInterval=" << (s / n) << std::endl;

   return 0;
}
