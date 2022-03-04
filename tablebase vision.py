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
    return [(pieceSymbols[1].index(i),0) for i in materialString[1:vLoc]]+[(pieceSymbols[1].index(i),1) for i in materialString[vLoc+2:]]
def generateCombinations(material):
    return set(c for m in range(len(material)+1) for c in combinations(material,m))
combinations=generateCombinations(parseMaterial("KNNNvK"))
print("combinations:",combinations)

def generatePermutations(material,squares):
    thingsToPermute=material+((0,0),)*squares
    return multiset_permutations(thingsToPermute)

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
        moves=[(position+xPolarity*(2-skewedness)+yPolarity*(1+skewedness)*boardWidth) for skewedness in range(2) for xPolarity in range(-1,3,2) if (xPosition>1-skewedness if xPolarity==-1 else boardWidth-xPosition>2-skewedness) for yPolarity in range(-1,3,2) if ((position>=(1+skewedness)*boardWidth) if yPolarity==-1 else (position<boardSquares-(1+skewedness)*boardWidth))] #do not touch (you will break it)
    return moves
def precomputeKnightMoves():
    return [findPieceMoves(5,i,((0,0),)*boardSquares) for i in range(boardSquares)]
knightMovesPrecomputed=0
precomputedKnightMoves=precomputeKnightMoves()
knightMovesPrecomputed=1
#print("precomputed knight moves:",precomputedKnightMoves)

