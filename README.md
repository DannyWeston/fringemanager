# Fringe Pattern Manager


### Introduction

Simple Python program for generating fringes on the fly and projecting them on a display-based projector. These projectors must appear as a regular "display" in Windows, i.e: they are connected by a video cable such as HDMI or VGA. 

Note that this program doesn't do any fancy stuff with interrupt signalling/syncing - you can simply choose a display to project fringes on and... project them.


### Requirements

- Windows (shouldn't take too much effort to port to UNIX-based systems)
- Python 3.11.7 


### Dependencies 
See requirements.txt

It could run on other versions of dependencies but this has only tested with specified versions in requirements.txt

- numpy
- Pillow
- pywin32 
