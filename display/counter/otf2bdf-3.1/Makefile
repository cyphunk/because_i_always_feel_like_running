#
# Copyright 2008 Department of Mathematical Sciences, New Mexico State University
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# DEPARTMENT OF MATHEMATICAL SCIENCES OR NEW MEXICO STATE UNIVERSITY BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

RM = rm
CP = cp
MKINSTALLDIRS = ./mkinstalldirs

CC = gcc
CFLAGS = -Wall -pedantic -g -O2

SRCS = remap.c otf2bdf.c
OBJS = remap.o otf2bdf.o

#
# Point these at the FreeType source directories.
#
INCS = -I/usr/include/freetype2/ 
LIBS =   -lfreetype
LDFLAGS = 

prefix = /usr/local
exec_prefix = ${prefix}
bindir = ${exec_prefix}/bin
mandir = ${prefix}/man

all: otf2bdf

otf2bdf: $(OBJS)
	$(CC) $(STATIC) $(LDFLAGS) -o otf2bdf $(OBJS) $(LIBS)

clean:
	$(RM) -f *.o *BAK *CKP *~ a.out core

realclean: clean
	$(RM) -f otf2bdf

distclean: clean
	$(RM) -f otf2bdf config.* Makefile

.c.o:
	$(CC) $(CFLAGS) $(INCS) -c $< -o $@

install: otf2bdf
	$(MKINSTALLDIRS) $(bindir) $(mandir)/man1
	$(CP) otf2bdf $(bindir)/otf2bdf
	$(CP) otf2bdf.man $(mandir)/man1/otf2bdf.1

uninstall:
	$(RM) -f $(bindir)/otf2bdf
	$(RM) -f $(mandir)/man1/otf2bdf.1

# end of Makefile
