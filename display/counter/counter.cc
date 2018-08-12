// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
// This is a slightly modified version of the clock example that comes with
// the rgb-matrix library
/*
~pi/git/display/counter/counter --led-gpio-mapping=adafruit-hat-pwm  --led-rows=32 --led-cols=64 --led-pixel-mapper="S-mapper;Rotate:90" --led-multiplexing=0 --led-chain=6 --led-slowdown-gpio=2 -d "%S" -m -C 255,0,0 -f ~pi/git/display/counter/ourfonts/SourceSansPro-Regular.otf-62.bdf -y -25 -x 0

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


#include <lo/lo.h>
#include <lo/lo_cpp.h>

using namespace rgb_matrix;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}

volatile bool pauseclock = false;
// Server sends SIGUSR1 (10):
static void PauseToggle(int signo) {
  pauseclock = !pauseclock;
}
// Server sends SIGUSR2 (12):
static void PauseOff(int signo) {
  pauseclock = false;
}

static int usage(const char *progname) {
  fprintf(stderr, "usage: %s [options]\n", progname);
  fprintf(stderr, "Reads text from stdin and displays it. "
          "Empty string: clear screen\n");
  fprintf(stderr, "Options:\n");
  rgb_matrix::PrintMatrixFlags(stderr);
  fprintf(stderr,
          "\t-d <time-format>  : Default '%%M:%%S'. See strftime()\n"
          "\t-m <decimals>     : append milliseconds of 1, 2 or 3 decimals (Default: none)\n"
          "\t-f <font-file>    : Use given font.\n"
          "\t-b <brightness>   : Sets brightness percent. Default: 100.\n"
          "\t-x <x-origin>     : X-Origin of displaying text (Default: 0)\n"
          "\t-y <y-origin>     : Y-Origin of displaying text (Default: 0)\n"
          "\t-S <spacing>      : Spacing pixels between letters (Default: 0)\n"
          "\t-C <r,g,b>        : Color. Default 255,255,0\n"
          "\t-B <r,g,b>        : Background-Color. Default 0,0,0\n"
          "\t-O <r,g,b>        : Outline-Color, e.g. to increase contrast.\n"
          "\t-s <port>         : enable osc on port\n"
          );

  return 1;
}

static bool parseColor(Color *c, const char *str) {
  return sscanf(str, "%hhu,%hhu,%hhu", &c->r, &c->g, &c->b) == 3;
}

static bool FullSaturation(const Color &c) {
    return (c.r == 0 || c.r == 255)
        && (c.g == 0 || c.g == 255)
        && (c.b == 0 || c.b == 255);
}

int main(int argc, char *argv[]) {
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return usage(argv[0]);
  }

  const char *time_format = "%M:%S";
  Color color(255, 255, 0);
  Color bg_color(0, 0, 0);
  Color outline_color(0,0,0);
  bool with_outline = false;

  volatile bool append_milli = false;
  int millidecimal = 1;

  const char *bdf_font_file = NULL;
  int x_orig = 0;
  int y_orig = 0;
  int brightness = 100;
  int letter_spacing = 0;
  int osc_port = 0;
  volatile bool osc_enabled = false;
  int osc_received = 0;

  int opt;
  while ((opt = getopt(argc, argv, "x:y:f:C:B:O:b:S:d:m:s:")) != -1) {
    switch (opt) {
    case 'd': time_format = strdup(optarg); break;
    case 'm': millidecimal = atoi(optarg); append_milli = true; break;
    case 'b': brightness = atoi(optarg); break;
    case 'x': x_orig = atoi(optarg); break;
    case 'y': y_orig = atoi(optarg); break;
    case 'f': bdf_font_file = strdup(optarg); break;
    case 'S': letter_spacing = atoi(optarg); break;
    case 's': osc_port = atoi(optarg); break;
    case 'C':
      if (!parseColor(&color, optarg)) {
        fprintf(stderr, "Invalid color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      break;
    case 'B':
      if (!parseColor(&bg_color, optarg)) {
        fprintf(stderr, "Invalid background color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      break;
    case 'O':
      if (!parseColor(&outline_color, optarg)) {
        fprintf(stderr, "Invalid outline color spec: %s\n", optarg);
        return usage(argv[0]);
      }
      with_outline = true;
      break;
    default:
      return usage(argv[0]);
    }
  }

  if (bdf_font_file == NULL) {
    fprintf(stderr, "Need to specify BDF font-file with -f\n");
    return usage(argv[0]);
  }

  /*
   * Load font. This needs to be a filename with a bdf bitmap font.
   */
  rgb_matrix::Font font;
  if (!font.LoadFont(bdf_font_file)) {
    fprintf(stderr, "Couldn't load font '%s'\n", bdf_font_file);
    return 1;
  }
  rgb_matrix::Font *outline_font = NULL;
  if (with_outline) {
      outline_font = font.CreateOutlineFont();
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

  const bool all_extreme_colors = (brightness == 100)
      && FullSaturation(color)
      && FullSaturation(bg_color)
      && FullSaturation(outline_color);
  if (all_extreme_colors)
      matrix->SetPWMBits(1);

  const int x = x_orig;
  int y = y_orig;

  FrameCanvas *offscreen = matrix->CreateFrameCanvas();

  // osc
  lo::ServerThread st(osc_port);
  if (osc_port > 0) {
    printf("using OSC port %d\n", osc_port);
    if (!st.is_valid()) {
      fprintf(stderr, "OSC failed to start.\n");
    }
    else {
      osc_enabled = true;
      // not available in the liblo 2014.01.27 found on rasbian
      // https://github.com/radarsat1/liblo/tree/e97ff7262894a36bb52335bdd1581a5198d8eb27
      // st.set_callbacks([&st](){printf("Thread init: %p.\n",&st);},
      //       [](){printf("Thread cleanup.\n");});
      // use cpp example from that commit
      printf("osc URL %s", st.url());
      st.add_method("int", "i",
                    [&osc_received](lo_arg **argv, int)
                    {
                     printf("int (%d): %d\n", ++osc_received, argv[0]->i);
                    }
                   );
     st.start();
    }
  }

  char text_buffer[256];
  struct timeval tv;
  struct timeval tv_first;
  struct tm tm;
  time_t elapsedsec;
  int millisec;
  int len;

  gettimeofday(&tv_first, NULL);


  signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);
  signal(SIGUSR1, PauseToggle);
  signal(SIGUSR2, PauseOff);

  // stdin nonblocking
  fcntl(0, F_SETFL, fcntl(0, F_GETFL) | O_NONBLOCK);
  char input = 0;

  while (!interrupt_received) {
      // input = fgetc(stdin);

      // change brightness from stdin
      input = getchar();
      if (input == 'q' || input =='a' || input == 's') {
        switch (input) {
          case 'q':
            if (brightness < 100) brightness += 1;
            matrix->SetBrightness(brightness);
            // BTW if you start app with brightness 100, then reducing below 70 results in all leds off. so start with -b 99 hack
            // if (  (brightness == 100)
            //     && FullSaturation(color)
            //     && FullSaturation(bg_color)
            //     && FullSaturation(outline_color) )
            //   matrix->SetPWMBits(1);
            // else
            //   matrix->SetPWMBits(0);

            break;
          case 'a':
            if (brightness > 0) brightness -= 1;
            matrix->SetBrightness(brightness);
            break;
          default:
            fprintf(stderr, "input: %c, brightness: %d\n", input, brightness);
            input = 0;
        }
      }
      input = 0;

      if (!pauseclock || elapsedsec <= 0)
        gettimeofday(&tv, NULL);
      elapsedsec = tv.tv_sec-tv_first.tv_sec;
      localtime_r(&elapsedsec, &tm);
      strftime(text_buffer, sizeof(text_buffer), time_format, &tm);
      if (append_milli) {
          // gettimeofday(&tv, NULL);
          millisec = lrint(tv.tv_usec/1000.0); // Round to nearest millisec
          len = strlen(text_buffer);
          if (millisec > 999) {
              millisec = 0;
          }
          if (millidecimal == 3)
            sprintf(text_buffer+len,".%03d",millisec);
          else if (millidecimal == 2)
            sprintf(text_buffer+len,".%02d",millisec/10);
          else //1
            sprintf(text_buffer+len,".%01d",millisec/100);
      }



      offscreen->Fill(bg_color.r, bg_color.g, bg_color.b);
      if (outline_font) {
          rgb_matrix::DrawText(offscreen, *outline_font,
                               x - 1, y + font.baseline(),
                               outline_color, NULL, text_buffer,
                               letter_spacing - 2);
      }
      rgb_matrix::DrawText(offscreen, font, x, y + font.baseline(),
                           color, NULL, text_buffer,
                           letter_spacing);

      // Wait until we're ready to show it.
      //clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &next_time, NULL);

      // Atomic swap with double buffer
      offscreen = matrix->SwapOnVSync(offscreen);

      // next_time.tv_sec += 1;

      usleep(10000); // sleep 1 ms
  }

  // Finished. Shut down the RGB matrix.
  matrix->Clear();
  delete matrix;

  write(STDOUT_FILENO, "\n", 1);  // Create a fresh new line after ^C on screen
  return 0;
}

void flush_input(char userInput[]) {
  if(strchr(userInput, '\n') == NULL) {
    /* If there is no new line found in the input, it means the [enter] character
    was not read into the input, so fgets() must have truncated the input
    therefore it would not put the enter key into the input.  The user would
    have typed in too much, so we would have to clear the buffer. */
    int ch;
    while ( (ch = getchar()) != '\n' && ch != EOF );
  } else {
    //If there is a new line, lets remove it from our input.  fgets() did not need to truncate
    userInput[strcspn(userInput, "\r\n")] = 0;
  }
}
