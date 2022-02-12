import math, pygame, random
from pygame.locals import *
clock=pygame.time.Clock()

boardWidth=3
boardSquares=boardWidth**2
board=[]*boardSquares
pieceNames=["empty","king","queen","rook","bishop","knight","pawn"]
pieceSymbols=[[" ","k","q","r","b","n","p"],[" ","K","Q","R","B","N","P"]]

def precomputeKnightMoves():
    return
precomputedKnightMoves=precomputeKnightMoves()

def findPieceMoves(piece,position): #outputs list of squares to which piece can travel
    if piece==0:
        return [] #return exits the function
    if piece==2:
        return findPieceMoves(3,position)+findPieceMoves(4,position)
    if piece==3:
        exit()
    if piece==4:
        exit()
    xPosition=position%boardWidth #the prior functions exit before this can be called because kings and knights both use this on position instead of iterating
    moves=[]
    if piece==1:
        horizontalMoves=[]
        if xPosition!=0: #not on leftmost file
            horizontalMoves.append(position-1)
        if xPosition!=boardWidth-1:
            horizontalMoves.append(position+1)
        moves=list(horizontalMoves)
        horizontalMoves.insert(1,position) #allow orthogonal vertical moves
        if position>=boardWidth: #not on bottom row
            moves+=[i-boardWidth for i in horizontalMoves]
        if position<boardSquares-boardWidth: #not on top row
            moves+=[i+boardWidth for i in horizontalMoves]
    elif piece==5: #extremely inelegant but I will call it hardcoded instead
        return precomputedKnightMoves[position]
        #xMovement=max(xPosition-boardWidth+3,0) if xPosition>1 else -1-(xPosition==0) #removed because I realised it doesn't work with 3*3 boards (where it's both 1 and -1)
        sideObstructions=[max(2-xPosition,0),max(xPosition-boardWidth+3,0),(position<2*boardWidth)*(1+(position<boardWidth)),(position>=boardSquares-2*boardWidth)*(1+(position>=boardSquares-boardWidth))] #directions [left,right,down,up], 0 is unobstructed, 1 is next to edge, 2 is on edge
    ''''if sideObstructions[0]<2:
            if sideObstructions[3]==0:
                moves+=(-1,-2)
            if sideObstructions[4]==0:
                moves+=(-1,2)
            if sideObstructions[0]==0:
                if sideObstructions[3]<2:
                    moves+=(-2,-1)
                if sideObstructions[4]<2:
                    moves+=(-2,1)
        if sideObstructions[1]<2:
            if sideObstructions[3]==0:
                moves+=(1,2)
            if sideObstructions[4]==0:
                moves+=(1,-2)
            if sideObstructions[1]==0:
                if sideObstructions[3]<2:
                    moves+=(2,1)
                if sideObstructions[4]<2:
                    moves+=(2,-1)''' #this part not finished due to inelegance (and using maximum 12 list lookups (you can do it in 8 if you're willing to repeat statements more, but I can't find an efficient way to do '(do c and (b if d)) if a else (b if e)' ))
    return moves


statesWithoutTurns=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateSquareAttacks=[] #list of whether each square is attacked and (if so) by whom
for i in range(boardSquares):
    iKingMoves=findPieceMoves(1,i) #the new Apple product
    for j in range(boardSquares):
        if not (i==j or j in iKingMoves):
            statesWithoutTurns.append([[(1 if k==i or k==j else 0),(1 if k==j else 0)] for k in range(boardSquares)]) #each square in each state list (in the list of them) is a list of the piece and its colour
            attackedSquares=[]
            for k,s in enumerate(statesWithoutTurns[-1]): #cannot be list comprehension because it references the list as it constructs it (I am greatly saddened)
                for l in findPieceMoves(s[0],k):
                    if [l,s[1]] not in attackedSquares:
                        attackedSquares.append([l,s[1]]) #will have to be made more complicated if pawns added
                #print(attackedSquares)
            #[0,0] is empty, [1,0] is white, [1,1] is black (I will eventually find how to make lists of bits to speed it up (like bitboards))
            stateSquareAttacks.append([[int([k,l] in attackedSquares) for l in range(2)] for k in range(boardSquares)]) #[0,0] is empty, [1,0] white, [0,1] black, [1,1] both
