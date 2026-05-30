# Ontology Boundary Validation Against NASA BGA

- Status: deterministic candidate analysis
- Existing coverage: 13
- Alias candidates: 4
- Recommended class candidates: 15
- Recommended property candidates: 5
- High-risk operational detections: 0
- Claim policy: boundary validation only; no automatic ontology expansion.

## Existing Ontology Coverage

- `Atmosphere`
- `Air`
- `Pressure`
- `Airfoil`
- `Wing`
- `Lift`
- `Drag`
- `AngleOfAttack`
- `BoundaryLayer`
- `AerodynamicForce`
- `NewtonLaw`
- `BernoulliPrinciple`
- `Downwash`

## NASA Extension Candidates

- `DynamicPressure` status=`candidate_new_class` change_required=True
- `Velocity` status=`candidate_new_class` change_required=True
- `Thrust` status=`candidate_new_class` change_required=True
- `Weight` status=`candidate_new_class` change_required=True
- `CenterOfPressure` status=`candidate_new_class` change_required=True
- `LiftEquation` status=`candidate_new_class` change_required=False
- `DragEquation` status=`candidate_new_class` change_required=False
- `LiftCoefficient` status=`candidate_new_class` change_required=True
- `DragCoefficient` status=`candidate_new_class` change_required=True
- `ReynoldsNumber` status=`candidate_new_class` change_required=True
- `AerodynamicCenter` status=`candidate_new_class` change_required=True
- `Streamline` status=`candidate_new_class` change_required=True
- `MassFlowRate` status=`candidate_new_class` change_required=True
- `Winglet` status=`candidate_new_class` change_required=False
- `InducedDrag` status=`candidate_new_class` change_required=False
- `Compressibility` status=`candidate_new_class` change_required=True
- `Viscosity` status=`candidate_new_class` change_required=True
- `SurfaceArea` status=`candidate_new_class` change_required=True
- `EquationVariable` status=`candidate_new_class` change_required=True

## Alias Candidates

- `AirDensity` -> `Density`
- `Inclination` -> `AngleOfAttack`
- `Vorticity` -> `WingtipVortex`
- `ReferenceArea` -> `PressureDistribution`

## Out-of-Scope Detections

- `aircraft-specific POH/AFM procedures`
- `emergency checklists`
- `current weather and NOTAMs`
- `ATC clearance`
- `legal flight decisions`
- `maintenance airworthiness decisions`
- `aircraft-specific performance calculations for real flights`
- `runway performance`
- `weight and balance for a real aircraft`
- `aircraft limitations`
- `emergency procedures`
- `route fuel planning`
- `current density altitude for a real airport`

## Claim Safety Notes

- This is deterministic boundary validation, not automatic ontology expansion.
- All new NASA terms are candidates until separately reviewed and accepted.
- NASA educational pages do not create operational readiness or expert certification.
