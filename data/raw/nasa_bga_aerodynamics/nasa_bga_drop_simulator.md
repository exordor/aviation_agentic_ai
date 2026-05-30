# Drop Interactive Simulator

- Document ID: `nasa_bga_drop_simulator`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drop-simulator/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 17, 2024
- Content hash: `2bdd8bb71cb4ca0396790b702fafe8d630e187a204c1328ce82629f340041e08`

## Cleaned Content

On this page:

With this simulator you can investigate how an object falls through the air by changing the values of different design variables.

Please note : the simulation below is best viewed on a desktop computer. It may take a few minutes for the simulation to load.

Gravity and Aerodynamic Drag

DropSim considers the single problem of an object falling under the influence of gravity and aerodynamic drag. The user specifies a value for the weight and a value of the drag coefficient. An initial release point is given by the altitude and speed, and the code uses the standard atmosphere equations to determine a value of air density at the specified altitude. The density is used to determine the instantaneous drag on the object. The program uses the value of drag and weight to solve for the flight trajectory from Newton’s second law of motion.

General Instructions

This program is designed to be interactive, so you have to work with the program. There are several different types of input “widgets” which you use to send and receive information from the program and to change the analysis and display results:

Some of your selections are made by using a choice box . A choice box has a descriptive word displayed and an arrow at the right of the box. To make a choice, click on the arrow, hold down and drag to make your selection from the menu which is displayed.

Some selection are made by using the buttons on the panels. To activate a button move your cursor over the button and click your mouse. The different colored buttons have different effects:

Blue buttons are option buttons which you can select.

White buttons are processes which cause the program to begin calculating.

You can use the Red “Abort” button to stop the calculation at any time.

On the input panel, the current value of a design variable is presented to you in a text box . Different colored boxes have different meanings:

A white box with black numbers is an input box and you can change the value of the number. To change the value in an input box, select the box by moving the cursor into the box and clicking the mouse, then backspace over the old number, enter a new number, then hit the Enter key on your keyboard. You must hit Enter to send the new value to the program.

A black box with colored numbers is an output box and the value is computed by the program.

For most input variables you can also use a slider , located next to the input box, to change the input value. To operate the slider, click on the slider bar, hold down and drag the slider bar, or you can click on the arrows at either end of the slider. If you experience difficulties when using the sliders to change variables, simply click away from the slider and then back to it. If the arrows on the end of the sliders disappear, click in the areas where the left and right arrow Images should appear, and they should reappear.

Screen Layout

The program screen is divided into three main parts:

On the lower right of the screen are the control buttons and labels, and the calculated output values for the flight.

On the upper right of the screen are the input sliders and boxes that you use to change flight conditions. Details of the Input Variables are given below.

On the left of the screen is the graphics window in which you will see the results of the calculations. Details are given in Graphics.

Graphics

You move the graphic within the view window by moving your cursor into the window, hold down the left mouse button and drag to a new location. You can change the size of the graphic by moving the “Zoom” widget in the same way. If you loose your picture, or want to return to the default settings, click on the “Find” button at the bottom of the view window. The grid behind your design is toggled on or off by using the “Grid” button located above the Zoom widget.

Data is displayed as “strip charts” of weight, drag, speed, and height. The horizontal grid increments are 1 second on the strip charts. The vertical increments on the speed and drag graphs change with time to keep the plot within a fixed field. The shape of the graph is the chief output of the strip charts.

During the flight you have two viewing options. The default is to show the strip chart slowly develop from left to right with the passage of time. The other mode is the “Tracking” mode option which keeps the right side of the chart centered in the view window during the flight. Viewing options are toggled using the “Track” button located below the graphics window.

Input Variables

Input variables are located on the upper right side of the screen.

The dropped object is assumed to have no propulsion system. The object is given some initial velocity at a specified altitude and gravity eventually brings the object back to the surface of the earth. You must specify the weight, cross-sectional area, and drag coefficient (Cd) for the object. You can reset these values as described above. The launch speed and altitude must also be specified before launch. You can also specify the wind speed which will cause the object to drift during descent.

As the object falls, the pressure, temperature, and fluid density change as function of altitude. The drag depends on the density, so the drag also changes. Ideally, When the drag and weight are equal, the net external force on the object is zero and the object falls at a constant terminal velocity. In reality, the terminal velocity changes slightly as the object descends because of th echange in air density. You can perform the drop in three ways. t The actual mode will instantaneously calculate the changing value of air density, Or you can neglect the change in density and use a constant terminal velocity based on the density at the altitude at which the object was dropped. Or you can use the ground value of the density to determine the constant terminal velocity.

On the Flight panel at the lower right, you have a white button to “Drop” the object. As the countdown begins, the button turns yellow, then green during the flight, and finally red after touchdown. During the flight, the time and telemetry information changes. You can interrupt the flight by pushing the blue “Pause” button. You can then proceed a time step at a time by pushing the white “Step” button, or resume the flight by pushing “Resume”. When your flight is finished, you can “Reset” the same flight conditions and shoot again by using the blue button, or you can change flight conditions. At any time you can “Abort” the mission. At the bottom of the “Flight Control” panel, the current and maximum values of the height, speed, and range (distance from the drop point) are displayed. The current value of weight, drag, pressure, and temperature are also displayed.

Have fun!

The original source code for the simulations is available for users to download at the BGA Simulations on GitHub .
