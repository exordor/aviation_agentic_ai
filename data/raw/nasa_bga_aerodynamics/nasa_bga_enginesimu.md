# Engine Parameter Interactive

- Document ID: `nasa_bga_enginesimu`
- Source URL: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/enginesimu/
- Source type: `nasa_web_educational_page`
- Authority: NASA Glenn Research Center
- Advisory risk level: `learning`
- Page last updated: July 17, 2024
- Content hash: `11ce8dfe6e6bbabb8ca15875180e296f87fb2c47dd68f42978ca91eb5668c3d0`

## Cleaned Content

On this page:

With this simulator, you can investigate how a turbine (or jet) engine produces thrust by changing the values of different engine parameters.

Please note : the simulation below is best viewed on a desktop computer. It may take a few minutes for the simulation to load.

General Instructions

This program is designed to be interactive. There are several different types of widgets that you use to work with the program.

There are a variety of choices that you must make regarding the analysis and the display of results by using a choice box . A choice box has a descriptive word displayed and an arrow at the right of the box. To make a choice, click on either the arrow or the current choice word, hold down, and drag to make your selection. The new selection is indicated by a change in the word. A recent security patch has changed the way that choice boxes operate. This can result in a condition where you can’t change from Imperial to Metric units. To overcome this problem, we have included an Override option on the choice boxes on the control panel. If you get stuck, click on Override then click on your choice; it will then work correctly.

The current values of the design variables are presented to you in text boxes . By convention, a white box with black numbers is an input box and you can change the value of the number. A black box with yellow or red numbers is an output box and the value has been computed by the program. To change the value in an input box, select the box by moving the cursor into the box and clicking the mouse, then backspace over the old number, enter a new number, then hit the Enter key on your keyboard. You must hit Enter to send the new value to the program.

For most input variables you can also use a slider located next to the input box. Click on the slider bar, hold down and drag the slider bar to change values, or you can click on the arrows at either end of the slider. If you experience difficulties when using the sliders to change variables, simply click away from the slider and then back to it. If the arrows on the end of the sliders disappear, click in the areas where the left and right arrow images should appear, and they should reappear.

Some graphics decisions are selected by pushing buttons . To push a button, move the cursor over the button and click the mouse.

Screen

The program screen is divided into four main parts:

On the top left side of the screen is a graphic of the engine you are designing or testing. In the Design Mode, the drawing is a schematic, while in Tunnel Test Mode the drawing is an animation.

On the upper right side of the screen are choice buttons that control the analysis. You can select the type of analysis, the type of output to be displayed, and the units to be used in the calculations. You will always see the overall engine performance displayed as thrust, fuel flow, airflow, and computed engine weight.

On the lower right side of the screen are the results of engine performance calculations. The output can be presented as numerical values of certain parameters, graphs of engine performance, or photos of the engine parts with descriptions of their purpose. You select the type of output displayed by using the red choice button labeled “Output:” on the upper right panel.

On the lower left side of the screen, various input panels are displayed. You can select the input panel by clicking on the name or the component in the graphic at the upper left. Limits are established for the variables in the program. If you click on “Limits” on the schematic, you will invoke a special input panel that allows you to reset those limits. You must push the blue “Submit” button to send your changes to the program .

Engine Design Process

You can choose from four different types of engines: a simple turbojet , a jet with an afterburner, a turbofan engine, or a ramjet . Selections are made on the graphics window by clicking on the engine name. The chosen engine is shown in yellow. Depending on the engine type, different input panels appear at the lower left.

The design process begins by selecting the design Flight Conditions. The Flight input panel lets you change the Mach number, airspeed, altitude, pressure, temperature, and throttle and afterburner settings. There are several different combinations of these variables available for input using the choice button on the input panel. The pressure and temperature are computed as functions of the altitude by using a Standard Day atmospheric model.

Design variables for each engine component can also be varied. The variables include the Inlet (pressure recovery), Fan (pressure ratio, efficiency, and bypass ratio), Compressor (CPR, compressor efficiency), Burner (fuel, maximum temperature, efficiency, pressure ratio), Turbine (turbine efficiency), and Nozzle (maximum temperature, efficiency, A8/A2). As you choose a different component the part of the engine being affected is highlighted in the graphic by changing from its default color to yellow. And a new input panel will appear at the lower left. If you change the Output Display to Photos you can view an actual photograph and description of each engine part.

