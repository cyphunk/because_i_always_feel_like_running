#!/usr/bin/env bash
# create bdf fonts
# otf2bdf: https://www.math.nmsu.edu/%7Emleisher/Software/otf2bdf/
#          ./configure CPPFLAGS="-I/usr/include/freetype2/"
MINSIZEPT=12
MAXSIZEPT=72
cd $(basename $0)
mkdir ourfonts
fonts="/usr/share/fonts/gsfonts/NimbusSans-Regular.otf /usr/share/fonts/adobe-source-sans-pro/SourceSansPro-Light.otf /usr/share/fonts/adobe-source-sans-pro/SourceSansPro-Regular.otf  /usr/share/fonts/adobe-source-sans-pro/SourceSansPro-Black.otf"
for font in $fonts; do
  for size in $(eval {$MINSIZEPT..$MAXSIZEPT}) ; do
    test $(($size % 2)) -eq 1 && continue;
    echo $font $size;
    name=$(basename $font)
    ./otf2bdf-3.1/otf2bdf -p $size $font > ourfonts/${name}-${size}.bdf
  done
doneh
