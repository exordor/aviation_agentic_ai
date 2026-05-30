# Aerodynamic Center

- Document ID: `nasa_bga_aerodynamic_center`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aerodynamic-center/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 27, 2023
- Content hash: `f64f8208ec651c5f42798855ec959f379ddb09d9e04bc37b5a9f809bc42c9945`

## Cleaned Content

On this page:

Image of the aerodynamic center of an angle of attack

Velocity

As an object moves through a fluid, the velocity of the fluid varies around the surface of the object. The variation of velocity produces a variation of pressure on the surface of the object. Integrating the pressure times the surface area around the body determines the aerodynamic force on the object. We can consider this force to act through the average location of the pressure on the surface of the object. We call the average location of the pressure variation the center of pressure in the same way that we call the average location of the weight of an object the center of gravity. In general, the pressure distribution around the object also imparts a torque, or moment, on the object. If a flying airfoil is not controlled in some way it will tumble as it moves through the air.

Aerodynamic Force

If we consider an airfoil at angle of attack, we can (theoretically) determine the pressure variation around the airfoil, and calculate the aerodynamic force and the center of pressure. But if we change the angle of attack, the pressure distribution changes and therefore the aerodynamic force and the location of the center of pressure and the moment all change. So determining the aerodynamic behavior of an airfoil is very complicated if we use the center of pressure to analyze the forces. We can compute the moment about any point on the airfoil if we know the pressure distribution. The aerodynamic force will be the same, but the value of the moment depends on the point where that force is applied. It has been found both experimentally and theoretically that, if the aerodynamic force is applied at a location 1/4 chord back from the leading edge on most low speed airfoils, the magnitude of the aerodynamic moment remains nearly constant with angle of attack. Engineers call the location where the aerodynamic moment remains constant the aerodynamic center (ac) of the airfoil. Using the aerodynamic center as the location where the aerodynamic force is applied eliminates the problem of the movement of the center of pressure with angle of attack in aerodynamic analysis. (For supersonic airfoils, the aerodynamic center is nearer the 1/2 chord location.)

Airfoil

For symmetric airfoils, the aerodynamic moment about the ac is zero for all angles of attack. With camber, the moment is non-zero and constant for thin airfoils. For a positive cambered airfoil, the moment is negative and results in a counterclockwise rotation of the airfoil. With camber, an angle of attack can be determined for which the airfoil produces no lift, but the moment is still present. For rectangular wings, the wing ac is the same as the airfoil ac. But for wings with some other planform (triangular, trapezoidal, compound, etc.) we have to find a mean aerodynamic center (mac) which is the average for the whole wing. The computation of the mac depends on the shape of the planform.
