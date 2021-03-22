[Mesh]
  file = test_model.inp
[]

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Modules/TensorMechanics/Master]
  [./block1]
    strain = SMALL #Small linearized strain, automatically set to XY coordinates
    add_variables = true #Add the variables from the displacement string in GlobalParams
  [../]
[]

[Materials]
  [./elasticity_tensor]
    type = ComputeIsotropicElasticityTensor
    youngs_modulus = 40.0e9
    poissons_ratio = 0.22
  [../]
  [./stress]
    type = ComputeLinearElasticStress
  [../]
[]

[Kernels]
  [./gravity_z]
    type = Gravity
    variable = disp_z
    value = -9.81
    density = 2500
  [../]
[]

[BCs]
  [./X_hold]
    type = DirichletBC
    variable = disp_x
    boundary = east
    value = 0.0
  [../]
  [./Y_hold]
    type = DirichletBC
    variable = disp_y
    boundary = north
    value = 0.0
  [../]
  [./bottom]
    type = DirichletBC
    variable = disp_z
    boundary = bottom
    value = 0.0
  [../]
  [./X_move]
    type = DirichletBC
    variable = disp_x
    boundary = west
    value = 2
  [../]
  [./Y_move]
    type = DirichletBC
    variable = disp_y
    boundary = south
    value = -5
  [../]
[]


[AuxVariables]
  [./stress_xx]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./stress_yy]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./stress_zz]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./stress_xy]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./stress_yz]
    order = CONSTANT
    family = MONOMIAL
  [../]
  [./stress_zx]
    order = CONSTANT
    family = MONOMIAL
  [../]
[]

[AuxKernels]
  [./stress_xx]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_xx
    index_i = 0
    index_j = 0
  [../]
  [./stress_yy]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_yy
    index_i = 1
    index_j = 1
  [../]
  [./stress_zz]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_zz
    index_i = 2
    index_j = 2
  [../]
  [./stress_xy]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_xy
    index_i = 0
    index_j = 1
  [../]
  [./stress_yz]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_yz
    index_i = 2
    index_j = 1
  [../]
  [./stress_zx]
    type = RankTwoAux
    rank_two_tensor = stress
    variable = stress_zx
    index_i = 2
    index_j = 0
  [../]
[]

[Executioner]
  type = Steady

  solve_type = 'NEWTON'

  petsc_options = '-snes_ksp_ew'
  petsc_options_iname = '-pc_type -sub_pc_type -pc_asm_overlap -ksp_gmres_restart'
  petsc_options_value = 'asm lu 1 101'
[]

[Outputs]
  exodus = true
  tecplot = true
  perf_graph = true
[]
