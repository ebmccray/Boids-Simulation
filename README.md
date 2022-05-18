# About
This program is a simple simulation of animal flocking/schooling/herding behavior in a 2D environment, based on Craig Reynolds' "boid" model.

## Boid Movement
These are the basic principles of boid movement, according to Reynolds.
1. Boids fly towards the center of mass of neighboring boids
2. Boids keep a small distance away from other objects (including other boids)
3. Boids try to match the velocity (speed and direction) of nearby boids

# Features
## Fixed Bugs:
- v.4.1: Boids interpret an obstacle as a square, regardless of actual shape.
      
# Version Notes
### VERSION 4.3:
- First attempts at targeted boids
- Obstacles and collision tweaks
    
### VERSION 4.2:
- BUG FIX: Boids now interact with obstacles in the correct manner, most of the time.
- Fullscreen and escape exits
- Little tweaks
- Now an option for same-color flocks - boids will only flock with boids that have the same color.
    
### VERSION 4.1:
- User can create walls which block boid movement
- Unfortunately, currently, boids see the wall as a box regardless of its shape.
    
### VERSION 4.0:
- Boids now correctly avoid obstacles!
    
### VERSION 3.2:
- Adherence to Reynolds' 3 rules.
- Boids match speed velocity of nearby boids
- Boids turn back when they reach the edge of the screen
    
### VERSION 3.1:
- Boids successfully avoid each other.

### VERSION 3.0:
- Copied rotation and most basic set-ups from version 2.4
- Boids move towards the center of mass of local boids

# Goals and To-Do
## Features to Implement:
- GUI with sliders for population size, separation distance, etc etc
- Mover boids with specific targets
- Color options for boids

## Known Bugs:
- Boids sometimes fly through very narrow obstacles
- Boids get "caught" on edges of wall obstacles

Thank you.