#!/bin/bash -l


#---------- for use HISTORY_JOSSE.RC  ---------

f=HISTORY_JOSSE.RC
f2=HISTORY.rc

m4 $f > $f2
echo "mv /discover/nobackup/yyu11/trash/$f2  ."
scp $f2 yyu11@discover:/discover/nobackup/yyu11/trash/.
exit

##cp /discover/nobackup/bmauer/tmp/lambert/lambert_grid.nc4 /discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/c24_Aug6_v12-rc17/scratch/



#---------- for use HISTORY_var2.RC  ---------

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
