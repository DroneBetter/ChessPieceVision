import math, random
from sympy.utilities.iterables import multiset_permutations, combinations #generates permutations where elements are identical, from https://stackoverflow.com/a/60252630

boardWidth=3
boardSquares=boardWidth**2
board=[]*boardSquares
pieceNames=["empty","king","queen","rook","bishop","knight","pawn"]
pieceSymbols=[[" ","k","q","r","b","n","p"],[" ","K","Q","R","B","N","P"]]
fileLetters=["a","b","c","d","e","f","g","h"]
def parseMaterial(materialString): #I think in the endgame material notation, the piece letters are all capitalised but the v isn't
    vLoc=materialString.index("v")
    return [[pieceSymbols[1].index(i),0] for i in materialString[:vLoc] if i!="K"]+[[pieceSymbols[1].index(i),1] for i in materialString[vLoc+1:] if i!="K"] #not sure how to shorten (elses don't seem to work in append-forgoing if statements in list comprehensions)
def generateCombinations(material):
    duplicateCombinations=[list(c) for m in range(len(material)+1) for c in combinations(material,m)]
    nonDuplicateCombinations=[]
    for c in duplicateCombinations:
        if c not in nonDuplicateCombinations:
            nonDuplicateCombinations.append(c)
    return nonDuplicateCombinations
combinations=generateCombinations(parseMaterial("KNNvK"))
print("combinations:",combinations)

def generatePermutations(material,squares):
    thingsToPermute=material+[[0,0]]*squares
    return list(multiset_permutations(thingsToPermute))

def appendMove(relativeMovement):
    return position+relativeMovement[0]+boardWidth*relativeMovement[1]

precomputedKnightMoves=[]
def findPieceMoves(piece,position,boardState): #outputs list of squares to which piece can travel
    if piece==0:
        return [] #return exits the function
    if piece==2:
        return sum(findPieceMoves(i,position,boardState) for i in range(3,5))
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
        if knightMovesPrecomputed:
            return precomputedKnightMoves[position]
        #xMovement=max(xPosition-boardWidth+3,0) if xPosition>1 else -1-(xPosition==0) #removed because I realised it doesn't work with 3*3 boards (where it's both 1 and -1)
        sideObstructions=[max(2-xPosition,0),max(xPosition-boardWidth+3,0),(position<2*boardWidth)+(position<boardWidth),(position>=boardSquares-2*boardWidth)+(position>=boardSquares-boardWidth)] #directions [left,right,down,up], 0 is unobstructed, 1 is next to edge, 2 is on edge
        if sideObstructions[0]<2:
            if sideObstructions[2]==0:
                moves.append((-1,-2))
            if sideObstructions[3]==0:
                moves.append((-1,2))
            if sideObstructions[0]==0:
                if sideObstructions[2]<2:
                    moves.append((-2,-1))
                if sideObstructions[3]<2:
                    moves.append((-2,1))
        if sideObstructions[1]<2:
            if sideObstructions[2]==0:
                moves.append((1,-2))
            if sideObstructions[3]==0:
                moves.append((1,2))
            if sideObstructions[1]==0:
                if sideObstructions[2]<2:
                    moves.append((2,-1))
                if sideObstructions[3]<2:
                    moves.append((2,1)) #I can't find an efficient way to do (i if e and b), (j if f and a), (k if f and c), (l if g and b), (m if g and d), (n if h and c), (o if h and a) and (p if e and d) where e implies a, f implies b, g implies c and h implies d (it can be implemented in eight lookups trivially if you're creating a circuit board but requires twelve with this method)
        moves=[position+m[0]+m[1]*boardWidth for m in moves]
            
    return moves
def precomputeKnightMoves():
    return [findPieceMoves(5,i,[[0,0]]*boardSquares) for i in range(boardSquares)]
knightMovesPrecomputed=0
precomputedKnightMoves=precomputeKnightMoves()
knightMovesPrecomputed=1