symmetryMode=(input("Would you like reduction by eightfold symmetry?")=="y")
statesWithoutTurns=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateKingPositions=[]
leftHalf=[x+y*boardWidth for y in range(boardWidth) for x in range(math.ceil(boardWidth/2))]
for r in combinations:
    piecePermutations=list(generatePermutations(r,boardSquares-2-len(r)))
    #print([i for i in piecePermutations]) #can't be directly printed due to being a generator object
    pawns=[6,0] in r or [6,1] in r #I hate pawns so much
    whiteKingRange=(leftHalf if pawns else [x+y*boardWidth for y in range(math.ceil(boardWidth/2)) for x in range(y,math.ceil(boardWidth/2))]) if symmetryMode==1 else range(boardSquares)
    #print("permutation lengths (should be "+str(boardSquares)+"):",[len(i) for i in piecePermutations])
    for i in whiteKingRange:
        iKingMoves=findPieceMoves(1,i,((0,0),)*boardSquares) #the new Apple product
        blackKingRange=(whiteKingRange if i==(boardSquares-1)/2 else (leftHalf if i%boardWidth==(boardWidth-1)/2 else ([x+y*boardWidth for y in range(boardWidth) for x in range(y,boardWidth)] if i%boardWidth==i//boardWidth and pawns==0 else range(boardSquares)))) if symmetryMode==1 else range(boardSquares)
        for j in blackKingRange:
            if not (i==j or j in iKingMoves):
                kingState=[(int(k==i or k==j),int(k==j)) for k in range(boardSquares)] #each square in each state list (in the list of them) is a list of the piece and its colour
                fixedKingPermutations=[] #not because the original ones are broken but because the kings are fixed in place
                for q in piecePermutations:
                    m=-1
                    fixedKingPermutations.append([l if l[0]==1 else q[m:=m+1] for l in kingState]) #the walrus operator is quite cute I would say
                #print("fixed-king permutation states' lengths (should be",str(boardSquares)+"):",[len(i) for i in fixedKingPermutations])
                statesWithoutTurns+=fixedKingPermutations #each square in each state list (in the list of them) is a list of the piece and its colour
                stateKingPositions+=((i,j),)*len(fixedKingPermutations)
stateSquareAttacks=[[[int((k,l) in attackedSquares) for l in range(2)] for k in range(boardSquares)] for q,attackedSquares in zip(statesWithoutTurns,[set((l,s[1]) for k,s in enumerate(q) for l in findPieceMoves(s[0],k,q)) for q in statesWithoutTurns])] #like states list but without turn to move and with [attacked by white,attacked by black] for each square
#will have to have exception condition if pawns added (due to not all destination squares being attacked)
stateChecks=[[r[stateKingPositions[q][l]][1-l] for l in range(2)] for q,r in enumerate(stateSquareAttacks)]

#print(len(statesWithoutTurns),"states without turns:",statesWithoutTurns)
states=[[j,i] for j in range(2) for i in statesWithoutTurns] #each state is formatted [colour to move,[[[square piece],[square colour]],[[square piece],[square colour]], ...]]
#print(len(states),"states:",states)
stateSquareAttacks*=2 #state formatted [[attacked by white?,attacked by black?] for square in range(boardSquares)] #get a load of the comments' opening square brackets' kerning
#print(len(stateSquareAttacks),"state square attacks:",stateSquareAttacks)
stateKingPositions*=2
stateChecks*=2
#print("state checks",[[j[0],i] for i,j in zip(stateChecks,states)])
stateMoves=[[[j for j in findPieceMoves(t[1][i][0],i,t) if (t[1][j][0]==0 or t[1][i][1]!=t[1][j][1]) and (s[j][1-t[0]]==0 if t[1][i][0]==1 else t[1][j][0]!=1)] if t[1][i][1]==t[0] else [] for i in range(boardSquares)] for s,t in zip(stateSquareAttacks,states)] #is list of lists of lists of destination squares for each piece #the i list comprehension if statement would have (s[1][i][0]!=0 and ) but is now superseded by findPieceMoves

def symmetry(position):
    if symmetryMode==0:
        return position
    def findKings():
        return [position.index((1,i)) for i in range(2)] #doesn't use stateKingPositions because positions without symmetry applied aren't included
    def firstDisparity(both): #from https://stackoverflow.com/a/15830697
        return next(((a[0]-b[0])*2+(a[1]-b[1]) for i, (a, b) in enumerate(both) if a!=b), 0)
    kingPositions=findKings()
    halfWidth=(boardWidth-1)//2
    if kingPositions[0]%boardWidth>halfWidth or (boardWidth%2==1 and kingPositions[0]%boardWidth==halfWidth and (kingPositions[1]%boardWidth>halfWidth or (kingPositions[1]%boardWidth==halfWidth and firstDisparity([[position[x*(1-2*i)-i+(y+i)*boardWidth] for i in range(2)] for x in range(halfWidth) for y in range(boardWidth)])<0))):
        position=[position[boardWidth-1-(i%boardWidth)+i//boardWidth*boardWidth] for i in range(len(position))] #flip white king to left half (or flip black king to left half when white king in centre file)
    if [6,0] in position or [6,1] in position:
        return position
    if kingPositions[0]//boardWidth>halfWidth or (boardWidth%2==1 and kingPositions[0]//boardWidth==halfWidth and (kingPositions[1]//boardWidth>halfWidth or (kingPositions[1]//boardWidth==halfWidth and firstDisparity([[position[x+boardWidth*(y*(1-2*i)+i*(boardWidth-1))] for i in range(2)] for x in range(halfWidth) for y in range(boardWidth)])<0))): #flip white king to bottom half (or black king if white in centre row (for subsequent flip)))
        position=[position[i%boardWidth+(boardWidth-1-i//boardWidth)*boardWidth] for i in range(len(position))]
    kingPositions=findKings()
    if kingPositions[0]%boardWidth<kingPositions[0]//boardWidth or (kingPositions[0]%boardWidth==kingPositions[0]//boardWidth and (kingPositions[1]%boardWidth<kingPositions[1]//boardWidth or (kingPositions[1]%boardWidth==kingPositions[1]//boardWidth and firstDisparity([[position[x*(boardWidth if i else 1)+y*(1 if i else boardWidth)] for i in range(2)] for x in range(halfWidth) for y in range(x)])<0))): #flip white king to bottom-right diagonal half of bottom-left quarter
        position=[position[i//boardWidth+i%boardWidth*boardWidth] for i in range(len(position))]
    return position

stateTransitions=[[states.index([1-t[0],symmetry([(0,0) if k==i else (t[1][i] if k==p else r) for k,r in enumerate(t[1])])]) for i,q in enumerate(s) for p in q] for s,t in zip(stateMoves,states)]
#print("transitions between",len(states),"states:",stateTransitions)
stateIllegalities=[2 if c[1-s[0]]==1 else (s[1]!=symmetry(s[1])) for c,s in zip(stateChecks,states)] #0 is good, 1 is incorrect symmetry, 2 is illegal
#print("state illegalities",stateIllegalities)
k=-1
stateNewIDs=[None if i==2 else (states.index([s[0],symmetry(s[1])]) if i==1 else (k:=k+1)) for s,i in zip(states,stateIllegalities)]
stateNewIDs=[stateNewIDs[s] if i==1 else s for s,i in zip(stateNewIDs,stateIllegalities)]
prunedStates=len([i for i in stateNewIDs if i!=None])
def pruneIllegalities(stateList):
    return [j for i,j in zip(stateIllegalities,stateList) if i==0]
print(len(states),"states pruned to",prunedStates)
#print("state new IDs",stateNewIDs)
states=pruneIllegalities(states)
stateSquareAttacks=pruneIllegalities(stateSquareAttacks)
stateKingPositions=pruneIllegalities(stateKingPositions)
stateChecks=pruneIllegalities(stateChecks)
#stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in [[m[k] for k,l in enumerate(j) if stateIllegalities[k]==0] for i,j,m in zip(stateIllegalities,stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves]) if i==0]] #would use this one except stateMoves is only currently used to convert a list of an origin and destination to a state ID (for which being parallel with stateTransitions is more efficient)
stateMoves=[[m[k] for k in range(len(j)) if stateIllegalities[k]!=2] for i,j,m in zip(stateIllegalities,stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves]) if i==0]
stateTransitions=[[stateNewIDs[k] for k in j if stateIllegalities[k]==0] for i,j in zip(stateIllegalities,stateTransitions) if i==0]

def printWinningnesses(): #could be done inline in the regression loop also to be slightly more efficient (though its performance impact is negligible) and to make it tell you as it finds them instead of at the end (which could take hours for large tablebases)
    i=0
    while i==0 or matesInI!=[0]*3:
        matesInI=[sum(1 for j in stateWinningnesses if j[0]==w and j[1]==i) for w in range(-1,2)]
        if matesInI!=[0]*3:
            print("there are",matesInI[1],"stalemates in "+str(i)+" and",matesInI[2*(i%2)],("wins in" if i%2==1 else "losses in"),i) #in terms of ply
        i+=1
stateWinningnesses=[[(0 if w==None else w),(None if w==None else 0)] for w in \
    [-c[s[0]] if t==[] else None for s,t,a,c in zip(states,stateTransitions,stateSquareAttacks,stateChecks)]] #0 if drawing, 1 if winning, -1 if losing (like engine evaluations but only polarity (and relative like Syzygy, not absolute like engines), not magnitude (due to infinite intelligence))
#print(stateWinningnesses)
#it assumes each position is drawing until it learns otherwise (because infinite loops with insufficient material to forcibly stalemate (and be marked as such by the regression) are draws)
#print("state winningnesses:",stateWinningnesses)
#printWinningnesses()
i=0
while i==0 or stateChanges!=0:
    blitStateWinningnesses=[]
    for t,w in zip(stateTransitions,stateWinningnesses):
        bestWinningness=-1
        bestMoves=0
        if t==[]:
            blitStateWinningnesses.append(w)
        else:
            #print("indices",len(stateWinningnesses),t)
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
    #print(stateChanges,"states changed")
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
        if (i%boardWidth+i//boardWidth)%2==1: #light square
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
            output=[[i+si/2 for si,i in zip(size,rotateVector([di-si/2 for di,si in zip(s,size)],cameraAngle[0])[1:])] for s in output]
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
            mouserino=[cameraAngle[1][1],cameraAngle[1][2]-mouseChange[1],cameraAngle[1][3]+mouseChange[0]] #temporarily less elegant so rotateByScreen can use comprehension
            cameraAngle[0]=rotateByScreen(cameraAngle[0],mouserino)
        squareScreenPositions=findSquareScreenPositions()
        #print(squareScreenPositions)
        renderOrder=[i for _, i in sorted((p[0],i) for i,p in enumerate(squareScreenPositions))]
        squareScreenPositions=[p[1:3] for p in squareScreenPositions]
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
