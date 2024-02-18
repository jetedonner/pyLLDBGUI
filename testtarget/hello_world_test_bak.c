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
//#include <signal.h>

//int shouldNotExit = 1;

int main() {
  
//signal(SIGINT, signal_handler);
  
  // Variable for iteration counter
  int idx = 0;
  
  // INT test variable for the disasseblers "Variable" view
  int testVar = 123;
  // Variable to hold the user input
  // char input[256];

  // Another test variable (char array) for the disasseblers "Variable" view
  char hardcoded_string[] = "S3CR3T";

  // This msg will prompt the user to enter his / her secret
  printf("Hello test: %d / %s", testVar, hardcoded_string);
  
  while(1)
    {
      printf("...");
      fflush(stdout);
      sleep(1);
      idx++;
    }

  // Will wait for user input and store the input in the variable "input"
  // scanf("%s", input);

  // Compare the value of the variable "input" with the variable "hardcoded_string"
  // int result = strcmp(input, hardcoded_string);

  // If the compare of the two values succeeds (or not) show a appropriate message
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
//void signal_handler(int signum) {
//shouldNotExit = 0;
//printf("shouldNotExit = 0;");
//}