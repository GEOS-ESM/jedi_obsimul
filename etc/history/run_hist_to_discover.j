#!/bin/bash -l

# usage:
#   sh run_hist_to_discover.j  1    # sync to GCM run
#                              2    # sync to MAPL run

if [[ $# -eq 0 || ( $# -eq 1 && $1 == 1 ) ]]; then 

#---------- for use HISTORY_JOSSE.RC  ---------
f=HISTORY_JOSSE.RC
f2=HISTORY.rc
d=/discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/c24_Aug6_v12-rc17/scratch/.
d=/discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/c24_v12_rc18_Sep2/scratch/.

m4 $f > $f2
cmd="scp $f2 yyu11@discover:$d"
echo $cmd
bash -c "$cmd"

exit

##cp /discover/nobackup/bmauer/tmp/lambert/lambert_grid.nc4 /discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/c24_Aug6_v12-rc17/scratch/

elif [[ ( $# -eq 1 && $1 == 2 ) ]]; then

#---------- for use HISTORY_var2.RC  ---------
f=HISTORY_var2.RC
fo=zb
fo2=zc
f2=HISTORY1.rc
d=/discover/nobackup/projects/gmao/aist-nr/yyu11/run_geos_su17/mapl_test_c12_traj_use_grid/.

sed -e  's#include(.*#include(var2.vl)#g'  $f > $fo
diff $f $fo

echo

sed -e 's/includex/include/g' \
    -e 's/includey/include/g' $fo > $fo2
diff $fo  $fo2
m4 $fo2 > $f2



# on Mac
sed -e 's#/discover/#/Volumes/T9/yonggang/discover/#g' $f2 > za
cp za  /Users/yyu11/bkup_run/run/test_c12_illustrate/$f2
exit



# on discover
cmd="scp $f2 yyu11@discover:$d"
echo $cmd
bash -c "$cmd"
less $f2
exit


fi
