#!MC 1410
# This Tecplot macro script converts the cell centered stress tensor variables to nodal variables.
#
# Create new nodal variables
$!AlterData 
  ValueLocation = Nodal
  Equation = '{XX Stress node} = {XX Stress}'
$!AlterData 
  ValueLocation = Nodal
  Equation = '{YY Stress node} = {YY Stress}'
$!AlterData 
  ValueLocation = Nodal
  Equation = '{ZZ Stress node} = {ZZ Stress}'
$!AlterData 
  ValueLocation = Nodal
  Equation = '{XY Stress node} = {XY Stress}'
$!AlterData 
  ValueLocation = Nodal
  Equation = '{YZ Stress node} = {YZ Stress}'
$!AlterData 
  ValueLocation = Nodal
  Equation = '{ZX Stress node} = {ZX Stress}'
#
# Delete the old stress tensor variables.
$!GetVarNumByName |XX|
  Name = "XX Stress"
$!GetVarNumByName |YY|
  Name = "YY Stress"
$!GetVarNumByName |ZZ|
  Name = "ZZ Stress"
$!GetVarNumByName |XY|
  Name = "XY Stress"
$!GetVarNumByName |YZ|
  Name = "YZ Stress"
$!GetVarNumByName |ZX|
  Name = "ZX Stress"
$!DeleteVars [|XX|,|YY|,|ZZ|,|XY|,|YZ|,|ZX|]
#
# Create new nodal stress tensor variables.
$!AlterData 
  Equation = '{XX Stress} = {XX Stress node}'
$!AlterData 
  Equation = '{YY Stress} = {YY Stress node}'
$!AlterData 
  Equation = '{ZZ Stress} = {ZZ Stress node}'
$!AlterData 
  Equation = '{XY Stress} = {XY Stress node}'
$!AlterData 
  Equation = '{YZ Stress} = {YZ Stress node}'
$!AlterData 
  Equation = '{ZX Stress} = {ZX Stress node}'
#
# Delete the temporary variables.
$!GetVarNumByName |XX|
  Name = "XX Stress node"
$!GetVarNumByName |YY|
  Name = "YY Stress node"
$!GetVarNumByName |ZZ|
  Name = "ZZ Stress node"
$!GetVarNumByName |XY|
  Name = "XY Stress node"
$!GetVarNumByName |YZ|
  Name = "YZ Stress node"
$!GetVarNumByName |ZX|
  Name = "ZX Stress node"
$!DeleteVars [|XX|,|YY|,|ZZ|,|XY|,|YZ|,|ZX|]

