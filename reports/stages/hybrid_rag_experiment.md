# Hybrid RAG Experiment

- Run ID: `hybrid-rag-20260519T005213Z`
- Questions: 10
- Chunks: `data/chunks/06_phak_ch4_0.jsonl`
- KG: `data/kg/06_phak_ch4_0.kg.jsonl`
- Chroma collection: `phak_ch4_chunks`
- Chunking strategy: `fixed_window`
- Rebuild chunks/index/KG: False / False / False

## Agent Boundary

This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Aggregate Metrics

### Retrieval

| Mode | Recall@5 | MRR@5 | Context Precision@5 |
| --- | ---: | ---: | ---: |
| vector | 1.0 | 0.7583 | 0.42 |
| graph | 0.8 | 0.65 | 0.49 |
| hybrid | 0.9 | 0.7533 | 0.4 |

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

- vs vector Recall@5: -0.1
- vs graph Recall@5: 0.1

## Question Results

### 06-phak-ch4-0-p00-fa9830b888

- Question: How should atmosphere, air, and constituent gases be modeled as a composition structure?
- Source page: 0
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Model it as a hierarchical composition:

- **Atmosphere** = an **envelope of air** surrounding Earth, so it contains **air** as a component.  
- **Air** = a **mixture of gases** / fluid, so it contains **constituent gases** as components.  
- **Constituent gases** = primarily **78% nitrogen**, **21% oxygen**, and **1% other gases** such as argon and helium.

A simple structure would be:

**Atmosphere → Air → Gases (nitrogen, oxygen, other gases)**

This is grounded by the retrieved materials, which state that the atmosphere is an envelope of air and that air is a mixture of gases, with the atmosphere composed of 78% nitrogen, 21% oxygen, and 1% other gases. [chunk_id=06_phak_ch4_0-fixed_window-p00-c00 page=0; chunk_id=06_phak_ch4_0-fixed_window-p01-c00 page=1]

**Citations:** chunk_id=06_phak_ch4_0-fixed_window-p00-c00 page=0 KG triple_id=06_phak_ch4_0-fixed_window-p00-c00-kg00-8748d82ca7; KG triple_id=06_phak_ch4_0-fixed_window-p00-c00-kg01-b36f7b1b3c; KG triple_id=06_phak_ch4_0-fixed_window-p00-c00-kg02-30f9108dc2; chunk_id=06_phak_ch4_0-fixed_window-p01-c00 page=1 KG triple_id=06_phak_ch4_0-fixed_window-p01-c00-kg00-898cdb205b

### 06-phak-ch4-0-p01-dbcda7dbf4

- Question: What classes and relations represent air as a fluid with viscosity, friction, and a boundary layer on a wing?
- Source page: 1
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The current PHAK Chapter 4 materials support modeling:

- **Air** as a **Fluid**: `Cl_Air -hasComponent-> Cl_Fluid` ([chunk p1 c00, triple 06_phak_ch4_0-fixed_window-p01-c00-kg00-898cdb205b]; also [chunk p1 c01, triple 06_phak_ch4_0-fixed_window-p01-c01-kg00-898cdb205b])
- **Viscosity** as a concept that **affects flow**: `Cl_Viscosity -affects-> Cl_Flow` ([chunk p1 c00, triple 06_phak_ch4_0-fixed_window-p01-c00-kg03-012eeeefb3])
- **Friction** as the mechanism by which the air adheres to the wing and forms the boundary layer, with the text stating: “Once the boundary layer of the air adheres to the wing by friction...” ([chunk p2 c00, triple 06_phak_ch4_0-fixed_window-p02-c00-kg02-77b9f87c3e])
- **Boundary layer** as the layer of air molecules near the wing surface: `boundary layer -hasComponent-> air molecules near the surface of the wing` ([chunk p1 c03, triple 06_phak_ch4_0-fixed_window-p01-c03-kg00-52eb682acd])

A grounded relation chain from the evidence is:
**Air (Fluid) → viscosity affects flow → friction causes adhesion to wing surface → boundary layer forms on the wing.**

Citations: [p1 c00 / 06_phak_ch4_0-fixed_window-p01-c00-kg00-898cdb205b], [p1 c00 / 06_phak_ch4_0-fixed_window-p01-c00-kg03-012eeeefb3], [p1 c03 / 06_phak_ch4_0-fixed_window-p01-c03-kg00-52eb682acd], [p2 c00 / 06_phak_ch4_0-fixed_window-p02-c00-kg02-77b9f87c3e].

