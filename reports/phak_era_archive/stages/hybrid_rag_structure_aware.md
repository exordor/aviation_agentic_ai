# Hybrid RAG Experiment

- Run ID: `hybrid-rag-20260519T012426Z`
- Questions: 10
- Chunks: `data/chunks/06_phak_ch4_0.structure_aware.jsonl`
- KG: `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`
- Chroma collection: `phak_ch4_chunks_structure_aware`
- Chunking strategy: `structure_aware`
- Rebuild chunks/index/KG: False / False / False

## Agent Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Aggregate Metrics

### Retrieval

| Mode | Recall@5 | MRR@5 | Context Precision@5 |
| --- | ---: | ---: | ---: |
| vector | 1.0 | 0.82 | 0.52 |
| graph | 0.9 | 0.7033 | 0.56 |
| hybrid | 1.0 | 0.7367 | 0.52 |

### KG Evidence

| Mode | Evidence coverage | Avg triples | Provenance complete | Avg invalid triples |
| --- | ---: | ---: | ---: | ---: |
| vector | 0.0 | 0.0 | 0.0 | 0.0 |
| graph | 0.9 | 7.3 | 1.0 | 0.0 |
| hybrid | 0.9 | 7.3 | 1.0 | 0.0 |

### LLM Answer

| Mode | Citation completeness | Insufficient-evidence abstention | Answer present |
| --- | ---: | ---: | ---: |
| vector | 1.0 | 0.2 | 1.0 |
| graph | 1.0 | 0.1 | 1.0 |
| hybrid | 1.0 | 0.0 | 1.0 |

## Hybrid Lift

- vs vector Recall@5: 0.0
- vs graph Recall@5: 0.1

## Question Results

### 06-phak-ch4-0-p00-fa9830b888

- Question: How should atmosphere, air, and constituent gases be modeled as a composition structure?
- Source page: 0
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Model the composition structure as:

- **Atmosphere** is the whole system, an **envelope of air** surrounding Earth.  
- **Atmosphere** **has component** **air**.  
- **Air** is a **mixture of gases**.  
- The atmosphere is composed of **78% nitrogen**, **21% oxygen**, and **1% other gases** (e.g., argon, helium).  
- **Oxygen** is a **part of the atmosphere**, and the evidence also notes that most atmospheric oxygen is below **35,000 feet**.  

This supports a simple composition hierarchy such as:

**Atmosphere → Air → constituent gases (nitrogen, oxygen, other gases)**

Citations: chunk **06_phak_ch4_0-structure_aware-p00-c04** p.0; triple **06_phak_ch4_0-structure_aware-p00-c04-kg00-8748d82ca7**; triple **06_phak_ch4_0-structure_aware-p00-c04-kg01-898cdb205b**; triple **06_phak_ch4_0-structure_aware-p00-c06-kg02-cb7d201076**; triple **06_phak_ch4_0-structure_aware-p00-c07-kg00-bcf45f34cc**.

### 06-phak-ch4-0-p01-dbcda7dbf4

- Question: What classes and relations represent air as a fluid with viscosity, friction, and a boundary layer on a wing?
- Source page: 1
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Air is represented as a **fluid** with **viscosity**, and the wing interaction is represented through **friction** and the **boundary layer**:

- **Air / Fluid**: air is a fluid; gases like air are also fluids, and fluids have slight resistance called viscosity.  
  - Pages/chunks: p.1, `06_phak_ch4_0-structure_aware-p01-c02`; p.1, `06_phak_ch4_0-structure_aware-p01-c06`
  - KG triples: `06_phak_ch4_0-structure_aware-p01-c02-kg00-178e9ee3e0`, `06_phak_ch4_0-structure_aware-p01-c02-kg01-a5b105db61`, `06_phak_ch4_0-structure_aware-p01-c06-kg00-d540390ba0`

- **Viscosity / friction / drag relation**: the boundary layer adheres to the wing by friction, and viscosity is the air’s tendency to stick to itself; together these resist airflow and are called drag.  
  - Page/chunk: p.2, `06_phak_ch4_0-structure_aware-p02-c101`
  - KG triple: `06_phak_ch4_0-structure_aware-p02-c101-kg03-856c4e4d9d`

- **Boundary layer**: the layer of air molecules that adhere to the wing surface because of friction.  
  - Page/chunk: p.1, `06_phak_ch4_0-structure_aware-p01-c08`; p.2, `06_phak_ch4_0-structure_aware-p02-c101`
  - KG triples: `06_phak_ch4_0-structure_aware-p01-c08-kg03-b158087c7c`, `06_phak_ch4_0-structure_aware-p02-c101-kg00-88fb08cc69`

