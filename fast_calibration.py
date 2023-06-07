# PyFAST Calibration v1.1 - GPLv3
# Moritz O. Ziegler, mziegler@gfz-potsdam.de
# Manual:   https://doi.org/10.48440/wsm.2021.003
# Download: https://github.com/MorZieg/PyFAST_Calibration
###############################################################################################
#
# Python Fast Automatic Stress Tensor Calibration v1.1 is a Python 3 translation
# of the FAST Calibration Matlab tool. It supports Moose and Abaqus solver, PyTecplot,
# GeoStressCmd (https://doi.org/10.5880/wsm.2020.001), and runs on Windows and Linux
# systems. It can be run as stand-alone script or called from another script.
#
# The basic principle is explained in the FAST Calibration Manual referenced above. The
# additionally required information is provided in this file. For simple usage refer to
# the user input section only. Additional comments are provided throughout the script.
#
# Important information:
# When using Tecplot Macros (pytecplot = 'off') three steps with the different boundary
# conditions are expected to be loaded in Tecplot. Make sure that the folder variable is set
# correctly and that the subdirectory 'data' exists in the working directory.
# 
# When using PyTecplot:
#   Abaqus:  The native variables stress variables (XX Stress etc.) or SHmax & Shmin are
#        expected.
#      On Windows a *.odb file is expected. (May have to be loaded before to be
#         converted to a readable format.
#      On Linux a *.fil file is expected.
#   Moose:   Three *.dat Tecplot files provided as output by Moose are required. After
#        the name they are expected to be named *_0001.dat, *_0002.dat, and *_0003.dat.
#      The native stress variables (stress_xx etc.) or SHmax & Shmin are expected.
###############################################################################################

#  User input:
solver = 'abaqus' #'moose'
pytecplot = 'on' # 'off'

#  The two stress components used for calibration. Using SHmax and Shmin with
#    PyTecplot automatically triggers the usage of GeoStressCmd.
stress_vars = ['SHmax','Shmin'] #['XX Stress','YY Stress'] # ['stress_xx','stress_yy']

#  The name of the calibration file with three boundary condition scenarios.
name = 'test_calibration'

#  The current folder (only required for Tecplot to export the data).
folder = 'c:\\Data\\User\\Documents\\Modelling\\FAST'

#  The test boundary conditions.
bcs = [[4, 2, 4],[-4, -5, -3]]

#  Stress data records (Location X Y Z, Magnitude in MPa, weight between 0 and 1)
shmax = [[3500, 3500, -2900, 100, 1],[3500, 3500, -2900, 100, 1]]
shmin = [[3500, 3500, -2900, 48, 1]]

###############################################################################################
def main(shmax,shmin,stress_vars,bcs,name,solver,pytecplot):
  import os.path
  import tecplot
  
  # Main script calls functions according to the chosen parameters.
  if pytecplot == 'on':
    if not os.path.exists((name+'.plt')):
      if solver == 'abaqus':
        load_abq(name)
      elif solver == 'moose':
        load_mse(name)
      else:
        print ('ERROR! Specify a solver.')
    else:
      print('Using existing *.plt file')
    [shmax_calib,shmin_calib] = extract_tp(name,solver,shmax,shmin,stress_vars)
    
  elif pytecplot == 'off':
    write_macro(shmax,shmin,stress_vars,name,folder)
    
    # A break appears here in order to execute the macro in Tecplot.
    print ('Execute Macro in Tecplot...')
    input("...then press Enter to continue...")
    
    [shmax_calib,shmin_calib] = load_csv(name,len(shmax),len(shmin),stress_vars)
    
  else:
    print ('ERROR! Indicate if you are using Pytecplot or not.')
  
  # If raw stress data directly from the solver in Pascal (instead of MPa) is
  # used, it is converted to the geoscientific convention (compression positive)
  # and to MPa.
  if stress_vars[0] != 'SHmax':
    shmax_calib = shmax_calib*(-1e-06)
    shmin_calib = shmin_calib*(-1e-06)
  
  [bcx,bcy] = calibration(shmax,shmin,shmax_calib,shmin_calib,bcs)
  
  return [bcx,bcy]
  