#print(len(statesWithoutTurns),"states without turns:",statesWithoutTurns)
states=[[j,i] for j in range(2) for i in statesWithoutTurns] #each state is formatted [colour to move,[[[square piece],[square colour]],[[square piece],[square colour]], ...]]
#print(len(states),"states:",states)
stateSquareAttacks=[i for j in range(2) for i in stateSquareAttacks] #state formatted [[attacked by white?,attacked by black?] for square in range(boardSquares)] #get a load of the comments' opening square brackets' kerning
#print(len(stateSquareAttacks),"state square attacks:",stateSquareAttacks)
stateMoves=[[[j for j in findPieceMoves(s[1][i][0],i) if s[1][i][0]!=1 or stateSquareAttacks[a][j][1-s[0]]==0] if (s[1][i][1]==s[0]) else [] for i in range(boardSquares)] for a,s in enumerate(states)] #is list of lists of destination squares for each piece #the i list comprehension if statement would have (s[1][i][0]!=0 and ) but is now superseded by findPieceMoves
#print(len(stateMoves),"state moves:",stateMoves)
stateTransitions=[[states.index([(1-t[0]),[[0,0] if k==i else (t[1][i] if k==p else r) for k,r in enumerate(t[1])]]) for i,q in enumerate(stateMoves[s]) for j,p in enumerate(q)] for s,t in enumerate(states)]
print("transitions between",len(states),"states:",stateTransitions)

def underline(input): #from https://stackoverflow.com/a/71034895
    return '{:s}'.format('\u0332'.join(input+' '))[0:-1]

def printBoard(board):
    output=""
    stateToPrint=""
    for i,s in enumerate(board):
        letter=pieceSymbols[s[1]][s[0]]
        if (i%boardWidth+math.floor(i/boardWidth))%2==1: #light square
            letter=underline(letter)
        stateToPrint+=letter
        #print(stateToPrint)
        if (i+1)%boardWidth==0:
            output+=stateToPrint
            output+='''
'''
            #print(output)
            stateToPrint=""
    return output

pygame.init()
black=(0,0,0)
squareColours=((236,217,185),(174,137,104)) #I am using lichess's square colours (I am wanted throughout NATO)
dims=2
size=[1050]*dims #my computer resolution (to let NATO catch me more easily)
screen = pygame.display.set_mode((size[0], size[1]))
cameraPosition=[i/2 for i in size]
cameraAngle=[1]+[0]*3
clickDone=0
boardLastPrinted=0
rad=size[0]/len(states)
#bitColours=[[int(255*(math.cos((j/n-i/3)*2*math.pi)+1)/2) for i in range(3)] for j in range(n)]
squares=[[[[s*rad,0]]+[[size[di]/2,random.random()/2**8] for di in range(dims-1)],[rad]*2,1, squareColours[t[0]]] for s,t in enumerate(states)]
FPS=60
drag=0.1
gravitationalConstant=-(size[0]/10)/(len(squares)/64)**2
hookeStrength=1/size[0]
def physics():
    for i in squares:
        if drag>0:
            absVel=max(1,math.sqrt(sum([i[0][di][1]**2 for di in range(dims)]))) #each dimension's deceleration from drag is its magnitude as a component of the unit vector of velocity times absolute velocity squared, is actual component times absolute velocity.
            for di in range(dims):
                i[0][di][1]*=1-absVel*drag #air resistance
        for di in range(dims):
            i[0][di][0]+=i[0][di][1]
    for i,k in enumerate(squares[:-1]):
        for j,l in enumerate(squares[i:]):
            differences=[l[0][di][0]-k[0][di][0] for di in range(dims)]
            gravity=gravitationalConstant/max(1,math.sqrt(sum([di**2 for di in differences])**3))
            for di in range(dims):
                k[0][di][1]+=differences[di]*(hookeStrength*(i+j in stateTransitions[i])+gravity*l[2])
                l[0][di][1]-=differences[di]*(hookeStrength*(i in stateTransitions[i+j])+gravity*k[2])
