# Aircraft Translations

- Document ID: `nasa_bga_aircraft_translations`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/aircraft-translations/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: August 25, 2025
- Content hash: `f1c47270c101dbf67df37b043137b0c179817f61fdc9d15b0d175c531aa7c108`

## Cleaned Content

On this page:

Image of airplanes with formulas

Object

We live in world that is defined by three spatial dimensions and one time dimension. Objects can move within this domain in two ways. An object can translate , or change location , from one point to another. And an object can rotate, or change its attitude . In general, the motion of an object involves both translation and rotation. The motion of an aircraft is particularly complex because the rotations and translations are coupled together; a rotation affects the magnitude and direction of the forces which affect translations.

Translation of an Aircraft

On this page we will consider only the translation of an aircraft within our domain. We can specify the location of our aircraft at any time t by specifying three coordinates x, y, and z on an orthogonal coordinate system. An orthogonal coordinate system has each of its coordinate directions perpendicular to all other coordinate directions. Initially, our aircraft is at point “0”, with coordinates x 0 , y 0 , and z 0 at time t 0 . In general, the aircraft moves through the domain until at some later time t1 the aircraft is at point “1” with coordinates x 1 , y 1 , and z 1 . We can specify the displacement – d in each coordinate direction by the difference in coordinate from point “0” to point “1”. The x-displacement equals \((x_1 – x_0)\), the y-displacement equals \((y_1 – y_0)\), and the z-displacement equals \((z_1 – z_0)\). For simplicity on the slide we are only going to consider the x coordinate.

Displacement

The total displacement is a vector quantity, which means that the displacement has a size and a direction associated with it. The direction is from point “0” to point “1”. The individual x-, y-, and z- displacements are the components of the displacement vector in the coordinate directions. All of the quantities derived from the displacement are also vector quantities.

Average Velocity

The velocity -V of the aircraft through the domain is the change of the location with respect to time. In the X – direction, the average velocity is the displacement divided by the time interval:

\(\LARGE V = \frac{x_1 – x_0}{t_1 – t_0}\)

This is an average velocity and the aircraft could speed up and slow down between points “0” and “1”. At any instant, the aircraft could have a velocity that is different than the average. If we shrink the time difference down to a very small (differential) size, we can define the instantaneous velocity to be the differential change in position divided by the differential change in time;

\(\LARGE V = \frac{dx}{dt}\)

where the symbol d / dt is the differential from calculus. So when we initially specified the location of our aircraft with x 0 , y 0 , z 0 , and t 0 coordinates, we could also specify an initial instantaneous velocity V 0 . Likewise at the final position x 1 , y 1 , z 1 , and t 1 , the velocity changes to a velocity V 1 . Again, for simplicity, we are considering only the x-component of the velocity. In reality, the aircraft velocity changes in all three directions. Velocity is a vector quantity and has both a magnitude and a direction.

Acceleration

The acceleration (a) of the aircraft through the domain is the change of the velocity with respect to time. In the X – direction, the average acceleration is the change in velocity divided by the time interval:

\(\LARGE a =\frac{V_1 – V_0}{t_1 – t_0}\)

As with the velocity, this is an average acceleration. At any instant, the aircraft could have an acceleration that is different than the average. If we shrink the time difference down to a very small (differential) size, we can define the instantaneous acceleration to be the differential change in velocity divided by the differential change in time:

Newton’s Second Law of Motion

From Newton’s second law of motion, we know that forces on an object produce accelerations. If we can determine the forces on an aircraft, and how the forces change with time, we can use the equations presented on this slide to determine the acceleration, velocity, and location of the aircraft as a function of time.
