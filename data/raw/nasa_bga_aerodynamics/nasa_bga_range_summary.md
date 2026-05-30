# Range Summary

- Document ID: `nasa_bga_range_summary`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/range-summary/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 7, 2025
- Content hash: `7cb4af8af2f0181b9c434b228a63edbd283e1a4eb2f341d0ba1c1624cf478b8f`

## Cleaned Content

On this page:

Image of an airplane with formulas

Cruise Conditions of an Aircraft’s Range

Let’s summarize the information necessary to do a preliminary calculation of an aircraft’s range under cruise conditions. We are taking a very simple view of aircraft range – for academic purposes. In reality, calculating the range is a complex problem because of the large number of variables. An aircraft’s flight is not conducted at a single ground speed but varies from zero at take-off, to cruise conditions, and back to zero at landing. Extra fuel is expended in climbing to altitude and in maneuvering the aircraft. The weight is constantly changing as fuel is burned, so the lift, drag, and thrust and fuel consumption rate are also continually changing. On real aircraft, just like with your automobile, there is usually a fuel reserve, and the pilot makes sure to land the plane with fuel still on board. We are going to neglect all of these effects.

Wind Tunnel Testing of an Aircraft

There are certain things that we need to know about our aircraft. From previous wind tunnel testing, we need to determine the L/D ratio \(\frac{C_l}{C_d}\) and the lift coefficient C l . We also need some information about the propulsion system, specifically, the specific fuel consumption rate TSFC of the engine. For the aircraft itself, we need to know the weight W of the aircraft, the wing area, A and the fuel load M . We are free to select a flight altitude, but this determines the air density ρ from our model of the standard atmosphere.

Lift Equation

In cruise, the lift L is equal to the weight W and the thrust F is equal to the drag D . Using the lift equation, we can solve for the velocity necessary to create enough lift to equal the weight.

Velocity

In this equation, all of the variables are known except the velocity V , so we solve this equation for V.

L/D Ratio

Using the L/D ratio, we can solve for the drag of the aircraft which is equal to the thrust.

Maximum Flight Time

The thrust, specific fuel consumption, and fuel load determine the maximum flight time available to the aircraft.

\(\LARGE t _{max} =\frac{M}{TSFC * F}\)

\(\LARGE t_{max}=\frac{M \frac{C_l}{C_d}}{TSFC * W}\)

This flight time multiplied by the aircraft velocity determines the range (R).

Range

\(\LARGE R=V*t _{max}\)

\(\LARGE R = \sqrt{ \frac{W}{ \left( \frac{1}{2} C_l \rho A \cdot M\frac{C_l}{C_d} \cdot \text{TSFC} \cdot W \right) } }\)

Try our Range Games interactive JavaScript simulation which demonstrates these concepts. This simulation presents problems which you must solve by using the range equation.
