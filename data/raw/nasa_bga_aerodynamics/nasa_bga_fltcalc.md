# Ballistic Flight Calculator

- Document ID: `nasa_bga_fltcalc`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/fltcalc/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 19, 2024
- Content hash: `768c86ee4c83e1e3bfb08852cd75bef6a0649586338ce62ee69921457d90716f`

## Cleaned Content

On this page:

Force

The study of model rockets, the flight of a baseball, or the “bend” of a soccer kick are excellent ways for students to learn the basics of forces and the response of an object to external forces. A ball in flight has no engine to produce continuous thrust and the resulting flight is similar to the flight of shell from a cannon, or a bullet from a gun. This type of flight is called ballistic flight. On this page, we present the equations that describe ballistic flight. Ballistic flight only occurs under the ideal conditions that weight is the only force acting on the object. There is no thrust and no aerodynamic drag acting on an object in ballistic flight. Such flight conditions would occur on the Moon, where there is no atmosphere to produce drag.

Aerodynamic Drag

On Earth, a baseball or a soccer ball generates a moderate amount of aerodynamic drag and the flight path is not strictly ballistic. Ballistic flight is, however, a first approximation to the flight of a ball. The actual flight equations including drag are much more complex because the drag is constantly changing throughout the flight. Drag depends on the square of the velocity and the velocity changes during the flight. The drag also depends on the air density which is a function of the weather conditions and altitude.

Vertical and Horizontal Angle

For ballistic flight, the ball is normally inclined at some angle to the vertical (or horizontal) as it is launched. We resolve the initial velocity into a vertical component V 0 and a horizontal component U 0 . The horizontal motion is uniform because there is no external force in the horizontal direction. So, according to Newton’s first law of motion, the horizontal velocity remains a constant and the distance x which the ball travels is given by the velocity times the expended time t :

\(\LARGE U=U_{0}\)

\(\LARGE x=U_{0}t\)

In the vertical plane, weight is the only external force acting on the object. Because the weight of the object is a constant, we can use the simple form of Newton’s second law to solve for the vertical motion:

\(\LARGE -W=F=ma=m\frac{\text{d}V}{\text{d}t}\)

where W is the weight, m is the mass, V is the vertical velocity, t is the time, a is the acceleration, and F is the net external force. The positive direction is upwards, so the weight is preceded by a negative sign. Solving the equation:

\(\LARGE \frac{\text{d}V}{\text{d}t}=\frac{-W}{m}=-g\)

\(\LARGE V=V_{0}-gt\)

where g is the gravitational acceleration which is equal to 32.2 ft/sec^2 or 9.8 m/sec^2 on the surface of the Earth. The value of the gravitational acceleration is different on the Moon and Mars. V 0 is the initial velocity leaving the launcher. The location at any time is found by integrating the velocity equation:

\(\LARGE \frac{\text{d}y}{\text{d}t}=V=V_{0}-gt\)

\(\LARGE y=V_{0}t-\frac{1}{2}gt^{2}\)

where y is the vertical coordinate. With this general description of the motion of a ballistic object, we can derive some interesting conclusions.

Notice that the flight equation includes no information about the object’s size, shape, or mass. All objects fly the same in purely ballistic flight. This is similar to Galileo’s principle that all objects fall at the same rate in a vacuum. If drag can be ignored, the flight of the object depends only on the initial velocity and the gravitational acceleration.

At the highest point in the flight, the vertical velocity is zero. From the velocity equation we can determine the time at which this happens:

\(\LARGE V=0\)

\(\LARGE t=\frac{V_{0}}{g}\)

The time to maximum altitude varies linearly with the launch velocity. Plugging this time into the altitude equation we obtain:

\(\LARGE y=V_{0}\frac{V_{0}}{g}-\frac{1}{2}g(\frac{V_{0}}{g})^{2}\)

\(\LARGE y=\frac{1}{2}\frac{V_{0}^{2}}{g}\)

The maximum altitude changes as the square of the launch velocity. Doubling the launch velocity produces four times the maximum altitude.

Below is a JavaScript calculator which will solve the equations presented on this page:

Please note : the simulation below is best viewed on a desktop computer. It may take a few minutes for the simulation to load.

General Instructions

To operate the calculator, you first select the planet using the choice button at the top left. For ballistic flight, select the “Ignore Drag” option with the middle choice button. On another page we develop the equations for flight with drag. You can perform the calculations in English (Imperial) or metric units. Enter the initial velocity, then press the red “Compute” button to compute the maximum height and the time to maximum height. Notice that entering a different value for the weight or the area does not change the computed maximum height.

Now consider the impact with the ground at the end of the flight. At impact the altitude is zero. Using the altitude equation:

\(\LARGE y=0\)

\(\LARGE V_{0}t=\frac{1}{2}gt^{2}\)

\(\LARGE t=\frac{2V_{0}}{g}\)

The total flight time varies linearly with the launch velocity. The total flight time is twice the time to reach maximum altitude. So, a ballistic shell takes as long coming down as it does going up. If we substitute this time into the velocity equation:

\(\LARGE V=V_{0}-g\frac{2V_{0}}{g}\)

\(\LARGE V=-V_{0}\)

The velocity at impact has the same magnitude but opposite direction as the velocity at launch.

The original source code for the simulations is available for users to download at the BGA Simulations on GitHub .
