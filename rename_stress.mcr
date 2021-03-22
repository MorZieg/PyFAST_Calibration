#!MC 1410
# This Tecplot macro script renames the stress tensor and displacement variables from a Moose output file to be compatible with GeoStress.
#
# Rename
$!AlterData 
  Equation = '{XX Stress} = {stress_xx}'
$!AlterData 
  Equation = '{YY Stress} = {stress_yy}'
$!AlterData 
  Equation = '{ZZ Stress} = {stress_zz}'
$!AlterData 
  Equation = '{XY Stress} = {stress_xy}'
$!AlterData 
  Equation = '{YZ Stress} = {stress_yz}'
$!AlterData 
  Equation = '{ZX Stress} = {stress_zx}'
$!AlterData 
  Equation = '{X Displacement} = {disp_x}'
$!AlterData 
  Equation = '{Y Displacement} = {disp_y}'
$!AlterData 
  Equation = '{Z Displacement} = {disp_z}'
#
# Delete the old stress tensor variables.
$!GetVarNumByName |XX|
  Name = "stress_xx"
$!GetVarNumByName |YY|
  Name = "stress_yy"
$!GetVarNumByName |ZZ|
  Name = "stress_zz"
$!GetVarNumByName |XY|
  Name = "stress_xy"
$!GetVarNumByName |YZ|
  Name = "stress_yz"
$!GetVarNumByName |ZX|
  Name = "stress_zx"
$!GetVarNumByName |X|
  Name = "disp_x"
$!GetVarNumByName |Y|
  Name = "disp_y"
$!GetVarNumByName |Z|
  Name = "disp_z"
$!DeleteVars [|XX|,|YY|,|ZZ|,|XY|,|YZ|,|ZX|,|X|,|Y|,|Z|]