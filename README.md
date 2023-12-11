# Python-Platformer with Tiled Map Editor

To run, install the following libraries:
- Pygame
- PyTmx

# To Create Levels install the Tiled map editor
- https://www.mapeditor.org/download.html
    - download is actually from itch.io

## Level Editor Layers
The following layers are needed:
- Blocks
    - These blocks are the blocks the player will interact with as barriers. The player will be able to collide with them from any direction.
- Background
    - This layer is the background. The player will ignore these blocks
- Level_Properties
    - add the following custom attributes
    - <b>LevelStartX</b> = x coordinate of where the player should spawn
    - <b>LevelStartY</b> = y coordinate of where the player should spawn
    - <b>LevelBlockSizeHeight</b> = number of pixel high each block is
    - <b>LevelBlockSizeWidth</b> = number of pixels wide each block is
    - <b>LevelEndX = x coordinate of where the player should get to end the level
    - <b>LevelEndY</b> = y coordinate of where the player should get to end the level

## Enemies
This game now supports enemies that move and obey gravity and a feature to allow the enemie to ignore gravity and fly horizontally. From within Tiled, edit a tileset and add an animation. Then open the tile properties and add the following custom properties for the tile:

[
    {
        "name": "availableFrames",
        "propertytype": "",
        "type": "string",
        "value": "idle,hit,move"
    },
    {
        "name": "gravityOff",
        "propertytype": "",
        "type": "bool",
        "value": true
    },
    {
        "name": "hitFrameCount",
        "propertytype": "",
        "type": "string",
        "value": "2"
    },
    {
        "name": "hitFrameRate",
        "propertytype": "",
        "type": "string",
        "value": "3"
    },
    {
        "name": "hitFrameStart",
        "propertytype": "",
        "type": "string",
        "value": "5"
    },
    {
        "name": "idleFrameCount",
        "propertytype": "",
        "type": "string",
        "value": "-1"
    },
    {
        "name": "idleFrameRate",
        "propertytype": "",
        "type": "string",
        "value": "-1"
    },
    {
        "name": "idleFrameStart",
        "propertytype": "",
        "type": "string",
        "value": "-1"
    },
    {
        "name": "moveFrameCount",
        "propertytype": "",
        "type": "string",
        "value": "4"
    },
    {
        "name": "moveFrameRate",
        "propertytype": "",
        "type": "string",
        "value": "5"
    },
    {
        "name": "moveFrameStart",
        "propertytype": "",
        "type": "string",
        "value": "1"
    },
    {
        "name": "velocityX",
        "propertytype": "",
        "type": "string",
        "value": "2"
    }
]

    ## Adding an Enemy to a level
    All enemies are objects. Add the tile from a tileset as a object that has an animation.

    

    # Controller Support
    This game has basic controller support. Also to note, the controller needs to connected and turned on prior the game starting. If the controller is found and has a rumble feature, the controller will rumble when it initialized in the game. Again, the controller needs to be connected before the game loop starts.
    
    ## moving
    When operating on Ubuntu, the D-pad will work, otherwise I have found only the first joystick works for moving.

    When jumping, the first button will make the player jump. With an xbox one controller this happens to be the 'A' button.

    # Keyboard Controls
    Spacebar jumps, left/right arrow keys move accordingly.