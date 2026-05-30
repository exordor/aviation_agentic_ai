# Dynamic Pressure

- Document ID: `nasa_bga_dynamic_pressure`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: June 28, 2024
- Content hash: `1754add4a3500d6c87c879b21248bb0353efa11bec091de01ae96c4738d0f836`

## Cleaned Content

On this page:

An important property of any gas is its pressure. Because understanding what pressure is and how it works is so fundamental to the understanding of aerodynamics and propulsion, we are including several slides on pressure in the Beginner’s Guide.

Pressure

There are two ways to look at pressure: (1) the small-scale action of individual air molecules or (2) the large-scale action of a large number of molecules. On the small scale, from the kinetic theory of gases , a gas is composed of a large number of molecules that are very small relative to the distance between molecules. The molecules of a gas are in constant, random motion and frequently collide with each other and with the walls of any container. During collisions with the walls, there is a change in velocity and therefore a change in the momentum of the molecules. The change in momentum produces a force on the walls which is related to the gas pressure. The pressure of a gas is a measure of the average linear momentum of the moving molecules of a gas.

On the large scale, the pressure of a gas is a state variable, like the temperature and the density. The change in pressure during any process is governed by the laws of thermodynamics. Although pressure itself is a scalar quantity, we can define a pressure force to be equal to the pressure (force/area) times the surface area in a direction perpendicular to the surface. If gas is static and not flowing, the measured pressure is the same in all directions. But if the gas is moving, the measured pressure depends on the direction of motion. This leads to the definition of dynamic pressure.

Derivation

To understand dynamic pressure, we begin with a one-dimensional version of the conservation of linear momentum for a fluid.

\(\LARGE \rho u \frac{du}{dx} = \frac{-dp}{dx}\)

where \(\rho\) is the density of the gas, p is the pressure, x is the direction of the flow, and u is the velocity in the x -direction. Performing a little algebra:

\(\LARGE \frac{dp}{dx} + \rho u \frac{du}{dx} = 0\)

For a constant density (incompressible flow) we can take the “\(\rho u\) ” term inside the differential:

\(\LARGE \frac{dp}{dx} + \frac{d(\frac{\rho u^2}{2})}{dx} = 0\)

and then gather all of the terms:

\(\LARGE \frac{d}{dx}(p + \frac{\rho u^2 }{2}) = 0\)

Integrating this differential equation:

\(\LARGE p_s + \frac{\rho u^2}{2} = constant = p_t\)

This equation looks exactly like the incompressible form of Bernoulli’s equation . Each term in this equation has the dimensions of a pressure (force/area); p s is the static pressure, the constant p t is called the total pressure, and is called the dynamic pressure because it is a pressure term associated with the velocity u of the flow.

\(\LARGE \frac{\rho u^2}{2}\)

Dynamic pressure is often assigned the letter q in aerodynamics:

Flow of Gas

The dynamic pressure is a defined property of a moving flow of gas. We have performed this simple derivation to determine the form of the dynamic pressure, but we can use and apply the idea of dynamic pressure in much more complex flows, like compressible flows or viscous flows. In particular, the aerodynamic forces acting on an object as it moves through the air are directly proportional to the dynamic pressure. The dynamic pressure is therefore used in the definition of the lift coefficient and the drag coefficient. As we have seen, dynamic pressure appears in Bernoulli’s equation even though that relationship was originally derived using energy conservation. By measuring the dynamic pressure in flight, a pitot-static tube (Prandtl tube) can be used to determine the airspeed of an aircraft.