###############################################################################################
def load_abq(name):
  # Only required if PyTecplot is used.
  # Load Abaqus output file and save it as *.plt file. Different input files
  # (and syntax) required depending on operating system.
  import tecplot as tp
  import platform

  print('Loading *.odb file')
  if platform.system() == 'Linux':
    tp.macro.execute_command("""$!ReadDataSet  '\"StandardSyntax\" \"1.0\" \"FEALoaderVersion\" \"446\" \"FILENAME_File\" \"%s.fil\" \"AutoAssignStrandIDs\" \"Yes\"'\n"""
    """  DataSetReader = 'ABAQUS .fil Data (FEA)'""" % name)
    
  elif platform.system() == 'Windows':
    tp.macro.execute_command("""$!ReadDataSet  '\"StandardSyntax\" \"1.0\" \"FEALoaderVersion\" \"446\" \"FILENAME_File\" \"%s.odb\" \"AutoAssignStrandIDs\" \"Yes\"'"""
    """DataSetReader = 'ABAQUS Output Database (FEA)'""" % name)
    
  else:
    print ('Platform/OS not recognized')
  
  # Save as *.plt file.
  tp.data.save_tecplot_plt('%s.plt' % name, include_text=False, include_geom=False, include_data_share_linkage=True)
  
###############################################################################################
def load_mse(name):
  # Only required in PyTecplot is used.
  # Load Moose output files consecutively, assign solution times, and generate
  # variable names suitable for GeoStress and GeoStressCmd and save as *.plt file.
  import tecplot as tp

  print('Loading Moose output file')
  # Load first solver output file.
  tp.macro.execute_command("""$!ReadDataSet  '\"%s_0001.dat\" '
    ReadDataOption = New
    ResetStyle = No
    VarLoadMode = ByName
    AssignStrandIDs = Yes
    VarNameList = '\"x\" \"y\" \"z\" \"stress_xx\" \"stress_yy\" \"stress_zz\" \"stress_xy\" \"stress_yz\" \"stress_zx\" \"disp_x\" \"disp_y\" \"disp_z\"'""" % name)
  
  # Append second and third solver output files.
  tp.macro.execute_command("""$!ReadDataSet  '\"%s_0002.dat\" '
    ReadDataOption = Append
    ResetStyle = No
    VarLoadMode = ByName
    AssignStrandIDs = Yes
    VarNameList = '\"x\" \"y\" \"z\" \"stress_xx\" \"stress_yy\" \"stress_zz\" \"stress_xy\" \"stress_yz\" \"stress_zx\" \"disp_x\" \"disp_y\" \"disp_z\"'""" % name)
  
  tp.macro.execute_command("""$!ReadDataSet  '\"%s_0003.dat\" '
    ReadDataOption = Append
    ResetStyle = No
    VarLoadMode = ByName
    AssignStrandIDs = Yes
    VarNameList = '\"x\" \"y\" \"z\" \"stress_xx\" \"stress_yy\" \"stress_zz\" \"stress_xy\" \"stress_yz\" \"stress_zx\" \"disp_x\" \"disp_y\" \"disp_z\"'""" % name)
  
  # Save as *.plt file.
  tp.data.save_tecplot_plt('%s.plt' % name, include_text=False, include_geom=False, include_data_share_linkage=True)
  
