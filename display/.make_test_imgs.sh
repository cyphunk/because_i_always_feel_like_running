#!/usr/bin/bash


(
echo "P2"
echo "# Column (width) Row (height)"
echo -e "$1 $2\n1"

# Create checkers patter
for row in `seq 1 $2` ; do
    for col in `seq 1 $1` ; do
        # add row so that it switches polarity with each row
        test `expr $(($col+$row)) % 2` -eq 1 && echo -n "1 " || echo -n "0 "
    done
    echo
done
) > /tmp/t.ppm
convert /tmp/t.ppm ./test-img-${1}x${2}.png


# t=`expr $1 / 8`
# for i in `seq 1 4`; do
#     for i in `seq 1 $t`; do
#         for i in `seq 1 4`; do
#             for i in `seq 1 $t`; do echo -n "1 "; done
#             for i in `seq 1 $t`; do echo -n "0 "; done
#         done
#         echo
#     done
#     for i in `seq 1 $t`; do
#         for i in `seq 1 4`; do
#             for i in `seq 1 $t`; do echo -n "0 "; done
#             for i in `seq 1 $t`; do echo -n "1 "; done
#         done
#         echo
#     done
# done
