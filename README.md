# BlackBlox
BlackBlox is a calculator for "black box" systems, ranging from single unit processes to factories with branching chains of processes.


## Unit Processes
Unit processes are the smallest"block" in BlackBlox. Each unit process has a set of inflows and outflows and a set of specified relationships between the process flows. Then, given a quantity for one inflow or outflow, the quantities of the remaining inflows and outflows can be calculated. 

### Defining unit processes  
A unit process is defined by two tables:

#### Calculations Table 
The first specifies the relationships between inflows and outflows, with each row listing two substances; whether each substance is an inflow, an outflow, or a flow internal to the unit process; the type of calculation that would generate the quantity of the second substance if the quantity of the first substance is known, and the name of the variable (if any) used in that calculation.  

The calculation types must be those available in the program's calculator library. The substance variable names are user specified. It is also possible to define special substance names (e.g. "fuel") to allow the substance to be defined in the variables table (e.g. "fuel type") and also have properties defined elsewhere (e.g. HHV and combustion emissions)

#### Variables Table 
The second provides the values of the variables named in the calculations table. Separating the values into their own table allows for the same unit process to be run in different configurations(e.g. different efficiencies or fuel types). 

### Balancing unit processes  
Balancing a unit process calculates the quantity of all inflows and outflows of that unit process. To balance a unit process, the following arguments  must be provided: 
  * the quantity of one inflow or outflow
  * the name of that inflow or outflow substance
  * whether the substance is an inflow or outflow
  * the name of the configuration scenario to use from the variables table.
  
 All arguments besides the quantity can be optional, if default values have been specified for the unit process.


## Process Chain
A process chain is a linear collection of one or more connected unit processes, where an outflow of a preceding unit process is an inflow of the following unit process. 

### Defining a chain
A process chain is defined by a table with a list of unit processes with an inflow and outflow to each, where the outflow of a unit process must be the inflow into the next unit process. When the process chain is first used, an initializalion process creates each of the unit processes, if they do not already exist, and verifies that the inflows and outflows specified in the chain table exist for the corresponding unit processes. 

### Balancing a chain 
Balancing a chain calculates the quantity of all inflows and outflows of each unit process in the chain, either from first inflow to last outflow or from last outflow to first inflow. To balance a chain, the following arguments  must be provided: 
  * the quantity of one inflow or outflow to the chain
  * the name of that inflow or outflow substance
  * the name of the configuration scenario to use from the variables table.
  
 All arguments besides the quantity can be optional, if default values have been specified for the process chain.
 
 Balancing a chain returns both the calculated inflows and outflows for each unit process, as well as the the overall inflows and outflows to the chain.

### Generating a chain diagram 
After a chain has been defined, a process flow diagram of the chain can be generated.


## Factory (under development)
A factory is a collection of one or more connected process chains, where the inflow of outflow of any unit process within any chain can be the inflow or outflow of any other chain. A factory has a single main chain, and zero or more auxiliary chains. By specifying an input or output quantity to the main chain, it is possible to calculate the inflows and outflows of all processes within the chain.
 

## Current limitations:
  * The current available calculation types are:
    - Ratio calculaitons (known Qty * known ratio)
    - Remainder calculations (known Qty * (1-known ratio)
    - Molecular Mass Ratio calculations (known Qty * (mol mass of unknown / mol mass of known)
    - Combustion calculations (mass of fuel use, and emissions of CO2 and waste heat, based on specified fuel type, energy demand, and efficieincy)
   * Recycling flows are not supported. 
   * Chains can only balance if the specified flow is a substance name that is uniquely an input or uniquely an output of the chain.