### 06-phak-ch4-0-p02-dafae1ecbc

- Question: How should standard atmosphere values for pressure, temperature, and density be modeled?
- Source page: 2
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Model standard atmosphere as a reference atmosphere with fixed sea-level values and defined lapse rates:

- **Sea level standard values:** pressure **29.92 inHg (1,013.2 mb)** and temperature **59 °F / 15 °C**. [chunk_id=06_phak_ch4_0-fixed_window-p02-c02 page=2; chunk_id=06_phak_ch4_0-fixed_window-p02-c00 page=2; KG triple ids: 06_phak_ch4_0-fixed_window-p02-c02-kg05-4ed6928f68, 06_phak_ch4_0-fixed_window-p02-c02-kg06-54921c8ed3, 06_phak_ch4_0-fixed_window-p02-c00]
- **Temperature lapse rate:** decreases about **3.5 °F or 2 °C per 1,000 ft** up to **36,000 ft**, then remains constant to **80,000 ft**. [chunk_id=06_phak_ch4_0-fixed_window-p02-c02 page=2; chunk_id=06_phak_ch4_0-fixed_window-p02-c03 page=2]
- **Pressure lapse rate:** decreases about **1 inHg per 1,000 ft** up to **10,000 ft**. [chunk_id=06_phak_ch4_0-fixed_window-p02-c03 page=2]

Density is not given as a single fixed sea-level value in the retrieved text, but the materials state that **pressure and temperature affect density**, and density varies **directly with pressure** and **inversely with temperature**. [chunk_id=06_phak_ch4_0-fixed_window-p03-c02 page=3; chunk_id=06_phak_ch4_0-fixed_window-p04-c01 page=4; KG triple ids: 06_phak_ch4_0-fixed_window-p04-c01-kg05-2bf419b2a5, 06_phak_ch4_0-fixed_window-p04-c01-kg06-b55090d06e]

Citations: [chunk_id=06_phak_ch4_0-fixed_window-p02-c02 page=2], [chunk_id=06_phak_ch4_0-fixed_window-p02-c03 page=2], [chunk_id=06_phak_ch4_0-fixed_window-p02-c00 page=2], [chunk_id=06_phak_ch4_0-fixed_window-p03-c02 page=3], [chunk_id=06_phak_ch4_0-fixed_window-p04-c01 page=4].

### 06-phak-ch4-0-p03-f463ba25ee

- Question: What causal schema links pressure altitude, density altitude, humidity, air density, and aircraft performance?
- Source page: 3
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The causal schema in the retrieved PHAK Chapter 4 evidence is:

**Pressure altitude + nonstandard temperature → density altitude; and humidity/altitude/temperature affect air density; air density then drives aircraft performance.**

More specifically:
- **Density altitude** is defined as **pressure altitude corrected for nonstandard temperature** ([chunk_id=06_phak_ch4_0-fixed_window-p03-c02 page=3], [chunk_id=06_phak_ch4_0-fixed_window-p03-c01 page=3]).
- **Air density** is affected by **altitude, temperature, and humidity** ([chunk_id=06_phak_ch4_0-fixed_window-p03-c03 page=3], [chunk_id=06_phak_ch4_0-fixed_window-p04-c01 page=4]).
- As **air density decreases** (higher density altitude), **aircraft performance decreases**; as **air density increases**, performance increases ([chunk_id=06_phak_ch4_0-fixed_window-p03-c01 page=3], [chunk_id=06_phak_ch4_0-fixed_window-p03-c03 page=3]).
- The text also notes that **humidity** is a contributing factor and **high humidity** is one of the conditions associated with **high density altitude**, with an observed **decrease in overall performance** ([chunk_id=06_phak_ch4_0-fixed_window-p03-c03 page=3], [chunk_id=06_phak_ch4_0-fixed_window-p04-c02 page=4], [chunk_id=06_phak_ch4_0-fixed_window-p04-c01 page=4]).

