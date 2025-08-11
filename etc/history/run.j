#!/bin/bash -l

f=HISTORY_var2.RC
fo=zb
fo2=zc
f2=HISTORY1.rc

sed -e  's#include(.*#include(var2.vl)#g'  $f > $fo
diff $f $fo

echo

sed -e 's/includex/include/g' \
    -e 's/includey/include/g' $fo > $fo2
diff $fo  $fo2



m4 $fo2 > $f2


less $f2