Citations: p.1 `06_phak_ch4_0-structure_aware-p01-c02`, `06_phak_ch4_0-structure_aware-p01-c06`, `06_phak_ch4_0-structure_aware-p01-c08`; p.2 `06_phak_ch4_0-structure_aware-p02-c101`; KG `06_phak_ch4_0-structure_aware-p01-c02-kg00-178e9ee3e0`, `...-kg01-a5b105db61`, `...-kg00-d540390ba0`, `...-kg03-856c4e4d9d`, `...-kg03-b158087c7c`, `...-kg00-88fb08cc69`.

### 06-phak-ch4-0-p02-dafae1ecbc

- Question: How should standard atmosphere values for pressure, temperature, and density be modeled?
- Source page: 2
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Standard atmosphere values should be modeled as **standard sea-level reference conditions**: pressure is the **standard sea level pressure** under the **Standard Atmosphere** ([chunk_id=06_phak_ch4_0-structure_aware-p02-c32 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c34 page=2], KG triples [triple_id=06_phak_ch4_0-structure_aware-p02-c32-kg02-342fce025c], [triple_id=06_phak_ch4_0-structure_aware-p02-c34-kg02-a5df06e0ff]); the standard atmosphere chart is organized by **altitude, pressure, and temperature** ([chunk_id=06_phak_ch4_0-structure_aware-p02-c49 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c47 page=2], KG triple [triple_id=06_phak_ch4_0-structure_aware-p02-c49-kg01-af3d2c1ffc], [triple_id=06_phak_ch4_0-structure_aware-p02-c49-kg02-acb42ecf0e]); and at sea level the standard pressure is about **14.70 psi** ([chunk_id=06_phak_ch4_0-structure_aware-p02-c106 page=2], KG triple [triple_id=06_phak_ch4_0-structure_aware-p02-c106-kg00-13a52f3cfe]). The retrieved PHAK Chapter 4 materials here do **not** provide enough grounded evidence to state a specific standard-atmosphere **density** value.

Citations: [chunk_id=06_phak_ch4_0-structure_aware-p02-c32 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c34 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c49 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c47 page=2], [chunk_id=06_phak_ch4_0-structure_aware-p02-c106 page=2]; KG [triple_id=06_phak_ch4_0-structure_aware-p02-c32-kg02-342fce025c], [triple_id=06_phak_ch4_0-structure_aware-p02-c34-kg02-a5df06e0ff], [triple_id=06_phak_ch4_0-structure_aware-p02-c49-kg01-af3d2c1ffc], [triple_id=06_phak_ch4_0-structure_aware-p02-c49-kg02-acb42ecf0e], [triple_id=06_phak_ch4_0-structure_aware-p02-c106-kg00-13a52f3cfe]

### 06-phak-ch4-0-p03-f463ba25ee

- Question: What causal schema links pressure altitude, density altitude, humidity, air density, and aircraft performance?
- Source page: 3
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The grounded causal schema in the PHAK Chapter 4 evidence is:

**Humidity, along with pressure and temperature, affects air density; air density in turn affects aircraft performance; density altitude is a practical correlate of that density, and higher density altitude corresponds to lower air density and reduced performance.**  
Also, **density altitude is pressure altitude corrected for nonstandard temperature**. Pressure altitude is part of the computation of density altitude.

In schema form:

**Pressure altitude + temperature (and humidity as a contributing factor via density) → air density / density altitude → aircraft performance**

Key relationships supported by the evidence:
- **Humidity affects density** and is a contributing factor in density altitude/performance calculations [chunk 06_phak_ch4_0-structure_aware-p04-c03 p.4; KG triple 06_phak_ch4_0-structure_aware-p04-c03-kg00-3d55cb1ee1].
- **Pressure, temperature, and humidity influence aircraft performance because of their effect upon density** [chunk 06_phak_ch4_0-structure_aware-p04-c03 p.4; KG triples 06_phak_ch4_0-structure_aware-p04-c03-kg02-5bc39328d7, kg03-ff8b142e2f, kg04-3722b6cd1a].
- **Density altitude is pressure altitude corrected for nonstandard temperature** [chunk 06_phak_ch4_0-structure_aware-p03-c04 p.3; chunk 06_phak_ch4_0-structure_aware-p03-c05 p.3].
- **As air density decreases (higher density altitude), aircraft performance decreases; as air density increases (lower density altitude), performance increases** [chunk 06_phak_ch4_0-structure_aware-p03-c04 p.3; KG triple 06_phak_ch4_0-structure_aware-p03-c04-kg03-b3bc48b215].
- **Density altitude is used in calculating aircraft performance** [chunk 06_phak_ch4_0-structure_aware-p03-c05 p.3; KG triple 06_phak_ch4_0-structure_aware-p03-c05-kg01-4f32705e99].

