# WokeLib

An opionated collection of decorators and functions I use for fuzz testing smart contracts with Woke. 

## 

## Generating data

I modelled this setup after hypothesis such that the generation of all random values is done outside of the flows and sequences in the woke fuzz class.  The reason I prefer this style relates to reproducability.  With this style, all inputs parameters to the flows can be recorded. 

```solidity

```

## Collecting data

All parameters for each flow can be recorded by attaching the `
