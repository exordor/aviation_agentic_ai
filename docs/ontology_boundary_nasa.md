# NASA Ontology Boundary

This boundary document defines how the NASA Glenn Beginners Guide to Aeronautics
aerodynamics corpus is used to test the current PHAK Chapter 4 task ontology.
The landing-page corpus is collected broadly, but the current ontology boundary
experiment is restricted to the `Lessons in Aerodynamics` subset. It is not an
automatic ontology expansion plan, and it does not claim complete aviation
coverage, expert certification, or operational readiness.

The NASA corpus is used as a second authoritative educational source for
source-diversity evaluation. The safe claim is narrow: NASA Glenn educational
pages can reveal whether the current ontology covers common aerodynamics
learning concepts and where candidate aliases, classes, or relations should be
proposed.

Collection and experiment scope are intentionally separated. Full-corpus
collection supports provenance and future extension. The present experiment uses
the eight `Lessons in Aerodynamics` pages because they align most directly with
the existing PHAK Chapter 4 aerodynamics ontology boundary.

## Layer A - Current Core Ontology Should Cover

| Concept | include_now | class_or_entity_candidate | Relation candidates | Rationale | Risk level | Ontology change required |
| --- | --- | --- | --- | --- | --- | --- |
| Atmosphere | true | Atmosphere | describes, affects | Existing PHAK atmosphere concept used for aerodynamics context. | learning | false |
| Air | true | Air | hasMedium, affects | Existing fluid medium concept. | learning | false |
| AirDensity | true | AirDensity | affects, dependsOn | NASA uses air density and pressure terms; current ontology may map this to Density. | learning | alias candidate |
| Pressure | true | Pressure | affects, variesWith | Existing pressure concept should cover NASA pressure explanations. | learning | false |
| DynamicPressure | true | DynamicPressure | dependsOn, hasEquation | NASA has a dedicated dynamic pressure page. | learning | candidate |
| Velocity | true | Velocity | affects, dependsOn | NASA equations and airflow explanations use speed/velocity. | learning | candidate |
| Airfoil | true | Airfoil | hasComponent, produces | Existing airfoil concept. | learning | false |
| Wing | true | Wing | hasComponent, produces | Existing wing concept. | learning | false |
| Lift | true | Lift | producedBy, increasesWith | Existing aerodynamic force concept. | learning | false |
| Drag | true | Drag | producedBy, increasesWith | Existing aerodynamic force concept. | learning | false |
| Thrust | true | Thrust | balances, opposes | NASA four-forces material includes thrust. | learning | candidate |
| Weight | true | Weight | balances, opposes | NASA four-forces material includes weight. | learning | candidate |
| AngleOfAttack / Inclination | true | AngleOfAttack | affects, increasesWith | Current ontology has AngleOfAttack; NASA often uses inclination. | learning | alias candidate |
| BoundaryLayer | true | BoundaryLayer | affectedBy, causes | Existing boundary-layer concept. | learning | false |
| CenterOfPressure | true | CenterOfPressure | locatedAt, shiftsWith | NASA has a dedicated center-of-pressure page. | learning | candidate |
| AerodynamicForce | true | AerodynamicForce | decomposesInto | Existing aerodynamic force superclass. | learning | false |
| NewtonLaw | true | NewtonLaw | explains | Existing physics principle. | learning | false |
| BernoulliPrinciple | true | BernoulliPrinciple | explains | Existing physics principle. | learning | false |

## Layer B - NASA Extension Candidates

These concepts are candidates because NASA BGA includes aerodynamics lessons with
more formula, coefficient, and flow-detail coverage than the current PHAK
Chapter 4 task ontology requires.

| Concept | include_now | class_or_entity_candidate | Relation candidates | Rationale | Risk level | Ontology change required |
| --- | --- | --- | --- | --- | --- | --- |
| LiftEquation | false | LiftEquation | hasVariable, hasCoefficient | Needed only if equation-level KG extraction is evaluated. | learning | candidate |
| DragEquation | false | DragEquation | hasVariable, hasCoefficient | Needed only if equation-level KG extraction is evaluated. | learning | candidate |
| LiftCoefficient | false | LiftCoefficient | hasCoefficient, dependsOn | NASA has coefficient explanations. | learning | candidate |
| DragCoefficient | false | DragCoefficient | hasCoefficient, dependsOn | Candidate for equation-aware extraction. | learning | candidate |
| ReynoldsNumber | false | ReynoldsNumber | dependsOn, explains | Candidate for fluid/aerodynamic regime explanations. | learning | candidate |
| AerodynamicCenter | false | AerodynamicCenter | locatedAt, contrastsWith | NASA has a dedicated aerodynamic-center page. | learning | candidate |
| Streamline | false | Streamline | describesFlow | Flow visualization candidate. | learning | candidate |
| MassFlowRate | false | MassFlowRate | hasVariable, dependsOn | Candidate for equation explanations. | learning | candidate |
| Winglet | false | Winglet | reduces, affects | Candidate extension for induced drag and vortices. | learning | candidate |
| InducedDrag | false | InducedDrag | causedBy, reducedBy | Candidate extension from wingtip/winglet explanations. | learning | candidate |
| Vorticity | false | Vorticity | causes, associatedWith | May map to WingtipVortex for current scope. | learning | alias candidate |
| Downwash | false | Downwash | causedBy, reduces | Existing ontology includes Downwash. | learning | false |
| Compressibility | false | Compressibility | affects | Candidate only if NASA corpus includes compressible-flow topics. | learning | candidate |
| Viscosity | false | Viscosity | affects | Candidate for boundary-layer explanations. | learning | candidate |
| SurfaceArea | false | SurfaceArea | hasVariable | Candidate for equation variables. | learning | candidate |
| ReferenceArea | false | ReferenceArea | hasVariable | Candidate for lift/drag equations. | learning | candidate |
| EquationVariable | false | EquationVariable | hasVariable | Candidate for formula-aware extraction. | learning | candidate |

## Layer C - Out Of Scope For Current Thesis

- Aircraft-specific POH/AFM procedures.
- Emergency checklists.
- Current weather and NOTAMs.
- ATC clearance.
- Legal flight decisions.
- Maintenance airworthiness decisions.
- Aircraft-specific performance calculations for real flights.

## Layer D - Deferred Operational/Procedure Concepts

- Runway performance.
- Weight and balance for a real aircraft.
- Aircraft limitations.
- Emergency procedures.
- Route fuel planning.
- Current density altitude for a real airport.

## Claim Safety

Safe wording:

- "NASA Glenn educational pages are added as a second authoritative learning source."
- "The NASA corpus enables cross-source evidence evaluation for aerodynamics concepts."
- "Ontology coverage is evaluated against NASA aerodynamics concepts."
- "Results are internal thesis evidence, not expert certification."

Unsafe wording:

- "NASA makes the system reliable."
- "The system is now flight-safe."
- "The ontology fully covers aviation."
- "The system can answer operational questions."

The advisory boundary remains unchanged: the system is for aviation learning and
decision support only and does not replace POH/AFM, approved checklists, ATC
instructions, instructor guidance, regulations, or pilot judgment.