Citations: chunk_id=06_phak_ch4_0-fixed_window-p03-c02 page=3; chunk_id=06_phak_ch4_0-fixed_window-p03-c01 page=3; chunk_id=06_phak_ch4_0-fixed_window-p03-c03 page=3; chunk_id=06_phak_ch4_0-fixed_window-p04-c01 page=4; chunk_id=06_phak_ch4_0-fixed_window-p04-c02 page=4; KG triple ids: 06_phak_ch4_0-fixed_window-p03-c01-kg00-851d22d42a, 06_phak_ch4_0-fixed_window-p03-c01-kg02-a140c7af03, 06_phak_ch4_0-fixed_window-p03-c03-kg00-cd15092b29, 06_phak_ch4_0-fixed_window-p03-c03-kg01-851d22d42a, 06_phak_ch4_0-fixed_window-p03-c03-kg02-db67ae14db, 06_phak_ch4_0-fixed_window-p03-c03-kg03-5f41309182, 06_phak_ch4_0-fixed_window-p03-c03-kg04-2bf419b2a5, 06_phak_ch4_0-fixed_window-p03-c03-kg05-3d55cb1ee1

### 06-phak-ch4-0-p05-986bfc7e8f

- Question: How should Newton's laws be represented as force and motion relations for aircraft?
- Source page: 5
- Gold level: page
- Retrieval Recall@5: False
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Newton’s laws can be represented for aircraft as force-and-motion relations like these:

- **First Law (inertia):** An aircraft **remains at rest or in uniform straight-line motion unless acted on by an external force**. In flight terms, forces can add to motion, slow it down, or change direction. [chunk_id=06_phak_ch4_0-fixed_window-p04-c04 page=4; KG triple_id=06_phak_ch4_0-fixed_window-p04-c04-kg03-bb6c8ab2da]
- **Second Law:** **Force equals mass times acceleration** for constant mass; more generally, force is the **change in momentum per unit time**. This means applied force produces acceleration, with greater mass requiring more force for the same acceleration. [chunk_id=06_phak_ch4_0-fixed_window-p04-c04 page=4]
- **Third Law:** **For every action, there is an equal and opposite reaction**. In aircraft, this is seen when the propeller or jet exhaust pushes air backward and the air pushes the aircraft forward. [chunk_id=06_phak_ch4_0-fixed_window-p05-c00 page=5]

If you want, I can also turn these into a simple “force, motion, reaction” table using only the chapter evidence.

Citations: [chunk_id=06_phak_ch4_0-fixed_window-p04-c04 page=4; KG triple_id=06_phak_ch4_0-fixed_window-p04-c04-kg03-bb6c8ab2da], [chunk_id=06_phak_ch4_0-fixed_window-p05-c00 page=5]

### 06-phak-ch4-0-p05-bb9a93ef72

- Question: What relation captures Bernoulli and venturi pressure decrease as air velocity increases?
- Source page: 5
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The relation is **inversely proportional**: as air velocity increases, pressure decreases under Bernoulli’s Principle. This is explicitly stated in the PHAK Chapter 4 evidence for moving fluid speed and pressure, including the venturi example. [chunk_id=06_phak_ch4_0-fixed_window-p05-c01 page=5] [chunk_id=06_phak_ch4_0-fixed_window-p05-c00 page=5] [chunk_id=06_phak_ch4_0-fixed_window-p05-c02 page=5]

Citations: chunk_id=06_phak_ch4_0-fixed_window-p05-c01 page=5; chunk_id=06_phak_ch4_0-fixed_window-p05-c00 page=5; chunk_id=06_phak_ch4_0-fixed_window-p05-c02 page=5; KG triple_id=06_phak_ch4_0-fixed_window-p05-c00-kg01-cd6545eea2

### 06-phak-ch4-0-p06-a653e00686

- Question: What partonomy should represent airfoil structure and section geometry?
- Source page: 6
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: A grounded partonomy for **airfoil structure and section geometry** should represent:

- **Wing → Airfoil** as the section/cross-section of the wing
- **Airfoil → Leading edge**
- **Airfoil → Trailing edge**
- **Airfoil → Chord line**
- **Airfoil → Airfoil surface** (upper and lower surfaces)
- Optionally, **Airfoil → Mean camber line** as a geometric reference line

This is supported by the evidence that a wing cross section is the airfoil, and that the typical airfoil section includes the leading edge, trailing edge, chord line, and upper/lower surfaces; the mean camber line is also described as a reference line in the section geometry. [chunk_id=06_phak_ch4_0-fixed_window-p05-c03 page=5; chunk_id=06_phak_ch4_0-fixed_window-p06-c00 page=6]

