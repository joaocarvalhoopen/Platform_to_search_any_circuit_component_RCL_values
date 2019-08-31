# Platform to search any circuit component RCL values and tolerance analysis.

## Description:
This is a simple program that is made to be customizable, in other words, to be modified to your own specific case. It will help you in automating the search for the optimal values of resistors, capacitors and inductors in any circuit that you have a mathematical description of it. You should also have a clear measure of how to evaluate the error distance regarding what you consider to be the best result.<br>                                            
It can also do tolerance analysis.<br>
You can customize the program in five simple steps, that are documented in code.<br>

## The inputs are
* dict_input_fixed_parameters ex:{VCC, VEE, GND}
* dict_resistors ex:{R1 [100, 100000, 1%], R2 [1000, 10000, 5%]}
* dict_capacitors ex:{C1 [1e-6, 4.7e-6, 10e-6, 10%], C2 [],}
* dict_inductors ex:{L1 [1e-3, 5e-3, 10e-3, 10%], L2 [],}
* dict_target_calc_values ex:{V_low_threshold, V_high_threshold}
  
# How it works
It works by making the full search of all combinations of values of components, to identify the ones that produce the smallest error. In this way it speeds up immensely the manual experimentation while dimensioning.<br>
The resistors are from the E24 scale and the tolerance can be chosen from 5%, 1%, 0.1% or 0.01%. The capacitors are from E12 scale. Or you can choose specific values or sets of values for each component.<br>
Don't forget that there is a combinatorial explosion in the total number of values that can be evaluated, but even with this simple version I hope that it could be useful. Other approaches to this problem of searching for an optimal configuration of passive components exists, and maybe in the future I will implement a version based on Genetic Algorithms to expand the current work to more simultaneous components.<br>   
Before you start, please always do a schematic diagram to better understand the program you need to write. <br>
Note: The program comes with an example of implementation that I used while developing and that will help to take any dought on how to customize it. The example implements in this new platform the some circuit that is calculated and documented in the project [Design Asymmetrical Inverted Schmitt-Trigger Single Supply program](https://github.com/joaocarvalhoopen/Design_Asymmetrical_Inverted_Schmitt_Trigger_Single_Supply_program) .<br>
<br>

![Program output 1](./text_output_part1.png?raw=true "Program output 1")

![Program output 2](./text_output_part2.png?raw=true "Program output 2")

## License
MIT open source license

## Have fun!
Best regards,<br>
Joao Nuno Carvalho<br>