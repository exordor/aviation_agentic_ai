# Reynolds Number Interactive Simulator

- Document ID: `nasa_bga_spcal`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/spcal/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 17, 2024
- Content hash: `0ce824be95a3b47b8a0052165f1a72f00192943582999ab8475044c54d504d29`

## Cleaned Content

On this page:

Image of Reynolds number formulas

Aerodynamic Forces

As an object moves through the atmosphere, the gas molecules of the atmosphere near the object are disturbed and move around the object. Aerodynamic forces are generated between the gas and the object. The magnitude of these forces depends on the shape of the object, the speed of the object, the mass of the gas going by the object, and on two other important properties of the gas, the viscosity , or stickiness, of the gas and the compressibility , or springiness, of the gas.

To properly model these effects, aerodynamicists use similarity parameters which are ratios of these effects to other forces present in the problem. If two experiments have the same values for the similarity parameters, then the relative importance of the forces are being correctly modeled. Representative values for the properties of air are given on another page, but the actual value of the parameter depends on the state of the gas and the altitude .

Boundary Layer

Aerodynamic forces depend in a complex way on the viscosity of the gas. As an object moves through a gas, the gas molecules stick to the surface. This creates a layer of gas near the surface, called a boundary layer, which, in effect, changes the shape of the object. The flow of gas reacts to the edge of the boundary layer as if it was the physical surface of the object. To make things more confusing, the boundary layer may separate from the body and create an effective shape much different from the physical shape. And to make it even more confusing, the flow conditions in and near the boundary layer are often unsteady (changing in time). The boundary layer is very important in determining the drag of an object. To determine and predict these conditions, aerodynamicists rely on wind tunnel testing and very sophisticated computer analysis.

Reynolds Number

The important similarity parameter for viscosity is the Reynolds number . The Reynolds number expresses the ratio of inertial (resistant to change or motion) forces to viscous (heavy and gluey) forces. From a detailed analysis of the momentum conservation equation , the inertial forces are characterized by the product of the density r times the velocity V times the gradient of the velocity dV/dx . The viscous forces are characterized by the dynamic viscosity coefficient mu times the second gradient of the velocity d^2V/dx^2 . The Reynolds number Re then becomes:

\(\LARGE \text{Re} = \frac{\rho \, V \, \frac{dV}{dx}}{\mu \, \frac{d^2V}{dx^2}} \)

The gradient of the velocity is proportional to the velocity divided by a length scale L . Similarly, the second derivative of the velocity is proportional to the velocity divided by the square of the length scale. Then:

\(\LARGE \text{Re} = \frac{\rho \, V \, \frac{V}{L}}{\mu \, \frac{V}{L^2}} \)

\(\LARGE \text{Re} = \frac{\rho \, V \, L}{\mu} \)

The Reynolds number is dimensionless. High values of the parameter (on the order of 10 million) indicate that viscous forces are small, and the flow is essentially inviscid. If the flow is inviscid, then the Euler equations can be used to model the flow. Low values of the parameter (on the order of 1 hundred) indicate that viscous forces must be considered.

The Reynolds number can be further simplified if we use the kinematic viscosity nu that is equal to the dynamic viscosity divided by the density:

\(\LARGE \nu = \frac{\mu}{\rho} \)

\(\LARGE \text{Re} = \frac{V \, L}{\nu} \)

For some problems, we can divide the Reynolds by the length scale to obtain the Reynolds number per foot Ref . This is given by:

\(\LARGE \text{Re}_f = \frac{V}{\nu} \)

The Reynolds number per foot (or per meter) is not a non-dimensional number like the Reynolds number. You can determine the Reynolds number per foot using the calculator by specifying the length scale to be 1 foot.

Below is a JavaScript application to calculate the coefficient of viscosity and the Reynolds number for different altitudes, lengths, and speeds.

Please note : the simulation below is best viewed on a desktop computer. It may take a few minutes for the simulation to load.

The Similarity Parameter Calculator was modified in May 2009, by Anthony Vila, a student at Vanderbilt University, during a summer intern session at NASA Glenn.

General Instructions

To change input values, click on the input box (black on white), backspace over the input value, type in your new value, and hit the Enter key on the keyboard (this sends your new value to the program). You will see the output boxes (yellow on black) change value. You can use either Imperial or Metric units and you can input either the Mach number or the speed by using the menu buttons. Just click on the menu button and click on your selection. The non-dimensional Mach number and Reynolds number are displayed in white on blue boxes.

The original source code for the simulations is available for users to download at the BGA Simulations on GitHub .
