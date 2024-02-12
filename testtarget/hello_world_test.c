// NO DEBUG-INFO:
// clang -target x86_64-apple-macos -arch x86_64 -o hello_world_test hello_world_test.c
//
// WITH DEBUG-INFO:
// clang -g -target x86_64-apple-macos -arch x86_64 -o hello_world_test hello_world_test.c
//
// FOR scanf():
// -lcurses
//
// Make executable:
// chmod u+x hello_world
//
// Codesign for MacOS
// codesign --verbose=4 --timestamp --strict --options runtime -s "<YOUR SIGNING CERTIFICATE NAME>" hello_world --force

// Standard include
#include <stdio.h>
// // For scanf()
// #include <curses.h> 
// // For strcmp()
// #include <string.h>
// For sleep()
#include <unistd.h>
#include <time.h>

int main() {
  
  int testVar = 123;
  // // Variable to hold the user input
  // char input[256];

  // // The secret to check against the user input
  char hardcoded_string[] = "S3CR3T";

  // This msg will prompt the user to enter his / her secret
  printf("Hello test: %d / %s", testVar, hardcoded_string);

//while(1)
//  {
////    testVar += 321;
//    printf(".");
//
//    sleep(1);
//    // sleep(1);
//    // struct timespec ts;
//    // ts.tv_sec = 0;
//    // ts.tv_nsec = 200000000; // 200ms
//    // nanosleep(&ts, NULL);
//  }

  // // Will wait for user input and store the input in the variable "input"
  // scanf("%s", input);

  // // Compare the value of the variable "input" with the variable "hardcoded_string"
  // int result = strcmp(input, hardcoded_string);

  // // If the compare of the two values succeeds (or not) show a appropriate message
  // if (result == 0) {
  //   printf("#=========================================================#\n");
  //   printf("|                       SUCCESS !!!!                      |\n");
  //   printf("|                                                         |\n");
  //   printf("|      Welcome to the hidden spot of this app. Enjoy!     |\n");
  //   printf("|                                                         |\n");
  //   printf("#=========================================================#\n");
  // } /*else if (result < 0) {
  //   printf("The input string is less than the hardcoded string.");
  // } */ else {
  //   printf("#=========================================================#\n");
  //   printf("|                        ERROR !!!!                       |\n");
  //   printf("|                                                         |\n");
  //   printf("|       The entered secret does not match, try again      |\n");
  //   printf("|                                                         |\n");
  //   printf("#=========================================================#\n");
  // }
  return 0;
}