print("precomputed knight moves:",precomputedKnightMoves)
#piecePermutations=[[[0,0]]*(boardSquares-2)]
statesWithoutTurns=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateSquareAttacks=[] #list of whether each square is attacked and (if so) by whom
stateChecks=[]
for r in combinations:
    piecePermutations=generatePermutations(r,boardSquares-2-len(r))
    #print("permutation lengths (should be "+str(boardSquares)+"):",[len(i) for i in piecePermutations])
    for i in range(boardSquares):
        iKingMoves=findPieceMoves(1,i,[[0,0]]*boardSquares) #the new Apple product
        for j in range(boardSquares):
            if not (i==j or j in iKingMoves):
                kingState=[[int(k==i or k==j),int(k==j)] for k in range(boardSquares)] #each square in each state list (in the list of them) is a list of the piece and its colour
                fixedKingPermutations=[] #not because the original ones are broken but because the kings are fixed in place
                for q in piecePermutations:
                    m=-1
                    fixedKingPermutations.append([l if l[0]==1 else q[m:=m+1] for l in kingState]) #the walrus operator is quite cute I would say
                #print("fixed-king permutation lengths (should be",str(boardSquares)+"):",[len(i) for i in fixedKingPermutations])
                for q in fixedKingPermutations:
                    statesWithoutTurns.append(q) #each square in each state list (in the list of them) is a list of the piece and its colour
                    attackedSquares=set((l,s[1]) for k,s in enumerate(statesWithoutTurns[-1]) for l in findPieceMoves(s[0],k,q)) #will have to be made more complicated if pawns added (due to destination squares not being attacked)
                    #print(attackedSquares)
                    #[0,0] is empty, [1,0] is white, [1,1] is black (may eventually be pairs of 64-bit binary numbers (like bitboards) when I need to optimise it)
                    stateSquareAttacks.append([[int((k,l) in attackedSquares) for l in range(2)] for k in range(boardSquares)]) #[0,0] is empty, [1,0] white, [0,1] black, [1,1] both
                    stateChecks.append([stateSquareAttacks[-1][i][1],stateSquareAttacks[-1][j][0]])
#print(len(statesWithoutTurns),"states without turns:",statesWithoutTurns)
states=[[j,i] for j in range(2) for i in statesWithoutTurns] #each state is formatted [colour to move,[[[square piece],[square colour]],[[square piece],[square colour]], ...]]
#print(len(states),"states:",states)
stateSquareAttacks*=2 #state formatted [[attacked by white?,attacked by black?] for square in range(boardSquares)] #get a load of the comments' opening square brackets' kerning
#print(len(stateSquareAttacks),"state square attacks:",stateSquareAttacks)
stateChecks*=2
#print("state checks",[[j[0],i] for i,j in zip(stateChecks,states)])
stateMoves=[[[j for j in findPieceMoves(t[1][i][0],i,t) if (t[1][j][0]==0 or t[1][i][1]!=t[1][j][1]) and (s[j][1-t[0]]==0 if t[1][i][0]==1 else t[1][j][0]!=1)] if t[1][i][1]==t[0] else [] for i in range(boardSquares)] for s,t in zip(stateSquareAttacks,states)] #is list of lists of lists of destination squares for each piece #the i list comprehension if statement would have (s[1][i][0]!=0 and ) but is now superseded by findPieceMoves
stateTransitions=[[states.index([1-t[0],[[0,0] if k==i else (t[1][i] if k==p else r) for k,r in enumerate(t[1])]]) for i,q in enumerate(s) for p in q] for s,t in zip(stateMoves,states)]
#print("transitions between",len(states),"states:",stateTransitions)
stateIllegalities=[(i[1-j[0]]==1) for i,j in zip(stateChecks,states)]
#print("state illegalities",stateIllegalities)
stateNewIDs=[]
k=-1
prunedStates=0
for i,j in zip(stateIllegalities,states):
    if i==1:
        stateNewIDs.append(None)
    else:
        stateNewIDs.append(k:=k+1)
        prunedStates+=1
def pruneIllegalities(stateList):
    return [j for i,j in zip(stateIllegalities,stateList) if i==0]