Citations: chunks 06_phak_ch4_0-structure_aware-p03-c04 p.3, 06_phak_ch4_0-structure_aware-p03-c05 p.3, 06_phak_ch4_0-structure_aware-p04-c03 p.4; KG triples 06_phak_ch4_0-structure_aware-p03-c04-kg03-b3bc48b215, 06_phak_ch4_0-structure_aware-p04-c03-kg00-3d55cb1ee1, 06_phak_ch4_0-structure_aware-p04-c03-kg02-5bc39328d7, 06_phak_ch4_0-structure_aware-p04-c03-kg03-ff8b142e2f, 06_phak_ch4_0-structure_aware-p04-c03-kg04-3722b6cd1a, 06_phak_ch4_0-structure_aware-p03-c05-kg01-4f32705e99.

### 06-phak-ch4-0-p05-986bfc7e8f

- Question: How should Newton's laws be represented as force and motion relations for aircraft?
- Source page: 5
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Newton’s laws should be represented as the basic force-and-motion relations governing aircraft flight:

- **First law:** an aircraft remains at rest or in uniform straight-line motion unless acted on by an outside force; forces can start, stop, or change its direction or speed.  
- **Second law:** for a constant mass, **force = mass × acceleration**; acceleration is directly proportional to applied force and inversely proportional to mass.  
- **Third law:** for every action there is an equal and opposite reaction; e.g., propeller or jet engine action on air produces an opposite reaction that moves the airplane forward.  

This framing is grounded in the chapter’s discussion of “the fundamental physical laws governing the forces acting upon an aircraft in flight” and “Newton’s basic laws of motion.” [chunk_id=06_phak_ch4_0-structure_aware-p00-c02 page=0; chunk_id=06_phak_ch4_0-structure_aware-p04-c11 page=4; chunk_id=06_phak_ch4_0-structure_aware-p04-c12 page=4; chunk_id=06_phak_ch4_0-structure_aware-p05-c43 page=5; KG triple_id=06_phak_ch4_0-structure_aware-p04-c11-kg00-45483e222a; KG triple_id=06_phak_ch4_0-structure_aware-p04-c12-kg00-c9bac8bd38; KG triple_id=06_phak_ch4_0-structure_aware-p05-c44-kg01-63f0c56092]

Citations: [chunk_id=06_phak_ch4_0-structure_aware-p00-c02 page=0], [chunk_id=06_phak_ch4_0-structure_aware-p04-c11 page=4], [chunk_id=06_phak_ch4_0-structure_aware-p04-c12 page=4], [chunk_id=06_phak_ch4_0-structure_aware-p05-c43 page=5], [KG triple_id=06_phak_ch4_0-structure_aware-p04-c11-kg00-45483e222a], [KG triple_id=06_phak_ch4_0-structure_aware-p04-c12-kg00-c9bac8bd38], [KG triple_id=06_phak_ch4_0-structure_aware-p05-c44-kg01-63f0c56092]

### 06-phak-ch4-0-p05-bb9a93ef72

- Question: What relation captures Bernoulli and venturi pressure decrease as air velocity increases?
- Source page: 5
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The relation is **decreases**: as air velocity increases, **pressure decreases** in Bernoulli’s Principle and in a venturi tube. This is supported by the page 5 evidence stating that “as the velocity of a moving fluid increases, the pressure within the fluid decreases” and that in the venturi constriction, “when the air speeds up, the pressure also decreases” ([chunk_id=06_phak_ch4_0-structure_aware-p05-c45, page 5], [chunk_id=06_phak_ch4_0-structure_aware-p05-c43, page 5]). The KG also supports Bernoulli’s Principle as causing “air pressure decreases in a venturi tube” ([triple_id=06_phak_ch4_0-structure_aware-p05-c43-kg00-d7a16bc022]).

Citations: [chunk_id=06_phak_ch4_0-structure_aware-p05-c45, page 5], [chunk_id=06_phak_ch4_0-structure_aware-p05-c43, page 5], [triple_id=06_phak_ch4_0-structure_aware-p05-c43-kg00-d7a16bc022]

### 06-phak-ch4-0-p06-a653e00686

- Question: What partonomy should represent airfoil structure and section geometry?
- Source page: 6
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: A grounded partonomy from the provided PHAK Chapter 4 evidence should represent an **airfoil** as having these components:

- **airfoil surface**: upper and lower surfaces of the airfoil  
- **leading edge**  
- **trailing edge**

The evidence also supports treating the **chord line** as a reference line **applied to** the airfoil, not as a part of the airfoil structure itself. The **mean camber line** is shown in the figures, but the retrieved text does not provide enough explicit grounded evidence to assert it as a part of the partonomy.

If you need a strict partonomy, the current PHAK Chapter 4 materials support:
**Airfoil → {airfoil surface, leading edge, trailing edge}**.