###############################################################################################
def extract_tp(name,solver,shmax,shmin,stress_vars):
  # Read the *.plt file created by load_abq or load_mse. If the stress variables
  # SHmax and Shmin are desired, GeoStressCmd is run to compute them. Then the
  # modelled stress state is extracted at the according locations using strextract.
  import tecplot as tp
  import numpy as np
  import platform
  
  model = tp.data.load_tecplot('%s.plt' % name, read_data_option=2)
  
  if platform.system() == 'Linux' and solver == 'abaqus':
    # Convert the cell centered stress tensor variables from the *.fil file to nodal variables.
    cell2nodal(model)
  
  if solver == 'moose':
    rnm_vrbls()
  
  # Run GeoStressCmd if SHmax and Shmin are desired.
  if stress_vars[0] == 'SHmax':
    print ('Running GeoStressCmd...')
    CommandString = 'Stress, 90.0, 0.0, 0.0, 0.0, -1.0E-6, 0, 0, 0, 0, 0, 1, 0, 0, 0'
    tp.macro.execute_extended_command("GeoStressCmd",CommandString)
    print ('Sucessfull!')
  
  # Extract the variables at the acording locations.
  shmax_calib = np.zeros((len(shmax),3))
  for i in range(len(shmax)):
    for k in range(3):
      shmax_calib[i][k] = strextract(shmax[i][0],shmax[i][1],shmax[i][2],k,model,stress_vars[0])
  
  shmin_calib = np.empty((len(shmin),3))
  for i in range(len(shmin)):
    for k in range(3):
      shmin_calib[i][k] = strextract(shmin[i][0],shmin[i][1],shmin[i][2],k,model,stress_vars[1])
  
  return [shmax_calib,shmin_calib]
  
###############################################################################################
def rnm_vrbls():
  import tecplot as tp
  
  # Assign solution time.
  tp.macro.execute_extended_command(command_processor_id='Strand Editor',command='ZoneSet=1-3;AssignStrands=TRUE;StrandValue=1;AssignSolutionTime=TRUE;TimeValue=1;DeltaValue=1;TimeOption=ConstantDelta;')
  
  # Generate variables according to the naming convetion of GeoStress.
  tp.data.operate.execute_equation(equation='{XX Stress} = {stress_xx}')
  tp.data.operate.execute_equation(equation='{YY Stress} = {stress_yy}')
  tp.data.operate.execute_equation(equation='{ZZ Stress} = {stress_zz}')
  tp.data.operate.execute_equation(equation='{XY Stress} = {stress_xy}')
  tp.data.operate.execute_equation(equation='{YZ Stress} = {stress_yz}')
  tp.data.operate.execute_equation(equation='{ZX Stress} = {stress_zx}')
  
  tp.data.operate.execute_equation(equation='{X Displacement} = {disp_x}')
  tp.data.operate.execute_equation(equation='{Y Displacement} = {disp_y}')
  tp.data.operate.execute_equation(equation='{Z Displacement} = {disp_z}')
  
###############################################################################################
def cell2nodal(model):
  import tecplot as tp
  from tecplot.constant import ValueLocation
  
  # Create new stress tensor variables at nodes.
  tp.data.operate.execute_equation('{XX Stress node} = {XX Stress}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{YY Stress node} = {YY Stress}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{ZZ Stress node} = {ZZ Stress}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{XY Stress node} = {XY Stress}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{YZ Stress node} = {YZ Stress}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{ZX Stress node} = {ZX Stress}', value_location=ValueLocation.Nodal)
  
  # Delete the original (cell-centered) stress tensor variables.
  model.delete_variables(model.variable('XX Stress'),model.variable('YY Stress'),model.variable('ZZ Stress'))
  model.delete_variables(model.variable('XY Stress'),model.variable('YZ Stress'),model.variable('ZX Stress'))
  
  # Create stress tensor variables at nodes.
  tp.data.operate.execute_equation('{XX Stress} = {XX Stress node}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{YY Stress} = {YY Stress node}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{ZZ Stress} = {ZZ Stress node}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{XY Stress} = {XY Stress node}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{YZ Stress} = {YZ Stress node}', value_location=ValueLocation.Nodal)
  tp.data.operate.execute_equation('{ZX Stress} = {ZX Stress node}', value_location=ValueLocation.Nodal)
  
  # Delete the temporal stress tensor variables.
  model.delete_variables(model.variable('XX Stress node'),model.variable('YY Stress node'),model.variable('ZZ Stress node'))
  model.delete_variables(model.variable('XY Stress node'),model.variable('YZ Stress node'),model.variable('ZX Stress node'))
  
