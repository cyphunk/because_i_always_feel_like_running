// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
/*

this was a test to see if we could modify the brightness of the display
when a different process (e.g. image player or video player) was in control.
does not work that way.

*/

#include "led-matrix.h"
#include "graphics.h"

#include <getopt.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>
#include <math.h>
#include <unistd.h>
#include <fcntl.h>

using namespace rgb_matrix;

static int usage(const char *progname) {
  fprintf(stderr, "usage: %s [options]\n", progname);
  fprintf(stderr, "Options:\n");
  rgb_matrix::PrintMatrixFlags(stderr);
  fprintf(stderr,
          "\t-b <brightness>   : Sets brightness percent. Default: 100.\n"
          );

  return 1;
}


int main(int argc, char *argv[]) {
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return usage(argv[0]);
  }

  int brightness = 100;

  int opt;
  while ((opt = getopt(argc, argv, "b:")) != -1) {
    switch (opt) {
    case 'b': brightness = atoi(optarg); break;
    default:
      return usage(argv[0]);
    }
  }

  if (brightness < 1 || brightness > 100) {
    fprintf(stderr, "Brightness is outside usable range.\n");
    return 1;
  }

  RGBMatrix *matrix = rgb_matrix::CreateMatrixFromOptions(matrix_options,
                                                          runtime_opt);
  if (matrix == NULL)
    return 1;

  matrix->SetBrightness(brightness);

  const bool all_extreme_colors = (brightness == 100);
  if (all_extreme_colors)
      matrix->SetPWMBits(1);


  // Finished. Shut down the RGB matrix.
  // matrix->Clear();
  // delete matrix;

  write(STDOUT_FILENO, "\n", 1);  // Create a fresh new line after ^C on screen
  return 0;
}
