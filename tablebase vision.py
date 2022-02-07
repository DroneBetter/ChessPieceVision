import math, pygame, random
from pygame.locals import *
clock=pygame.time.Clock()

boardWidth=3
boardSquares=boardWidth**2
board=[]*boardSquares
pieceNames=["empty","king","queen","rook","bishop","knight","pawn"]

def findPieceMoves(piece,position): #outputs list of squares to which piece can travel
    if piece==0:
        return []
    else:
        moves=[]
        horizontalMoves=[]
        if piece==1:
            if position%boardWidth!=0: #not on leftmost file
                horizontalMoves.append(position-1)
            if position%boardWidth!=boardWidth-1:
                horizontalMoves.append(position+1)
            moves=list(horizontalMoves)
            horizontalMoves.insert(1,position) #allow orthogonal vertical moves
            if position>=boardWidth: #not on bottom row
                moves+=[i-boardWidth for i in horizontalMoves]
            if position<boardSquares-boardWidth: #not on top row
                moves+=[i+boardWidth for i in horizontalMoves]
            return moves
        elif piece==2:
            return findPieceMoves(3,position)+findPieceMoves(4,position)

statesWithoutTurns=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateSquareAttacks=[] #list of whether each square is attacked and (if so) by whom
for i in range(boardSquares):
    iKingMoves=findPieceMoves(1,i) #the new Apple product
    for j in range(boardSquares):
        if not (i==j or j in iKingMoves):
            statesWithoutTurns.append([[(1 if k==i or k==j else 0),(1 if k==j else 0)] for k in range(boardSquares)]) #each square in each state list (in the list of them) is a list of the piece and its colour
            attackedSquares=[]
            for k in range(len(statesWithoutTurns[-1])): #cannot be list comprehension because it references the list as it constructs it (I am greatly saddened)
                for l in findPieceMoves(statesWithoutTurns[-1][k][0],k):
                    if [l,statesWithoutTurns[-1][k][1]] not in attackedSquares:
                        attackedSquares.append([l,statesWithoutTurns[-1][k][1]]) #will have to be made more complicated if pawns added
                #print(attackedSquares)
            #[0,0] is empty, [1,0] is white, [1,1] is black (I will eventually find how to make lists of bits to speed it up (like bitboards))
            stateSquareAttacks.append([[int([k,l] in attackedSquares) for l in range(2)] for k in range(boardSquares)]) #[0,0] is empty, [1,0] white, [0,1] black, [1,1] both
#print(len(statesWithoutTurns),"states without turns:",statesWithoutTurns)
states=[[j,i] for j in range(2) for i in statesWithoutTurns] #each state is formatted [colour to move,[[[square piece],[square colour]],[[square piece],[square colour]], ...]]
#print(len(states),"states:",states)
stateSquareAttacks=[i for j in range(2) for i in stateSquareAttacks] #state formatted [[attacked by white?,attacked by black?] for square in range(boardSquares)] #get a load of the comments' opening square brackets' kerning
#print(len(stateSquareAttacks),"state square attacks:",stateSquareAttacks)
stateMoves=[[[j if states[s][1][i][0]!=1 or stateSquareAttacks[s][j][1-states[s][0]]==0 else None for j in findPieceMoves(states[s][1][i][0],i)] if (states[s][1][i][1]==states[s][0]) else [] for i in range(boardSquares)] for s in range(len(states))] #is list of lists of destination squares for each piece #the i list comprehension if statement would have (s[1][i][0]!=0 and ) but is now superseded by findPieceMoves
#print(len(stateMoves),"state moves:",stateMoves)

stateTransitions=[]
for s in range(len(states)):
    stateTransitions.append([]) #doing stateTransitions=[[]]*len(states) seems to make it copy into every element of stateTransitions
    for i in range(len(stateMoves[s])): #squares
        for j in range(len(stateMoves[s][i])): #moves per square
            if stateMoves[s][i][j]!=None:
                stateTransitions[s].append(states.index([(1-states[s][0]),[[0,0] if k==i else (states[s][1][i] if k==stateMoves[s][i][j] else states[s][1][k]) for k in range(len(states[s][1]))]]))
print("state transitions:",stateTransitions)

pygame.init()
size=[1280,800]
black=(0,0,0)
squareColours=((174,137,104),(236,217,185)) #I am using lichess's colours (I am a criminal wanted throughout NATO)
screen = pygame.display.set_mode((size[0], size[1]))
camera=[i/2 for i in size]
rad=size[0]/len(states)
#bitColours=[[int(255*(math.cos((j/n-i/3)*2*math.pi)+1)/2) for i in range(3)] for j in range(n)]
squares=[]
for s in range(len(states)):
    squares.append([[[s*rad,0],[size[1]/2,random.random()/2**8]],[rad*2]*2,1, squareColours[states[s][0]]])
dims=2
FPS=60
drag=0.1
gravitationalConstant=-100
hookeStrength=0.001
def physics():
    for i in range(len(squares)):
        if drag>0:
            absVel=max(1,math.sqrt(sum([squares[i][0][di][1]**2 for di in range(dims)]))) #each dimension's deceleration from drag is its magnitude as a component of the unit vector of velocity times absolute velocity squared, is actual component times absolute velocity.
            for di in range(dims):
                squares[i][0][di][1]*=1-absVel*drag #air resistance
        for di in range(dims):
            squares[i][0][di][0]+=squares[i][0][di][1]
    for i in range(len(squares)-1):
        for i2 in range(i+1,len(squares)):
            differences=[squares[i2][0][di][0]-squares[i][0][di][0] for di in range(dims)]
            dist=max(1,math.sqrt(sum([di**2 for di in differences])**3))
            gravity=gravitationalConstant/dist
            for di in range(dims):
                squares[i][0][di][1]+=differences[di]*(hookeStrength*(i2 in stateTransitions[i])+gravity*squares[i2][2])
                squares[i2][0][di][1]-=differences[di]*(hookeStrength*(i in stateTransitions[i2])+gravity*squares[i][2])
def drawShape(size,pos,colour,shape):
    color=(colour[0],colour[1],colour[2])
    if shape==0:
        surf = pygame.Surface(size)
        surf.fill(color)
        rect = surf.get_rect()
        screen.blit(surf, pos)
    else:
        pygame.draw.circle(screen, color, [pos[di]-camera[di] for di in range(dims)], size[0]/2)
def drawLine(initial,destination,colour):
    pygame.draw.line(screen,colour,[initial[di]-camera[di] for di in range(dims)],[destination[di]-camera[di] for di in range(dims)])

run=True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    physics()
    screen.fill(black)
    camera=[sum([i[0][di][0] for i in squares])/len(squares)-size[di]/2 for di in range(dims)]
    for i in range(len(stateTransitions)):
        for j in range(len(stateTransitions[i])):
            drawLine([squares[i][0][di][0] for di in range(dims)],[squares[stateTransitions[i][j]][0][di][0] for di in range(dims)],(255,)*3)
    for i in range(len(squares)):
        drawShape(squares[i][1],[squares[i][0][di][0] for di in range(dims)],squares[i][3],1)
    pygame.display.flip()
    clock.tick(FPS)
else:
    exit()
