# NASA Glenn Aerodynamics Source Scope

## Purpose

NASA Glenn Beginner's Guide to Aeronautics aerodynamics pages are added as a
second authoritative learning source beyond FAA PHAK Chapter 4. The landing page
is treated as a source catalog: all unique content links discovered under the
page are collected as the NASA BGA corpus, while the current experiment uses only
the `Lessons in Aerodynamics` subset. The objective is source-diversity testing:
can the current PHAK Chapter 4 task ontology, chunking strategies, KG extraction
profile, and RAG retrieval pipeline transfer to another official aerodynamics
education corpus?

This is not an operational readiness expansion. NASA Glenn educational pages are
source-scoped learning material for aerodynamics concepts, not POH/AFM
procedures, ATC instructions, checklists, weather, NOTAMs, regulations, or legal
flight authority.

## Suitability

- Official NASA Glenn Research Center educational source.
- Overlaps with PHAK Chapter 4 concepts such as air, pressure, lift, drag,
  angle of attack, boundary layer, wing geometry, center of pressure, and
  Newton/Bernoulli explanations.
- Provides focused lessons including aerodynamic forces, dynamic pressure,
  center of pressure, aerodynamic center, boundary layer, four forces, lift,
  drag, lift equation, drag equation, and winglets.
- Web-page structure differs from the current PDF source, which makes it useful
  for chunking and metadata generalization tests.

## Collection And Experiment Boundary

- Full collection scope: every unique content page discovered from the NASA
  Glenn `Guide to Aerodynamics` landing page.
- Current experiment subset: the `Lessons in Aerodynamics` section only:
  aerodynamic forces, dynamic pressure, center of pressure, aerodynamic center,
  Reynolds number interactive, boundary layer, mass flow rate, and streamlines.
- Other collected sections such as object motion, aircraft motion, airplane
  parts, aircraft forces, thrust, weight, lift, drag, and gliders are retained as
  future extension material and are not used for the current primary experiment.
- Interactive pages are collected when present, but their extracted text is
  reported as educational web evidence only and is not treated as a complete
  simulator-state extraction.

## Can Support

- Educational aerodynamics QA when answers are grounded in retrieved NASA or
  FAA evidence.
- Cross-source evidence retrieval for concepts shared by FAA PHAK Chapter 4 and
  NASA Glenn lessons.
- Ontology boundary validation by comparing current core ontology concepts to
  NASA aerodynamics concepts.
- KG coverage expansion analysis and proposal-only ontology extensions.
- Chunking stability checks across PDF and web educational source types.

## Cannot Support

- Operational flight decisions.
- Current weather, NOTAM, TFR, or airport condition answers.
- ATC clearance interpretation or compliance.
- POH/AFM procedure replacement.
- Emergency checklist actions.
- External aviation expert certification.
- A claim that the ontology is a complete aviation ontology.

## Safe Wording

- "NASA Glenn educational pages are added as a second authoritative learning
  source."
- "The NASA corpus enables cross-source evidence evaluation for aerodynamics
  concepts."
- "Ontology coverage is evaluated against NASA aerodynamics concepts."
- "Results are internal thesis evidence, not expert certification."
- "NASA source integration supports internal source-diversity evaluation, not
  external aviation certification."

## Unsafe Wording

- "NASA makes the system reliable."
- "The system is now flight-safe."
- "The ontology fully covers aviation."
- "The system can answer operational questions."
- "NASA validates the ontology completely."

## Preserved Advisory Boundary

The system is for aviation learning and decision support only and does not
replace POH/AFM, approved checklists, ATC instructions, instructor guidance,
regulations, or pilot judgment.
