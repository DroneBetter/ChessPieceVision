# Chess Piece Vision
A Scratch program to display chessboards and many other things as Eulerian graphs for topological manifolds.

Run in the browser at https://turbowarp.org/551121474?hqpen&offscreen

## Eulerian Graph modes (with physics)
### Standard
The default mode, start the program without holding any keys to use it. The squares in the board are circular nodes that repel from each other with the inverse-square law but are pulled towards those a move away with Hooke's law springs attempting to converge to 0 length. Click and drag to move them about. Press the space bar to alternate between the light and dark checkerboard and a colour wheel (each square's colour representing its original direction from the origin and brightness its distance, used to show origin positions of each node in eventual manifolds, like domain colouring). Move the mouse pointer to the top of the screen to change board size (width and height), see energy (the total force from repulsion and Hooke's law at the current frame) and change the piece modelled.

### Metaconnections
Press `L` on startup or during runtime to use. In this mode, there is no inverse-square law repulsion, but each pair of nodes is connected by a spring of length proportional to the number of moves between them. Creates much more symmetrical manifolds (including of pieces like the nightrider, which the standard mode only finds chaotic manifolds of), but runs slower (with time complexity `O(n^2*(n^2+1))=O(n^4+n^2)` of board width n), be warned.

By default, both the regular and metaconnections modes work in 3D. However, if you want to experiment in 2D like the original program, hold the 2 key on startup. Don't do this to increase performance, it will increase it by less than 50%, because most intensive calculations (like absolute distance cubed to divide nodes' differences in each axis by for gravitational force) aren't very much more intensive with additional dimensions, board size has a much greater bearing.

## Non-physics modes
### Mobility Mode (not currently working)
Start while holding `M` to use. Calculates the average number of moves to reach each square from the current one, does for all squares, maps reciprocally to brightness (fewer = brighter, fewest = white).

### Moves from Origin Mode
Start while holding `N` to use. Finds the minimum number of squares the modelled piece takes to reach each cell from the origin. Begins by finding all those one move from the origin, then all those one move away from those which have been reached but not calculated. Cells are set to a second uncalculated state if a shorter route to them is found than the first one, at which they don't add to the moves list when calculated (because they'd be duplicates). Can subtract pieces' minimum moves from each other also, representing positive with red and negative with cyan, but not in the UI, you must run the 'Find distance between' function inside the program.

## Special modes
### Ben Finegold's queen-knight puzzle
Start while holding `B` (for Ben). There's a queen that remains still on d5, you have a knight on h8 and want to reach every square in order, row-by-row, from right to left and up to down, while avoiding the queen and all squares it attacks. 10 squares are each only accessible from one 'parent', while the other 26 form four octagons and two quadrilaterals. This mode displays it in network graph mode, you must intervene to pull it into the optimal state from the local minimum.

