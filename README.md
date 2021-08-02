# Chess Piece Vision
A Scratch program to display chessboards based on the moves of pieces.

Run in the browser at https://turbowarp.org/551121474?hqpen&offscreen

# How to use
## Network Graph Mode
The default mode, start the program without holding any keys to use it. The squares in the board are instead circular nodes that repel from each other with the inverse-square law but are pulled towards those a move away. Click and drag to move them about. Press space to alternate between seeing dark and light ones accordiing to the original pattern and seeing a colour wheel (each square's colour representing its direction from the origin and brightness its distance). Move the mouse pointer to the top of the screen to change board size (width and height), see energy (the total force from repulsion and Hooke's law at the current frame) and change the piece modelled.

## Mobility Mode (not currently working)
Start while holding 'm' to use. Calculates the average number of moves to reach each square from the current one, does for all squares, maps to brightness (fewer = brighter, fewest = white).

## Moves from Origin Mode
Start while holding 'n' to use. Finds the minimum number of squares the modelled piece takes to reach each cell from the origin. Begins by finding all those one move from the origin, then all those one move away from those which have been reached but not calculated. Cells are set to a second uncalculated state if a shorter route to them is found than the first one, at which they don't add to the moves list when calculated (because they'd be duplicates). I plan to add an index for the calculated list so a piece's precomputed moves can be found more efficiently.

## Ben Finegold's queen-knight puzzle
Start while holding 'B' (for Ben). There's a queen that remains still on d5, you have a knight on h8 and want to reach every square in order, row-by-row, from right to left and up to down, while avoiding the queen and all squares it attacks. This mode displays it in network graph mode, you must intervene to pull it into the optimal state from the local minimum. [4K YouTube video of it (with further explanation in description)](https://youtu.be/fGOOcOnY7PY)

## Pieces implemented
0. Knight
1. Rook
2. Bishop
3. King
4. Pawn (one-way connections cause oscillators in network graph mode, which don't seem to stabilise over time at sizes above 6)
5. Nightrider (knight that can move arbitrarily far in a direction per move, like a queen but knight moves instead of king ones)
6. Rose (nightrider that switches forwards or backwards through the eight possible knight moves, meaning it can move from its origin to one of 7 other positions in 8 octagons instead of to one of 8 spaces)
7. Huygens (moves as rook but only looks at squares a prime-numbered distance away)
8. unnamed Fibonacci piece (Huygens but Fibonacci distances instead of prime)
9. unnamed atan(φ^x) piece I made (moves as Fibonacci but at each orthogonal step can either proceed as usual or switch to 'diagonal' moves, increasing the position in the Fibonacci list of the perpendicular component by the same amount as the parallel, named because for x orthogonal moves before switching to 'diagonal' the angle of each successive move's destination from the origin (or indeed the previous one, the discrete derivative is by definition two steps behind the current value) will converge towards the equation's output)
10. Queen

# TODO
Implement the 'Connection Node Beginnings Index' list, which will allow (in either the Mobility or Moves from Origin mode, which sometimes find shorter paths to squares that reduce not just their 'moves from origin' value but also that of all those a move away that have a greater such value) reading through the indexed part a list instead of recomputing the moves.
