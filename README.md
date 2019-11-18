---
# Cache MTR

This is a 'lightweight' simulator for evaluating the performance of simple caching algorithms. At the moment, this only consists of chosen user caching distributions relative to a known caching distribution. As inputs,

![equation](https://latex.codecogs.com/svg.latex?%5C%5Cp_r%28m%29%20-%20%5Cmathrm%7BProbability%5C%20of%5C%20requesting%5C%20file%5C%20index%5C%20%7Dm%5C%5C%20p_c%28m%29%20-%20%5Cmathrm%7BProbability%5C%20of%5C%20caching%5C%20file%5C%20index%5C%20%7Dm)

A simple example would be a tilted caching distribution with scaling factor ![equation](https://latex.codecogs.com/svg.latex?%5Calpha):

![equation](https://latex.codecogs.com/svg.latex?p_c%28m%29%20%3D%20%7B%7Bp_r%28m%29%5E%7B1%5Cover%5Calpha%7D%7D%5Cover%20%5Cover%7B%5Csum_%7Bn%3D1%7D%5E%7Bm%7D%7Bp_r%28n%29%5E%7B1%5Cover%5Calpha%7D%7D%7D%7D)


----
## Notes
* Notably, CacheMTR supports _LaTeX_ formula inputs with some nuance. See instructions for use and restrictions.
* Efficiency is in the works, most noticeable with simulations demanding >10,000 cache/request choices.
* Thank you to [QuickLatex](https://quicklatex.com/) for a simple and dependable API for generating UI renders of _LaTeX_, far simpler than making renders in-house with existing libraries.




----
## Usage
Running the visualizer - `visualize.py`

CLI Interfacing - `not yet available`

----
## Remarks/Changelog

* **1.0.0** – Initial commit