#print(len(states),"states pruned to",prunedStates)
#print("state new IDs",stateNewIDs)
states=pruneIllegalities(states)
stateSquareAttacks=pruneIllegalities(stateSquareAttacks)
stateChecks=pruneIllegalities(stateChecks)
'''stateMoves=[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves] #convert from moves being in pieces to being in states directly
stateMoves=[[m[k] for k in range(len(j)) if stateIllegalities[k]==0] for i,j,m in zip(stateIllegalities,stateTransitions,stateMoves) if i==0] #prune
stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in stateMoves] #convert back''' #these are nested for more efficiency
#stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in [[m[k] for k,l in enumerate(j) if stateIllegalities[k]==0] for i,j,m in zip(stateIllegalities,stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves]) if i==0]] #would use this one except it's only currently used to convert a list of an origin and destination to a state ID (for which being parallel with stateTransitions is more efficient)
stateMoves=[[m[k] for k in range(len(j)) if stateIllegalities[k]==0] for i,j,m in zip(stateIllegalities,stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves]) if i==0]
stateTransitions=[[stateNewIDs[k] for k in j if stateIllegalities[k]==0] for i,j in zip(stateIllegalities,stateTransitions) if i==0]
def printWinningnesses():
    i=0
    while i==0 or matesInI!=[0]*3:
        matesInI=[sum(1 for j in stateWinningnesses if j[0]==w and j[1]==i) for w in range(-1,2)]
        if matesInI!=[0]*3:
            print("there are",matesInI[0],"losses in "+str(i)+",",matesInI[1],"stalemates in "+str(i)+", and",matesInI[2],"wins in",i)
        i+=1
stateWinningnesses=[[(0 if w==None else w),(None if w==None else 0)] for w in \
    [-(a[s[1].index([1,s[0]])][1-s[0]]) if t==[] else None for s,t,a in zip(states,stateTransitions,stateSquareAttacks)]] #0 if drawing, 1 if winning, -1 if losing (like engine evaluations but only polarity (and relative like Syzygy, not absolute like engines), not magnitude (due to infinite intelligence))
#it assumes each position is drawing until it learns otherwise (because infinite loops with insufficient material to forcibly stalemate (and be marked as such by the regression) are draws)
#print("state winningnesses:",stateWinningnesses)
#printWinningnesses()
i=0
while i==0 or stateChanges!=0:
    blitStateWinningnesses=[]
    for t,s,w in zip(stateTransitions,states,stateWinningnesses):
        bestWinningness=-1
        bestMoves=0
        if t==[]:
            blitStateWinningnesses.append(w)
        else:
            for k in t:
                candidateWinningness=-stateWinningnesses[k][0]
                candidateMoves=stateWinningnesses[k][1]
                if candidateMoves!=None:
                    candidateMoves+=1
                if candidateWinningness>=bestWinningness and (candidateWinningness>bestWinningness or (candidateMoves>bestMoves if candidateWinningness==-1 else (candidateMoves!=None and (bestMoves==None or candidateMoves<bestMoves)))): #if neither side can win, it will attempt to stalemate as quickly as possible (but still prolongs mate if losing and does it as quickly as possible if winning)
                    bestWinningness=candidateWinningness
                    bestMoves=candidateMoves
            blitStateWinningnesses.append([bestWinningness,bestMoves])
    stateChanges=sum(int(b!=w) for b,w in zip(blitStateWinningnesses,stateWinningnesses))
    print(stateChanges,"states changed")
    stateWinningnesses=blitStateWinningnesses
    #print("new state winningnesses:",stateWinningnesses)
    #printWinningnesses()
    i+=1
printWinningnesses()

#print(stateTransitions)
def underline(input): #from https://stackoverflow.com/a/71034895
    return '{:s}'.format('\u0332'.join(input+' '))[:-1]

def printBoard(board):
    output='''
    '''*(boardWidth)
    stateToPrint=""
    for i,s in enumerate(board):
        letter=pieceSymbols[s[1]][s[0]]
        if (i%boardWidth+math.floor(i/boardWidth))%2==1: #light square
            letter=underline(letter)
        stateToPrint+=letter
        if (i+1)%boardWidth==0:
            output+="\033[F"+stateToPrint
            stateToPrint=""
    return output+"\033["+str(boardWidth-1)+"B"