Engine Size can be specified by either the frontal area or the diameter. As the engine size changes, the grid background changes in proportion to the size. The distance between any two grid lines is 1 foot.

Materials Input

The program will calculate the average weight of the engine that you design. The thrust to weight ratio of the engine is displayed in the numerical output and is a measure of the efficiency of the engine. The weight depends on the number of stages in the compressor and turbine, the diameter (frontal area) of the engine, and the component materials. The program begins with standard materials for the components, but you can change the materials and see the effects on the weight of the engine. Just push the blue Materials choice button on any component input panel. You can also select to define your material by choosing My Material from the menu. Just type in your values for material density and temperature limit.

The program will check the temperature throughout the engine design against the material limits. If you exceed a limit, a flashing warning will occur in the schematic. You can see the temperature limits by choosing Graphs in the Output display of the control panel. Then select Temperature as the type of graphics display. (For the afterburner and the ramjet, the graphical temperature limits are based on the flow temperature, not on the material temperature, and are slightly higher than the material limits. Cooling airflow is often used along the walls of these components to keep the material temperature within limits.)

Control Panel Choices: Mode, Units, Output Display

The program works in two modes: Design or Tunnel Test Mode. In the Design Mode, you can change design variables including the flight conditions, the engine size, the inlet performance , the turbomachinery compressor and turbine performance, the combustors or burner performance, or the nozzle performance. For a turbofan engine design, you can also vary the fan performance and the bypass ratio. In Design Mode, any change in an input parameter produces a new engine design. You have to be very careful when concluding the effects of input variables on performance because you are not comparing the effects on the same engine.

In Tunnel Test Mode you can vary only the flight conditions and you cannot change any of the component design parameters except the throttle setting. The values of some of the parameters like inlet recovery and nozzle area may change according to choices that you made during design. In Tunnel Test Mode you are evaluating the off-design performance of the engine model which you specified in Design Mode. In Tunnel Test mode, you can load models of existing turbine engines for comparison with your design. You can always reload your design to continue testing. In Design Mode, you can use the existing engine models as good starting points for your design.

The calculations can be performed in either Metric or Imperial (English) units. You can always return to the default conditions by pushing the red Reset button on the control panel.

Graphical Output

The red Output display menu on the upper right control panel allows you to change the contents of the output window on the lower right side of the screen. You can choose to display output boxes with numerical values of the engine performance, as described below. Or you can display photographs and descriptions of each engine part. You can display the variation of the value of pressure and temperature at various stations through the engine. Or you can also display a T-s Plot or a P-v Plot, which are used by engineers to determine engine performance.

To generate your performance plots, select “Generate” from the graphics window. The input panel will now display some additional buttons and sliders to generate a plot. Choose the variables to be plotted using the pulldown menus and then push the “Begin” data button. Set the value of the independent variable by using the slider or the type-in box. Push the blue “Take Data” button and a data point will appear on the graph. Set a new value for the variable and take another data point (up to 25 points in any order). When you are finished, push the “End” button and a line will be drawn through your data points. To start a new graph, push “Begin” and your old graph will vanish. When you are finished, push the red “Exit” button and you will return to free stream conditions.

Numerical Output

Numerical Output from the program is displayed on two panels. The total engine performance is always displayed on the control panel at the upper right and includes the engine net thrust , the fuel flow rate , the engine airflow rate, the engine weight, the thrust to weight ratio, and the specific fuel consumption .

Two additional performance panels are displayed at the lower right. The Engine Performance output panel shows the fuel-to-air ratio , the engine pressure ratio (EPR) and engine temperature ratio (ETR) , gross thrust, and ram drag. Additional component performance parameters, such as the nozzle pressure ratio (NPR), compressor pressure ratio (CPR), engine thermal efficiency, nozzle exit velocity (V exit), free stream dynamic pressure (q0), and specific impulse (ISP) are displayed. Nozzle exit pressure (Pexit) and fan nozzle exit pressure (P fan exit) and the compressor face Mach number (M2) are also displayed. The Component Performance output panel shows the variation of total pressure and temperature at various stages through the engine.

