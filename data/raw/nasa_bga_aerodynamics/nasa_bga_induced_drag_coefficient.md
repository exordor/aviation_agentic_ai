# Induced Drag Coefficient

- Document ID: `nasa_bga_induced_drag_coefficient`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 27, 2023
- Content hash: `2f501178d61a2584e4cfcee4f6e96d8f450cd9467335c7c6132ad431b9b57097`

## Cleaned Content

On this page:

Image of an airplane

Aerodynamic Drag

There are many factors which influence the amount of aerodynamic drag which a body generates. Drag depends on the shape, size, and inclination, of the object, and on flow conditions of the air passing the object. For a three-dimensional wing, there is an additional component of drag, called induced drag , which will be discussed on this page.

Air Pressure of a Wing

For a lifting wing, the air pressure on the top of the wing is lower than the pressure below the wing. Near the tips of the wing, the air is free to move from the region of high pressure into the region of low pressure. The resulting flow is shown on the figure by the two circular blue-grey arrows with the arrowheads showing the flow direction. As the aircraft moves to the lower left, a pair of counter-rotating vortices are formed at the wing tips. The line of the center of the vortices are shown as blue vortex lines leading from the wing tips.

If the atmosphere has very high humidity, you can sometimes see the vortex lines on an airliner during landing as long thin “contrails” leaving the wing tips. The wing tip vortices produce a swirling flow of air behind the wing which is very strong near the wing tips and decreases toward the wing root. The effective angle of attack of the wing is decreased by the induced flow of the vortices and varies from wing tip to wing root. The induced flow produces an additional, downstream-facing, component of aerodynamic force of the wing. This additional force is called induced drag because it faces downstream and has been “induced” by the action of the tip vortices. It is also called “drag due to lift” because it only occurs on finite, lifting wings and the magnitude of the drag depends on the lift of the wing.

Drag Coefficient

The derivation of the equation for the induced drag is fairly tedious and relies on some theoretical ideas which are beyond the scope of the Beginner’s Guide. The induced drag coefficient Cdi is equal to the square of the lift coefficient Cl divided by the quantity: pi (3.14159) times the aspect ratio AR times an efficiency factor e .

Cdi = (Cl^2) / (pi * AR * e)

The aspect ratio is the square of the span s divided by the wing area A .

AR = s^2 / A

For a rectangular wing this reduces to the ratio of the span to the chord c .

AR (rectangle) = s / c

Considering the induced drag equation, there are several ways to reduce the induced drag. Wings with high aspect ratio have lower induced drag than wings with low aspect ratio for the same wing area. So, wings with a long span and a short chord have lower induced drag than wings with a short span and a long chord.

Lifting Line Theory

Lifting line theory shows that the optimum (lowest) induced drag occurs for an elliptic distribution of lift from tip to tip. The efficiency factor e is equal to 1.0 for an elliptic distribution and is some value less than 1.0 for any other lift distribution. So, an elliptical wing planform has the lowest amount of induced drag and all other wing shapes have higher induced drag than an elliptical wing. For a rectangular wing, the efficiency factor is equal to .7.

Winglets

For many years, wing designers have attempted to reduce the induced drag component by special shaping of the wing tips. The Wright Brothers used curved trailing edges on their rectangular wings based on wind tunnel results. The outstanding aerodynamic performance of the British Spitfire of World War II is partially attributable to its elliptic shaped wing which gave the aircraft a very low amount of induced drag. On modern airliners, the wing tips are often bent up to form winglets. Winglets were extensively studied by Richard Whitcomb of the NASA Langley Research Center in an effort to reduce the induced drag on airliners.

For a wing, the total drag coefficient, Cd is equal to the base drag coefficient at zero lift Cdo plus the induced drag coefficient Cdi .

Cd = Cdo + Cdi

The drag coefficient in this equation uses the wing area for the reference area. Otherwise, we could not add it to the square of the lift coefficient, which is also based on the wing area.