if input("Would you like to play chess with God (y) or see the state transition diagram (n)? ")=="y":
    def whereIs(square):
        return fileLetters.index(square[0])+(int(square[1])-1)*boardWidth #only supports up to 9*9 boards (but beyond that seems infeasible for now)
    def parseMove(move,state,stateIndex): #supports descriptive and algebraic
        if move[0] in fileLetters:
            return [whereIs(move[2*i:2*i+2]) for i in range(2)]
        elif move[0] in pieceSymbols[1]:
            destination=whereIs(move[-2:])
            restrictedRank=None
            restrictedFile=None
            if len(move)>3:
                restrictionIndex=1
                if move[restrictionIndex] not in fileLetters:
                    restrictedRank=int(move[restrictionIndex])
                    restrictionIndex+=1
                if move[restrictionIndex] in fileLetters:
                    restrictedFile=fileLetters.index(move[restrictionIndex])
            #print(pieceSymbols[1].index(move[0]))
            for i,p in enumerate(state[1]):
                if p[0]==pieceSymbols[1].index(move[0]) and p[1]==state[0] and [i,destination] in stateMoves[stateIndex] and (restrictedFile==None or i%boardWidth==restrictedFile) and (restrictedRank==None or floor(i/boardWidth)==restrictedRank):
                    #print(i,p[0],destination)
                    return [i,destination]
    currentIndex=random.randrange(len(states))
    humanColour=states[currentIndex][0] #it includes a u because this is a British program (property of her majesty)
    while True:
        currentState=states[currentIndex]
        print(printBoard(currentState[1]))
        if currentState[0]==humanColour:
            move=input("state "+str(currentIndex)+", "+("white" if currentState[0]==0 else "black")+" to move. ")
            currentIndex=stateTransitions[currentIndex][stateMoves[currentIndex].index(parseMove(move,currentState,currentIndex))]
        else:
            tablebaseMoves=[i for i in stateTransitions[currentIndex] if stateWinningnesses[i]==[0-stateWinningnesses[currentIndex][0],stateWinningnesses[currentIndex][1]-1]]
            print("state "+str(currentIndex)+", I play",("the only" if len(tablebaseMoves)==1 else "one of "+str(len(tablebaseMoves))),str(["losing","drawing","winning"][stateWinningnesses[currentIndex][0]+1]),"move"+"s"*(len(tablebaseMoves)!=1)+".")
            currentIndex=tablebaseMoves[random.randrange(len(tablebaseMoves))]
