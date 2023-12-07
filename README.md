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

    # Controller Support
    This game has basic controller support. When operating on Ubuntu, the D-pad will work, otherwise I have found only the first joystick works for moving.

    When jumping, the first button will make the player jump. With an xbox one controller this happens to be the 'A' button.

    # Keyboard Controls
    Spacebar jumps, left/right arrow keys move accordingly.