#!/bash/bin

# expand jedi super collection into 'jedi01 + ... + jedi29'
#

list=" aircraft airs_aqua amsr2_gcom-w1 amsua_aqua amsua_metop-b amsua_n15 amsua_n18 amsua_n19 atms_n20 atms_npp avhrr3_metop-b avhrr3_n18 avhrr3_n19 cris-fsr_n20 cris-fsr_npp gmi_gpm gps iasi_metop-b mhs_metop-b mhs_n19 mls55_aura omi_aura ompsnm_npp satwind scatwind sfc sfcship sondes ssmis_f17 "

collect_set="jedi_29_collections.set"
collect_name_vl="jedi_collection_names.vl"

rm -f t1 t2 output
j=0
for i in $list; do
  j=$(( j+1 ))
  j2=$(printf "%02d" "$j")
  echo $i
  sed -e "s#jedi.ObsPlatforms:.*#jedi.ObsPlatforms:         $i#g"  \
      -e "s/jedi/jedi${j2}_$i/g"   \
      jedi_input > t1
  cat t1 >> output
  echo "         'jedi${j2}_$i'"  >> t2  
done

rm  t1
cat output
cat t2
mv  output  $collect_set
mv  t2      $collect_name_vl

#  glue
m4 HISTORY_JOSSE.RC > HISTORY_J29.rc
cp HISTORY_J29.rc   HISTORY.rc

exit