Citations: [06_phak_ch4_0-fixed_window-p05-c03 p.5 kg04-7543176b0f], [06_phak_ch4_0-fixed_window-p05-c03 p.5 kg00-c2d45fd4f6], [06_phak_ch4_0-fixed_window-p05-c03 p.5 kg01-a87aa93e4f], [06_phak_ch4_0-fixed_window-p05-c03 p.5 kg02-1560082613], [06_phak_ch4_0-fixed_window-p05-c03 p.5 kg03-e6f8bc1000], [06_phak_ch4_0-fixed_window-p06-c00 p.6], [06_phak_ch4_0-fixed_window-p06-c03 p.6 kg01-d374f2f475]

### 06-phak-ch4-0-p07-9737986760

- Question: How should lift be modeled as an aerodynamic force produced by pressure differences and flow turning?
- Source page: 7
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: Lift should be modeled as an aerodynamic force that results from both:

- **Pressure differences** across the airfoil: lower pressure on the upper surface and higher pressure on the lower surface create a net upward force. The text states that “the pressure differential between the upper and lower surface of the airfoil increases, total lift increases,” and that negative pressure on the upper surface creates a larger force than the positive pressure below [chunk_id=06_phak_ch4_0-fixed_window-p07-c01 page=7; triple_id=06_phak_ch4_0-fixed_window-p05-c01-kg01-618e279253].  
- **Flow turning / deflection**: the airfoil changes the direction of the airflow, and this turning of the flow is “partly (or fully) responsible for creating lift” [chunk_id=06_phak_ch4_0-fixed_window-p08-c00 page=8; triple_id=06_phak_ch4_0-fixed_window-p08-c00-kg02-09be8462ad].

So, a grounded model from the provided PHAK Chapter 4 materials is: **lift is the net aerodynamic force produced by pressure differences between the upper and lower surfaces, with flow turning/deflection contributing to that force generation** [page 4, page 7, page 8].

Citations: [chunk_id=06_phak_ch4_0-fixed_window-p07-c01 page=7; triple_id=06_phak_ch4_0-fixed_window-p05-c01-kg01-618e279253], [chunk_id=06_phak_ch4_0-fixed_window-p08-c00 page=8; triple_id=06_phak_ch4_0-fixed_window-p08-c00-kg02-09be8462ad]

### 06-phak-ch4-0-p07-59d55c9639

- Question: What schema links angle of attack to airfoil pressure distribution and center of pressure movement?
- Source page: 7
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: True
- Citation complete: True
- Hybrid answer: The schema in the Chapter 4 materials is:

**Angle of attack → pressure distribution along the airfoil → center of pressure (CP) movement.**

At different angles of attack, the wing has different pressure distributions, and the **average of the pressure variation** is the **center of pressure**. The CP moves **forward at high AOA** and **aft at low AOA**. This is explicitly stated in the retrieved evidence.  
- [chunk_id=06_phak_ch4_0-fixed_window-p07-c02 page=7]  
- [chunk_id=06_phak_ch4_0-fixed_window-p07-c00 page=7]  
- KG triples: `06_phak_ch4_0-fixed_window-p07-c02-kg00-865d5a01fd`, `06_phak_ch4_0-fixed_window-p07-c00-kg00-865d5a01fd`

Citations: chunk_id=06_phak_ch4_0-fixed_window-p07-c02 page=7; chunk_id=06_phak_ch4_0-fixed_window-p07-c00 page=7; KG triple ids `06_phak_ch4_0-fixed_window-p07-c02-kg00-865d5a01fd`, `06_phak_ch4_0-fixed_window-p07-c00-kg00-865d5a01fd`

### 06-phak-ch4-0-p08-84dd3b3d9f

- Question: How should wingtip vortex formation and winglet mitigation be modeled?
- Source page: 8
- Gold level: page
- Retrieval Recall@5: True
- KG evidence coverage: False
- Citation complete: True
- Hybrid answer: Model wingtip vortex formation as high-pressure air on the wing’s lower surface flowing around the wingtip toward the low-pressure upper surface, creating a rotating tip vortex and a trailing downwash that reduces lift on the affected portion of the wing. Model winglet mitigation as a tip device that acts like a dam to reduce or prevent vortex formation; the materials also note tapering the tip as another way to reduce the pressure differential and smooth airflow. [chunk_id=06_phak_ch4_0-fixed_window-p08-c01 page=8; chunk_id=06_phak_ch4_0-fixed_window-p06-c03 page=6]

Citations: chunk_id=06_phak_ch4_0-fixed_window-p08-c01 page=8; chunk_id=06_phak_ch4_0-fixed_window-p06-c03 page=6; KG triple_id=06_phak_ch4_0-fixed_window-p08-c01-kg05-ee7a4b62dd.