###############################################################################################
def strextract(x,y,z,zone,model,comp):
  # Function that extracts specified variables at a certain location and zone.
  import tecplot as tp
  
  tecvar = model.variable(comp).index
  result = tp.data.query.probe_at_position(x,y,z,zones=[zone])
  stress = result[0][tecvar]
  
  return stress
  
###############################################################################################
def write_macro(shmax,shmin,stress_vars,name,folder):
  # A Tecplot macro to export the stress state at the calibration points
  # is written.
  import numpy as np
  
  # Create one variable with all locations of calibration points.
  coords = []
  for i in range(len(shmax)):
    coords.append(shmax[i][0:3])
  for i in range(len(shmin)):
    coords.append(shmin[i][0:3])
  
  # Start writing the macro file with its header.
  # (The header may vary depending on Tecplot version.)
  fid =  open('macro_calibration.mcr','w')
  fid.write('#!MC 1410\n\n')
  # Find the number Tecplot assigned to the variables according to their names.
  fid.write('$!GETVARNUMBYNAME |SHMAX|\nNAME = "%s"\n$!GETVARNUMBYNAME |SHMIN|\nNAME = "%s"\n\n' % (stress_vars[0],stress_vars[1]))
  
  # Create 1D zones at the calibration points. At each point 3 zones are created.
  for i in range(len(coords)):
    for j in range(3):
      fid.write('$!CREATERECTANGULARZONE\nIMAX = 1\nJMAX = 1\nKMAX = 1\n')
      fid.write('X1 = %i\nY1 = %i\nZ1 = %i\n' % (coords[i][0],coords[i][1],coords[i][2]))
      fid.write('X2 = %i\nY2 = %i\nZ2 = %i\n\n' % (coords[i][0],coords[i][1],coords[i][2]))
  
  # Interpolate stress state to newly created 1D zones. From each boundary condition
  # scenario at each calibration point the stress state is interpolated to a 1D zone.
  for i in range(len(coords)):
    for x,j in enumerate([1,2,3]):
      fid.write('$!LINEARINTERPOLATE\nSOURCEZONES =  [%i]\n' % j)
      fid.write('DESTINATIONZONE = %i\nVARLIST =  [|SHMAX|,|SHMIN|]\nLINEARINTERPCONST = 0\nLINEARINTERPMODE = DONTCHANGE\n\n' % (3+(i*3)+j))
  
  # Export the two stress components to individually named files in the specified folder.
  for i in range(2):
    fid.write('$!EXTENDEDCOMMAND\nCOMMANDPROCESSORID = \'excsv\'\n')
    if i == 0:
      inst = 'SHMAX'
      id = '_' + stress_vars[0]
    elif i == 1:
      inst = 'SHMIN'
      id = '_' + stress_vars[1]
    
    fid.write('COMMAND = \'FrOp=1:ZnCount=%i:ZnList=[%i-%i]:VarCount=1:VarList=[|%s|]:ValSep=",":FNAME="%s\\data\\%s.csv"\'\n\n' % (len(coords)*3,4,len(coords)*3+3,inst,folder,(name+id)))
  
  # Delet the 1D zones.
  fid.write('$!DELETEZONES [%i-%i]' % (4,len(coords)*3+3))
  
  fid.close()
  