else:
    import pygame
    from pygame.locals import *
    clock=pygame.time.Clock()
    pygame.init()
    black=(0,0,0)
    squareColours=((236,217,185),(174,137,104)) #using lichess's square colours but do not tell lichess
    dims=3
    size=[1050]*dims
    screen = pygame.display.set_mode(size[:2])
    cameraPosition=[i/2 for i in size]
    cameraAngle=[[1]+[0]*3]*2
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
                absVel=max(1,math.sqrt(sum(i[0][di][1]**2 for di in range(dims)))) #each dimension's deceleration from drag is its magnitude as a component of the unit vector of velocity times absolute velocity squared, is actual component times absolute velocity.
                for di in i[0]:
                    di[1]*=1-absVel*drag #air resistance
            for di in i[0]:
                di[0]+=di[1]
        for i,k in enumerate(squares[:-1]):
            for j,l in enumerate(squares[i+1:]):
                differences=[l[0][di][0]-k[0][di][0] for di in range(dims)]
                gravity=gravitationalConstant/max(1,sum(di**2 for di in differences)**1.5) #inverse-square law is 1/distance**2, for x axis is cos(angle of distance from axis)/(absolute distance)**2, the cos is x/(absolute), so is x/(abs)**3, however the sum outputs distance**2 so is exponentiated by 1.5 instead of 3
                for di in range(dims):
                    k[0][di][1]+=differences[di]*(hookeStrength*(i+1+j in stateTransitions[i])+gravity*l[2])
                    l[0][di][1]-=differences[di]*(hookeStrength*(i in stateTransitions[i+1+j])+gravity*k[2])
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
        return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]] #this function not to be taken to before 1843

    def quaternionConjugate(q):
        return [q[0]]+[-i for i in q[1:4]]

    def rotateVector(v,q): #sR is stereographic radius (to be passed through to perspective function)
        return quaternionMultiply(quaternionMultiply(q,[0]+v),quaternionConjugate(q))

    pixelAngle=math.tau/max(size)
    def rotateByScreen(angle,screenRotation):
        magnitude=math.sqrt(sum(i**2 for i in screenRotation))
        if magnitude==0:
            return angle
        else:
            magpi=magnitude*pixelAngle
            simagomag=math.sin(magpi)/magnitude #come and get your simagomags delivered fresh
            return quaternionMultiply([math.cos(magpi)]+[i*simagomag for i in screenRotation], angle)

    def findSquareScreenPositions():
        output=[[s[0][di][0]-cameraPosition[di] for di in range(dims)] for s in squares]
        if dims==3:
            output=[[i+di/2 for di,i in zip(size,rotateVector([di-si/2 for di,si in zip(s,size)],cameraAngle[0])[:3])] for s in output]
        return output

    gain=1
    angularVelocityConversionFactor=math.tau/FPS
    mouse=pygame.mouse
    run=True
    while run:
        for event in pygame.event.get():
            run=event.type != pygame.QUIT
            clickDone=event.type == pygame.MOUSEBUTTONUP
        cameraPosition=[sum(i[0][di][0] for i in squares)/len(squares)-size[di]/2 for di in range(dims)]
        if dims==3:
            keys=pygame.key.get_pressed()
            if mouse.get_pressed()[0]==1:
                mouseChange=mouse.get_rel()
            else:
                mouse.get_rel() #otherwise it jumps
                mouseChange=(0,)*2
            arrowAccs=[0]+[keys[pygame.K_UP]-keys[pygame.K_DOWN],keys[pygame.K_RIGHT]-keys[pygame.K_LEFT],keys[pygame.K_e]-keys[pygame.K_q]] 
            magnitude=math.sqrt(sum(abs(i) for i in arrowAccs))
            if magnitude!=0:
                arrowAccs=[i/magnitude for i in arrowAccs]
            for di in range(1,4):
                cameraAngle[1][di]+=arrowAccs[di]*gain*angularVelocityConversionFactor
                cameraAngle[1][di]/=1+drag #cameraOrientation[1][0] isn't used (because they're yaw,pitch,roll but they pretend to be i,j,k (no w))
            mouserino=[cameraAngle[1][1]-mouseChange[1],cameraAngle[1][2]+mouseChange[0],cameraAngle[1][3]] #temporarily less elegant so rotateByScreen can use comprehension
            cameraAngle[0]=rotateByScreen(cameraAngle[0],mouserino)
        squareScreenPositions=findSquareScreenPositions()
        #print(squareScreenPositions)
        renderOrder=[i for _, i in sorted([(j[0],i) for i,j in enumerate(squareScreenPositions)])]
        squareScreenPositions=[i[1:3] for i in squareScreenPositions]
        physics()
        screen.fill(black)
        for sc,st,k in zip(squareScreenPositions,states,stateTransitions):
            for l in k:
                drawLine(sc,squareScreenPositions[l],squareColours[st[0]])
        if clickDone:
            mousePos=mouse.get_pos()
        for i in renderOrder:
            k=squares[i]
            drawShape(k[1],squareScreenPositions[i],k[3],1)
            if clickDone and i!=boardLastPrinted and sum((squareScreenPositions[i][di]-mousePos[di])**2 for di in range(2))<k[1][0]**2: #the range(2) will eventually have to be changed when I get a 3D monitor
                print(printBoard(states[i][1]))
                boardLastPrinted=i
        pygame.display.flip()
        clock.tick(FPS)
    else: exit()
