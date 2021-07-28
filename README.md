# Chess Piece Vision
A Scratch program to display chessboards based on the moves of pieces.

Run in the browser at https://turbowarp.org/551121474?fps=60&hqpen&offscreen

# How to use
## Physics Mode
The default mode, start the program without holding any keys to use it. The squares in the board are instead circular nodes that repel from each other with the inverse-square law but are pulled towards those a move away. Click and drag to move them about. Press space to alternate between seeing dark and light ones accordiing to the original pattern and seeing a colour wheel (each square's colour representing its direction from the origin and brightness its distance). Move the mouse pointer to the top of the screen to change board size (width and height), see energy (the total force from repulsion and Hooke's law at the current frame) and change the piece modelled.

## Mobility Mode (not currently working)
Start while holding 'm' to use. Calculates the average number of moves to reach each square from the current one, does for all squares, maps to brightness (fewer = brighter, fewest = white).

## Moves from Origin Mode
Start while holding 'n' to use. Finds the minimum number of squares the modelled piece takes to reach each cell from the origin. Begins by finding all those one move from the origin, then all those one move away from those which have been reached but not calculated. Cells are set to a second uncalculated state if a shorter route to them is found than the first one, at which they don't add to the moves list when calculated (because they'd be duplicates). I plan to add an index for the calculated list so a piece's precomputed moves can be found more efficiently. 

## Piece list
0. Knight
1. Rook
2. Bishop
3. King
4. Nightrider (knight that can move arbitrarily far in a direction per move, like a queen but knight moves instead of king ones)
5. Rose (nightrider that switches forwards or backwards through the eight possible knight moves, meaning it can move from its origin to one of 7 other positions in 8 octagons instead of to one of 8 spaces)
