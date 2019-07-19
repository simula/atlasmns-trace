#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <functional>
#include <iostream>

// #include <boost/bind.hpp>
// #include <boost/function.hpp>


void t1(double a, int b, const char* c)
{
   printf("%1.6f: %d <%s>\n", a, b, c);
}


int main(int argc, char** argv)
{
   std::function<void(double, int)> f1 = std::bind(&t1, std::placeholders::_1, std::placeholders::_2, "TEST");

   f1(3.14156,1234);

   return 0;
}