Citations: chunk 06_phak_ch4_0-structure_aware-p05-c48 p.5; chunk 06_phak_ch4_0-structure_aware-p05-c49 p.5; KG triples 06_phak_ch4_0-structure_aware-p05-c48-kg00-e6f8bc1000, 06_phak_ch4_0-structure_aware-p05-c48-kg01-c2d45fd4f6, 06_phak_ch4_0-structure_aware-p05-c48-kg02-a87aa93e4f, 06_phak_ch4_0-structure_aware-p05-c49-kg00-eab0721eca, 06_phak_ch4_0-structure_aware-p05-c49-kg01-bdaad57a7f, 06_phak_ch4_0-structure_aware-p05-c49-kg02-8e3723e3ee.

### 06-phak-ch4-0-p07-9737986760

- Question: How should lift be modeled as an aerodynamic force produced by pressure differences and flow turning?
- Source page: 7
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Lift should be modeled as an aerodynamic force generated by **both pressure differences and flow turning**:

- **Pressure difference:** As air flows over a wing, regions of **lower-than-atmospheric pressure** on the upper surface and **higher pressure** on the lower surface create a net force on the wing; this pressure distribution produces lift. The wing’s motion through air generates lift, and pressure is described as a force acting perpendicular to a surface. [chunk_id=06_phak_ch4_0-structure_aware-p07-c23 page=7; chunk_id=06_phak_ch4_0-structure_aware-p02-c103 page=2; chunk_id=06_phak_ch4_0-structure_aware-p04-c09 page=4]

- **Flow turning / deflection:** An airfoil inclined to the airstream deflects the airflow, causing the air to turn about the object. This change in flow direction is associated with a measurable force on the airfoil and is described as part of lift generation. [chunk_id=06_phak_ch4_0-structure_aware-p08-c02 page=8; chunk_id=06_phak_ch4_0-structure_aware-p07-c20 page=7]

The current PHAK Chapter 4 materials support describing lift as arising from **pressure distribution plus Newtonian flow deflection/turning**, but they do not provide a single unified mathematical model in the retrieved evidence.

Citations: chunk_ids/pages above; KG triple ids used: 06_phak_ch4_0-structure_aware-p04-c09-kg02-813c55c60f, 06_phak_ch4_0-structure_aware-p02-c105-kg01-95989858d4, 06_phak_ch4_0-structure_aware-p07-c19-kg01-9844b11d81, 06_phak_ch4_0-structure_aware-p07-c20-kg00-49247f068d

### 06-phak-ch4-0-p07-59d55c9639

- Question: What schema links angle of attack to airfoil pressure distribution and center of pressure movement?
- Source page: 7
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The current PHAK Chapter 4 materials support this schema:

- **Angle of attack (AOA)** changes the **pressure distribution** along the airfoil.
- The **center of pressure (CP)** is the average of that pressure variation for a given AOA.
- As AOA increases, the **CP moves forward**; as AOA decreases, the **CP moves aft**.

This is directly stated in the evidence on page 7: “as air flows along the surface of a wing at different angles of attack (AOA)... The average of the pressure variation for any given AOA is referred to as the center of pressure (CP)... At high angles of attack, the CP moves forward, while at low angles of attack the CP moves aft.” [chunk_id=06_phak_ch4_0-structure_aware-p07-c23 page=7]

The figure caption also links **pressure distribution on an airfoil and CP changes with AOA**. [chunk_id=06_phak_ch4_0-structure_aware-p07-c19 page=7; triple_id=06_phak_ch4_0-structure_aware-p07-c19-kg00-e0ca3cf11d]

Citations: [chunk_id=06_phak_ch4_0-structure_aware-p07-c23 page=7], [chunk_id=06_phak_ch4_0-structure_aware-p07-c19 page=7; triple_id=06_phak_ch4_0-structure_aware-p07-c19-kg00-e0ca3cf11d]

### 06-phak-ch4-0-p08-84dd3b3d9f

- Question: How should wingtip vortex formation and winglet mitigation be modeled?
- Source page: 8
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: False
- Citation complete: True
- Hybrid answer: Model wingtip vortex formation as a **third-dimensional pressure equalization around the wingtip**: high-pressure air beneath the airfoil flows around the tip toward the low-pressure area above, creating a **rotating tip vortex** and a **downwash** behind the wing that reduces lift in the affected portion of the airfoil. Winglet mitigation should be modeled as a **physical barrier that reduces or prevents this tip flow/vortex formation**; the material says winglets “act as a dam preventing the vortex from forming,” and tapering the tip is another mitigation by reducing pressure differential and smoothing airflow around the tip. [chunk_id=06_phak_ch4_0-structure_aware-p08-c04 p.8]

Citations: [chunk_id=06_phak_ch4_0-structure_aware-p08-c04 p.8; KG triple: 06_phak_ch4_0-structure_aware-p08-c04-kg01-5aec0888c9]