New Features

The NASA Glenn Educational Programs Office will continue to improve and update EngineSim based on user input. Changes from previous versions of the program include:

On 19 Aug 14 version 1.8a was released. This version has been updated to overcome some problems caused by recent Java security patches. There are no longer any photos of engine components and no animation displayed during Tunnel Test mode. The basic analysis has remained the same from Version 1.7c, only the photos have been removed.

On 5 Dec 13 version 1.7c was released. This version has been updated to overcome some problems in the use of choice boxes caused by recent Java security patches.

On 18 Oct 12 version 1.7b was released. This version has been updated to include the compressor pressure ratio on the output panel. This will help users to see the difference between Design Mode and Tunnel Test Mode.

On 26 Oct 05 version 1.7a was released. This version has been re-sized to fit the NASA portal. Some additional output variables have been added and a correction to the gross thrust calculation was made. The logic for moving the engine graphic was also changed.

On 20 Feb 04 version 1.6e was released. This version has a cleaner look by moving the units into the output boxes. Engine thermal efficiency is now output instead of compressor Mach number.

On 11 Dec 03 version 1.6d was released. This version has separate input panels for the ramjet burner and nozzle and allows the user to specify the ramjet fuel.

On 25 Nov 03 version 1.6c was released. This version lets the user move the engine graphic. The user can also specify any fuel by giving the fuel heating value. A bug related to the nozzle total temperature has been fixed.

On 17 Oct 03 version 1.6b was released. This version has a slightly modified graphics window for resizing the application. Tabs are also added to the printed output of the application.

On 15 Sep 03 version 1.6a was released. This version includes the component output panel, additional input, and output variables, and some new input options for the flight conditions. This is the first version that is available as a Java application. The application permits the user to save results between sessions and is run off-line. There are minor changes to the layout of the program and bugs in the weight calculations that are corrected.

On 6 Jun 03 version 1.5h was released. This version corrects a bug in the loading of existing engine models. Materials information is now included in the upload.

On 29 Apr 03 version 1.5g was released. This version corrects a bug in the ramjet temperature calculations.

On 18 Mar 03 version 1.5f was released. This version includes a correction to the weight calculation when you change the compressor face area.

On 17 Sep 01 a special version for undergraduates was released. This version includes the ability to reset most of the limits in the program.

On 22 Aug 01 version 1.5b was released. This version includes more corrections to the ramjet analysis and some slight changes to the variable limits. A “sleek” version of the program is now available for experienced users.

On 19 Apr 01 version 1.5 was released. This version includes improved graphics and a more consistent input environment. There are also corrections to the ramjet analysis from previous versions.

On 13 Oct 00 version 1.4 was released. This version includes material properties for each component and a calculation of the engine weight. Temperature limits for each component are also checked.

On 26 Sept 00 version 1.3 was released. This version uses the “card format” for input and output. Component input panels are invoked from the engine graphic. Optional photos of the components are included on the output panel.

On 31 Mar 00 version 1.2 was released. This version includes a ramjet simulation.

On 2 Dec 99 version 1.1 was released. This version includes a variety of plots and optional animation displays. This applet enables the student to interactively observe the effects of engine component performance on thrust and fuel consumption.

Activities

Introductory Exercise

Set the following conditions in EngineSim:

Design Mode English Units Turbojet Flight Conditions

The Airspeed should be 0, the Altitude 0, and the Throttle 100. Record the thrust (F net) ___________and the Fuel Flow __________. Now go ahead and change the altitude to 10,000 ft. and the Airspeed to 350. Did the thrust increase or decrease? Did the fuel flow increase or decrease? Thrust ________ Fuel Flow__. What happens when you choose a different engine? Choose a jet with afterburner and record the thrust ___________ and the fuel flow ____________. Choose a turbofan engine and record the thrust _____________ and the fuel flow________. What can you conclude about the effect of an increase in altitude and airspeed on thrust? __________________________________ On fuel flow?__________________________ Which engine is most fuel efficient? _______________________________

The original source code for the simulations is available for users to download at the BGA Simulations on GitHub .