def drawShape(size,pos,colour,shape):
    if shape==0:
        surf = pygame.Surface(size)
        surf.fill(colour)
        rect = surf.get_rect()
        screen.blit(surf, pos)
    else:
        pygame.draw.circle(screen, colour, pos, size[0])
def drawLine(initial,destination,colour):
    pygame.draw.line(screen,colour,initial,destination)

def quaternionMultiply(a,b):
    return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],a[0]*b[3]+a[1]*b[2]+a[2]*b[1]+a[3]*b[0]]

def quaternionConjugate(q):
    return [q[0]]+[-q[i] for i in range(1,len(q))]

def rotateVector(v,q): #sR is stereographic radius (to be passed through to perspective function)
    return quaternionMultiply(quaternionMultiply(q,[0]+v),quaternionConjugate(q))

pixelAngle=math.tau/max(size)
def rotateByScreen(angle,screenRotation):
    magnitude=math.sqrt(sum([i**2 for i in screenRotation]))
    if magnitude==0:
        return angle
    else:
        magpi=magnitude*pixelAngle
        simagomag=math.sin(magpi)/magnitude #come and get your simagomags delivered fresh
        #print("screen rotation",math.sqrt(sum([i**2 for i in angle])),"multiplication",sum([i**2 for i in [math.cos(magpi),-screenRotation[1]*simagomag,screenRotation[0]*simagomag,0]]),"output",sum([i**2 for i in quaternionMultiply([math.cos(magpi),-screenRotation[1]*simagomag,screenRotation[0]*simagomag,0], angle)]),"input",sum([i**2 for i in angle]))
        return quaternionMultiply([math.cos(magpi),-screenRotation[1]*simagomag,screenRotation[0]*simagomag,0], angle)

def findSquareScreenPositions():
    output=[[s[0][di][0]-cameraPosition[di] for di in range(dims)] for s in squares]
    if dims==3:
        output=[rotateVector(rotateVector(cameraAngle,[0]+s),quaternionConjugate(cameraAngle))[0:2] for s in output]
    return output

oldMouse=pygame.mouse.get_pos()
run=True
while run:
    for event in pygame.event.get():
        run=event.type != pygame.QUIT
        clickDone=event.type == pygame.MOUSEBUTTONUP
    cameraPosition=[sum([i[0][di][0] for i in squares])/len(squares)-size[di]/2 for di in range(dims)]
    if dims==3:
        mouse=pygame.mouse.get_pos()
        mouseChange=[mouse[i]-oldMouse[i] for i in range(2)]
        oldMouse=mouse
        if pygame.mouse.get_pressed()[0]==1:
            cameraAngle=rotateByScreen(cameraAngle, mouseChange)
    squareScreenPositions=findSquareScreenPositions()
    physics()
    screen.fill(black)
    for i,k in enumerate(stateTransitions):
        for j,l in enumerate(k):
            drawLine(squareScreenPositions[i],squareScreenPositions[l],squareColours[states[i][0]])
    for i,k in enumerate(squares):
        drawShape(k[1],squareScreenPositions[i],k[3],1)
        if clickDone and i!=boardLastPrinted and sum([(squareScreenPositions[i][di]-mouse[di])**2 for di in range(dims)])<k[1][0]**2:
            #print(printBoard(states[i][1]))
            boardLastPrinted=i
    pygame.display.flip()
    clock.tick(FPS)
else:
    exit()
