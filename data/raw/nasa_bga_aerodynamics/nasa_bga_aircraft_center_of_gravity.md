# Aircraft Center of Gravity

- Document ID: `nasa_bga_aircraft_center_of_gravity`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aircraft-center-of-gravity/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 15, 2024
- Content hash: `61c984fa6df5c0c1d7d71b6d315b920c18e874001ca2e178c4fd69b66b335ef0`

## Cleaned Content

On this page:

Image of an airplane

Aerodynamic Control Surfaces

An airplane in flight can be maneuvered by the pilot using the aerodynamic control surfaces; the elevator, rudder, or ailerons. As the control surfaces change the amount of force that each surface generates, the aircraft rotates about a point called the center of gravity. The center of gravity is the average location of the weight of the aircraft. The weight is actually distributed throughout the airplane, and for some problems it is important to know the distribution. But for total aircraft maneuvering, we need to be concerned with only the total weight and the location of the center of gravity.

How do engineers determine the location of the center of gravity for an airplane which they are designing?

Newton’s Weight Equation

An airplane is a combination of many parts; the wings, engines, fuselage, and tail, plus the payload and the fuel. Each part has a weight associated with it which the engineer can estimate, or calculate, using Newton’s weight equation:

\(\LARGE w=m\cdot g\)

where w is the weight, m is the mass, and g is the gravitational constant which is 32.2 ft/square sec in English units and 9.8 meters/square sec in metric units. To determine the center of gravity cg , we choose a reference location, or reference line . The cg is determined relative to this reference location. The total weight of the aircraft is simply the sum of all the individual weights of the components. Since the center of gravity is an average location of the weight, we can say that the weight of the entire aircraft W times the location cg of the center of gravity is equal to the sum of the weight w of each component times the distance d of that component from the reference location:

\(\LARGE cg\cdot W={\left(w\cdot d\right)}_{fuselage}+{\left(w\cdot d\right)}_{wing}+{\left(w\cdot d\right)}_{engines}+…\)

The center of gravity is the mass-weighted average of the component locations.

Sigma

We can generalize the technique discussed above. If we had a total of “n” discrete components, the center of gravity cg of the aircraft times the weight W of the aircraft would be the sum of the individual i component weight times the distance d from the reference line (\(w\cdot d\)) with the index i going from 1 to n. Mathematicians use the Greek letter sigma (Σ) to denote this addition. (Sigma is a zig-zag symbol with the index designation being placed below the bottom bar, the total number of additions placed over the top bar, and the variable to be summed placed to the right of the sigma with each component designated by the index.)

\(\LARGE cg\cdot W=\sum_{i=1}^{i=n}{\left(w\cdot d\right)}_i\)

This equation says that the center of gravity times the sum of “n” parts’ weight is equal to the sum of “n” parts’ weight times their distance. The discrete equation works for “n” discrete parts.