[4K YouTube video of my simulation](https://youtu.be/fGOOcOnY7PY), [Ben Finegold's video on the puzzle](https://www.youtu.be/SrQlpY_eGYU) (someone told him about it in 1988, he told us about it), [website to play and time yourself](https://www.funnyhowtheknightmoves.com/) ([repo](https://github.com/jairtrejo/knight-moves))

Press `V` at any point to make it solve the problem with a bidirectional breadth-first search on the network (with red highlighting showing moves from origin and cyan for moves from destination for searched cells), or hold both 'B' and 'V' to do so on a chessboard of squares. [YouTube video with distance highlighting](https://youtu.be/PTLC1jobvU8)

### Minecraft mode
Hold `M` to begin. Minecraft mode has a board of the size determined by the slider, connected by king moves, but each 8\*8 region is connected to its own Nether node. Nether nodes are themselves connected to each other. Connections between cells don't correspond with widths of Minecraft blocks but with the distance such that travelling across them is as 'difficult' as moving to your current position in the Nether or back. This program represents Euclidean space's curvature in discrete graphs such that the most direct route corresponds as accurately as possible with the route through fewest edges. Excluding vertical motion (which isn't mapped, but world heights are negligible compared to width), Minecraft takes place in a 2-layer-high Nil manifold, meaning it's hyperbolic.

### Terraria mode
Hold `T` to begin, creates board of king moves also, but rectangular and corresponding with the game's world sizes (but scaled down). The king has items (configured in the Terraria function), like the magic mirror (which allows it to teleport to the origin from any location), these correspond with asymmetrical connections, the board corrugates, combinations of teleporting items create more complicated manifolds.

### Assembly Line mode
Hold `A` to begin, simulates the item crafting tree in the Android game Assembly Line (with bidirectional connections, to prevent the non-material ones from flying away infinitely far), minimum-energy states in 2 and 3 dimensions push the processed versions raw materials that aren't themselves materials in recipes to the outside, circuits seem to be furthest inside due to their 16 connections, batteries are further out than water heaters in 2D (because, despite batteries having 10 connections against 3, heater plates connect the otherwise disparate aluminium plates, diamond plates and heater plates).

### Quaternion mode
Hold `Q` to begin, it first creates (1,0,0,0), then finds its product with each positive quaternion basis vector (in the imaginary axes), connecting it to each and creating those that are missing, then it moves on to the next value in the list (positive i) that it created in the search from 1, it continues until it has iterated over each one generated, for all eight nodes and twenty-four connections, you can see how multiplication by each corresponds to motion through loops (to convey that it's a continuum, connections are direct paths through spherical space, not Cartesian). I would have made it a separate program because it isn't chess, but most other special modes aren't chess either, and I had already added quaternion multiplication functions for rotation in this program.

### Quotient space modes
In the modes with connections on rectangular boards (including the default chess mode), by default pieces stop moving at edges, but for non-iterative ones (ie. knight and king, not rook or bishop), you can make them scroll, causing the minimum-energy manifold to change dramatically. Hold `P` on startup for regular (cylindrical horizontal scrolling or `O` for inversive (Möbius strip). The same applies to vertically with `I` and `U` (on different columns because my keyboard doesn't recognise multiple being pressed simultaneously on the same column), and you can use `Y` to make the top side connect to the right and the bottom to the left instead (for the topological sphere). Most clearly on king moves, `P` and `I` make a torus, `P` and `U` make a Klein bottle, `O` and `U` make a real projective plane (that looks like the Roman surface immersion), `P`, `I` and `Y` make a topological sphere (more lemon-shaped, an artefact of the square board, with interesting manifolds at the ends, an artefact of the discrete simulation), `P`, `U` and `Y` make something similar but with directed connections that make it spin, and `O`, `U` and `Y` make a samosa-looking thing (frankly delicious). Toroidal scrolling on knight moves on a 4\*4 board has four connections per node (eight in total, but each can be reflected about its long axis to end up at the same destination) and sixteen nodes, and is rotationally symmetrical about each, so is an immersion of a tesseract in 3D.

## Chess pieces implemented
0. Knight
1. Rook
2. Bishop
3. King
4. Pawn (one-way connections cause oscillators in network graph mode)
5. Nightrider (knight that can move arbitrarily far in a direction per move, like a queen but knight moves instead of king ones)
6. Rose (nightrider that switches forwards or backwards through the eight possible knight moves, meaning it can move from its origin to one of 7 other positions in 8 octagons instead of to one of 8 spaces)
7. Huygens (moves as rook but only looks at squares a prime-numbered distance away)
8. Fibonacci rook (Huygens but Fibonacci distances instead of prime)
9. atan(φ^x) piece I made (moves as Fibonacci but at each orthogonal step can either proceed as usual or switch to 'diagonal' moves, increasing the position in the Fibonacci list of the perpendicular component by the same amount as the parallel, named because for x orthogonal moves before switching to 'diagonal' the angle of each successive move's destination from the origin (or indeed the previous one, the discrete derivative is by definition two steps behind the current value) will converge towards the equation's output)
10. Queen

## Credits
[@failedxyz](https://scratch.mit.edu/users/failedxyz) on Scratch for the only [implementation of the Sieve of Atkin](https://scratch.mit.edu/projects/17456670/) I found there, used to generate moves for the huygens (speed isn't very necessary because primes are computed prior).

[User:Cburnett](https://en.wikipedia.org/wiki/User:Cburnett) on Wikipedia for the [SVG chess pieces](https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces).

[Simon](https://stackoverflow.com/users/827753/simon) on StackOverflow for the [O(1) function for minimum knight move count between relative coordinates on an infinite plane](https://stackoverflow.com/a/41704071), used as the heuristic in the A\* search algorithm in Ben Finegold mode.

[@boraini](https://scratch.mit.edu/users/boraini) on Scratch for [the quaternion functions](https://turbowarp.org/454897467) used in this for 3D rotation (I originally used absolute yaw and pitch gimbals, but I had the problems with absolute yaw at high pitch corresponding with local roll, and unconstrained pitch inverting yaw controls, but with quaternions, mouse dragging now always corresponds with local yaw and pitch).

# Tablebase Vision
A Python program that is similar to the original/main purpose of CPV except generating tablebases (lists of all possible positions (permutations with turns) of a set of pieces with all possible moves they can make) and displaying them as a state transition diagram (like what Stephen Wolfram made for [elementary cellular automata](https://demonstrations.wolfram.com/CellularAutomatonStateTransitionDiagrams/)), currently only supporting kings.
## TODO
- Add move generation for iterative pieces (currently only kings and knights)
- Add node colouring based on whether it's checkmate (or part of a forced sequence to which)
- Add a mode with both playing and seeing the state transition diagram (showing your place in it)
- Perhaps add GUI for playing (the CLI is good but selecting and dragging pieces and seeing winningness highlighted on each destination would be better)
- Allow exporting of PGNs of sessions against the tablebase (or of checkmate sequences with maximum length)
- Add node mouse dragging (in planes parallel to the screen)
- Add topological manifold boards (Klein bottle and real projective plane and such)
- After topological manifold boards added, add option to account for their vertex-transitivity to reduce even further from eightfold symmetry
- Allow exporting tablebases to folder containing program (so they can be reimported instead of regenerated each time)

Done:
- Add 3D mode (for the embedding of the graph, not the board itself) with quaternion rotation
- Detect and regress from checkmated states (and stalemated ones (at a lower priority that checkmate overwrites)) to determine optimal moves in all states
- Add ability to play against tablebases (play chess with God)
- Add eightfold symmetry mode (becomes only twofold when there are pawns)