###############################################################################################
def load_csv(name,leshmax,leshmin,stress_vars):
  # Load the files/stress components that were exported from Tecplot with the macro. 
  import csv
  import numpy as np
  
  # Read the SHmax (or other first variable) file.
  shmax_temp = []
  shmax_calib = []
  with open('data/' + name + '_' + stress_vars[0] + '.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      if row != []:
        shmax_temp.append(float(row[0]))
      
  # Read the Shmin (or other second variable) file.
  shmin_temp = []
  shmin_calib = []
  with open('data/' + name + '_' + stress_vars[1] + '.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      if row != []:
        shmin_temp.append(float(row[0]))
      
  # Sort the SHmax (or other first variable) according to calibration points.
  for i in range(leshmax):
    temp = []
    for j in range(3):
      temp.append(shmax_temp[j+i*3])
    shmax_calib.append(temp)
  
  # Sort the Shmin (or other second variable) according to calibration points.
  # Please note that both variables are exported at all calibration points. Thus,
  # calibration points with ONLY SHmax or ONLY Shmin data are still exported for both
  # components. Thus, the first (SHmax) values are discarded in the following.
  for i in range(leshmin):
    temp = []
    for j in range(3):
      temp.append(shmin_temp[j+(leshmax+i)*3])
    shmin_calib.append(temp)
  
  # The variables are converted to a numpy array.
  shmax_calib = np.array(shmax_calib)
  shmin_calib = np.array(shmin_calib)
  
  return [shmax_calib,shmin_calib]
  
###############################################################################################
def calibration(shmax,shmin,shmax_calib,shmin_calib,bcs):
  # Derive the best-fit boundary conditions for the final model using the
  # FAST Calibration algorithm described in the manual.
  import numpy as np
  
  # Apply the weighting of the calibration points.
  dshmin = np.array([shmin_calib[i,:]-shmin[i][3] for i in range(len(shmin))])
  weight = [shmin[i][4] for i in range(len(shmin))]
  dshmin = np.average(dshmin,0,weight)
  
  dshmax = np.array([shmax_calib[i,:]-shmax[i][3] for i in range(len(shmax))])
  weight = [shmax[i][4] for i in range(len(shmax))]
  dshmax = np.average(dshmax,0,weight)
  
  # Transform relevant variables into an array.
  xco = [float(i) for i in bcs[0]]
  yco = [float(i) for i in bcs[1]]
  dshmaxo = [float(i) for i in dshmax]
  dshmino = [float(i) for i in dshmin]
  
  # Setup 'planes' and derive the equation for the isolines of zero deviation.
  for i in range(2):
    v = [xco]
    v.append(yco)
    if i == 0:
      v.append(dshmaxo)
    else:
      v.append(dshmino)
    
    v = np.asarray(v)
    v = np.transpose(v)
    r1 = v[1,:] - v[0,:]
    r2 = v[2,:] - v[0,:]
    
    r2 = np.where(r2 == 0, 0.00001, r2)
    test = [r1[j] / r2[j] for j in range(3)]
    if test[0] == test[1] and test[1] == test[2]:
      print('ERROR! Planes are linearly dependent.')
    
    n = np.cross(r1,r2)
    d = np.dot(n,v[0,:])
    
    if i == 0:
      d_x = d
      n1_x = n[0]
      n2_x = n[1]
    else:
      d_i = d
      n1_i = n[0]
      n2_i = n[1]
      
  # Compute the best-fit boundary conditions.
  if n2_x == 0:
    n2_x = 0.0001
  x = ( n2_i * d_x - n2_x * d_i ) / ( n1_x * n2_i - n2_x * n1_i )
  y = (d_x - n1_x * x) / n2_x
  
  return [x, y]
  
###############################################################################################
if __name__ == '__main__':
  print('Running PyFAST Calibration v1.1')
  [bcx,bcy] = main(shmax,shmin,stress_vars,bcs,name,solver,pytecplot)
  
  # If the function is run as a stand-alone script the boundary conditions are
  # printed to the screen.
  print('Boundary Condition X: ' + str(bcx))
  print('Boundary Condition Y: ' + str(bcy))
###############################################################################################
