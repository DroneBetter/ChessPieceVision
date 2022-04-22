import math, random
from sympy.utilities.iterables import combinations, multiset_permutations #generates permutations where elements are identical, from https://stackoverflow.com/a/60252630
def sgn(n):
    return 1 if n>0 else -1 if n<0 else 0

boardWidth=8
halfWidth=(boardWidth-1)//2
boardSquares=boardWidth**2
pieceNames=["empty","king","queen","rook","bishop","knight","pawn","nightrider"]
iterativePieces=[           2,      3,     4,                       7]
elementaryIterativePieces=[         3,     4,                       7] #may be optimisable further for nightriders because kings can't move to squares that are only in check after being moved to with them
pieceSymbols=[[" ","k","q","r","b","n","p","m"],[" ","K","Q","R","B","N","P","M"]] #nightriders are M because Wikipedia said to make them N and substitute knights for S (which is shallow and pedantic)
axisLetters=[["a","b","c","d","e","f","g","h"],["1","2","3","4","5","6","7","8"]]

def parseMaterial(materialString): #I think in the endgame material notation, the piece letters are all capitalised but the v isn't
    return [(pieceSymbols[1].index(j),c) for c,i in enumerate(materialString.split("v")) for j in (i[1:] if i[0]=="K" else i)]
def generateCombinations(material):
    return set(c for m in range(len(material)+1) for c in combinations(material,m))
combinations=generateCombinations(parseMaterial("KMNvK"))
print("combinations:",combinations)
def generatePermutations(material,squares):
    return multiset_permutations(material+((0,0),)*squares)

increments=(tuple((p,p==1,p*boardWidth**di) for p in range(-1,3,2) for di in range(2)),tuple(((x,y),(x==1,y==1),x+y*boardWidth) for x in range(-1,3,2) for y in range(-1,3,2)),tuple(((x,y),(x>0,y>0),x+y*boardWidth) for s in range(2) for x in range(-1*(2-s),3*(2-s),2*(2-s)) for y in range(-1*(1+s),3*(1+s),2*(1+s))))
def findPieceMoves(boardState,position,piece): #outputs list of squares to which piece can travel
    if piece[0]==0:
        return []
    if piece[0]==2:
        return [j for i in range(3,5) for j in findPieceMoves(boardState,position,i)]
    spatial=(position%boardWidth,position//boardWidth)
    if piece[0]==1:
        moves=(spatial[0]!=0)*[position-1]+(spatial[0]!=boardWidth-1)*[position+1]
        horizontalMoves=moves+[position] #allow orthogonal vertical moves
        moves+=(position>=boardWidth)*[i-boardWidth for i in horizontalMoves]+(position<boardSquares-boardWidth)*[i+boardWidth for i in horizontalMoves]
    if piece[0] in elementaryIterativePieces:
        moves=[]
        for i,(p,b,n) in enumerate(increments[elementaryIterativePieces.index(piece[0])]): #indice, (polarity, boolean polarity,increment)
            arm=position
            #armSpatial=(spatial[i%2] if piece[0]==3 else spatial)
            for i in range((boardWidth-1-spatial[i%2] if b else spatial[i%2]) if piece[0]==3 else min((boardWidth-1-s if bi else s) for s,bi in zip(spatial,b)) if piece[0]==4 else min((boardWidth-1-s if pi>0 else s)//abs(pi) for s,pi in zip(spatial,p))):
                '''if piece[0]==3:
                    armSpatial+=p
                else:
                    armSpatial=map(sum,zip(armSpatial,p))'''
                arm+=n
                if boardState[arm][0]!=0:
                    if boardState[arm][1]!=piece[1]:
                        moves.append(arm)
                    break
                else:
                    moves.append(arm)
    if piece[0]==5:
        if knightMovesPrecomputed:
            return precomputedKnightMoves[position]
        moves=[(position+xPolarity*(2-skewedness)+yPolarity*(1+skewedness)*boardWidth) for skewedness in range(2) for xPolarity in range(-1,3,2) if (spatial[0]<boardWidth-2+skewedness if xPolarity==1 else spatial[0]>1-skewedness) for yPolarity in range(-1,3,2) if (spatial[1]<boardWidth-1-skewedness if yPolarity==1 else spatial[1]>skewedness)] #do not touch (you will break it) #could perhaps be made more elegant by XORing skewedness with di to reuse condition
    return moves
def precomputeKnightMoves():
    return [findPieceMoves(((0,0),)*boardSquares,i,(5,0)) for i in range(boardSquares)]
knightMovesPrecomputed=0
precomputedKnightMoves=tuple(precomputeKnightMoves())
knightMovesPrecomputed=1
#print("precomputed knight moves:",precomputedKnightMoves)

def firstDisparity(both): #from https://stackoverflow.com/a/15830697
    return next(((a[0]-b[0])*2+(a[1]-b[1]) for i, (a, b) in enumerate(both) if a!=b),0)
def axialDisparity(state,axis,suspicious=0): #very suspicious
    return firstDisparity(((state[x*boardWidth**i+y*boardWidth**(1-i)] for i in range(2)) for x in range(boardWidth) for y in range(x)) if axis==2 else ((state[x*(1-2*i)*boardWidth**axis+(boardWidth-1-y if suspicious else y)*boardWidth**(1-axis)+(boardWidth-1)*i] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))<0

symmetryReduction=(input("Would you like reduction by eightfold symmetry? ")=="y")
states=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateKingPositions=[]
leftHalf=[x+y*boardWidth for y in range(boardWidth) for x in range(math.ceil(boardWidth/2))]
diagonalHalf=[x+y*boardWidth for x in range(boardWidth) for y in range(x+1)]

def generateKingPositions(pawns):
    whiteKingRange=(leftHalf if pawns else [x+y*boardWidth for x in range(math.ceil(boardWidth/2)) for y in range(x+1)]) if symmetryReduction else range(boardSquares)
    #print("permutation lengths (should be "+str(boardSquares)+"):",map(len,piecePermutations))
    kingPositions=[(i,j) for i,iKingMoves in zip(whiteKingRange,[findPieceMoves(((0,0),)*boardSquares,i,(1,0)) for i in whiteKingRange]) for j in ((whiteKingRange if i==(boardSquares-1)/2 else leftHalf if i%boardWidth==(boardWidth-1)/2 else diagonalHalf if i%boardWidth==i//boardWidth and pawns==0 else range(boardSquares)) if symmetryReduction else range(boardSquares)) if not (i==j or j in iKingMoves)]
    kingStates=[tuple((int(k==i or k==j),int(k==j)) for k in range(boardSquares)) for i,j in kingPositions] #each square in each state list (in the list of them) is a list of the piece and its colour
    kingLineOfSymmetry=[2 if i%boardWidth==i//boardWidth and j%boardWidth==j//boardWidth else (0 if i%boardWidth==j%boardWidth==halfWidth else 1 if i//boardWidth==j//boardWidth==halfWidth else -1) if boardWidth%2==1 else -1 for i,j in kingPositions] #-1 for no symmetry, 0 for x, 1 for y, 2 for diagonal
    return kingPositions,kingStates,kingLineOfSymmetry

anyPawns=any(p[0]==6 for c in combinations for p in c)
allKingPositions=(generateKingPositions(0),)+(generateKingPositions(1),)*anyPawns
combinationIndices=[]
combinationTurnwises=[]
def constructState(k,m):
    return (l if l[0]==1 else next(m) for l in k)

for c in combinations:
    piecePermutations=tuple(generatePermutations(c,boardSquares-2-len(c))) #leaving as generator expression causes many problems
    #print([i for i in piecePermutations]) #can't be directly printed due to being a generator object
    pawns=any(p[0]==6 for p in c) #pawns prevent eightfold symmetry (I hate them so much)
    (kingPositions,kingStates,kingLineOfSymmetry)=allKingPositions[pawns]
    combinationIndices.append(len(states))
    playerPieces=[[],[]]
    for i in c:
        playerPieces[i[1]].append(i[0])
    combinationTurnwises.append(sorted(playerPieces[0])==sorted(playerPieces[1])) #not very elegant
    (newKingPositions,newStates)=zip(*[(p,i) for p,i,l in ((p,tuple(constructState(k,m)),l) for p,k,l in zip(kingPositions,kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations)) if not symmetryReduction or l==-1 or not axialDisparity(i,l)]) #not tuple(boardReflect(constructState(k,m)) if l!=-1 and axialDisparity(constructState(k,m),l) else tuple(constructState(k,m)) for k,l in zip(kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations)) because the reflected (reduced) one will appear anyway
    stateKingPositions+=newKingPositions
    states+=newStates

def isSymmetry(state,kingPositions): #only for those with kings eightfolded already
    if all(i%boardWidth==halfWidth for i in kingPositions) and boardWidth%2==0:
        return axialDisparity(state,0)
    if all(i%boardWidth==i//boardWidth for i in kingPositions):
        return axialDisparity(state,2)
    return False

combinationIndices.append(len(states))
stateSquareAttacks=[[[(k,l) in attackedSquares for l in range(2)] for k in range(boardSquares)] for q,attackedSquares in zip(states,[set([(m,q[1]) for i,q in enumerate(s) for m in findPieceMoves(s,i,q)]) for s in states])] #like states list but without turn to move and with (attacked by white,attacked by black) for each square
#will have to have exception condition if pawns added (due to not all destination squares being attacked)
stateChecks=[[r[q[l]][1-l] for l in range(2)] for q,r in zip(stateKingPositions,stateSquareAttacks)]

def reflect(axis,position):
    return boardWidth-1-position+position//boardWidth*boardWidth*2 if axis==0 else position%boardWidth+(boardWidth-1-position//boardWidth)*boardWidth if axis==1 else position//boardWidth+(position%boardWidth)*boardWidth if axis==2 else position
def boardReflect(board,axis):
    return tuple(board[reflect(axis,i)] for i in range(boardSquares))
def symmetry(state,reflectionMode=0,reflectionsToApply=[False]*3): #reflection modes: 0 reduces by eightfold, 1 reduces and reports reflections, 2 only reports, 3 applies list of reflections
    if not symmetryReduction:
        return state
    if reflectionMode==3:
        for i,d in enumerate(reflectionsToApply):
            if d:
                state=boardReflect(state,i)
        return state
    kingPositions=[divmod(state.index((1,i)),boardWidth)[::-1] for i in range(2)] #this intakes positions without symmetry applied so doesn't use stateKingPositions 
    pawns=any(s[0]==6 for s in state)
    if reflectionMode>0:
        reflections=[0]*3
    for d,w,b in zip(range(1+(not pawns)),*kingPositions): #iterating through dimensions (pretty cool)
        if w>halfWidth or (boardWidth%2==1 and w==halfWidth and (b>halfWidth or (b==halfWidth and axialDisparity(state,d,(d==0 and (kingPositions[0][1]>halfWidth or (kingPositions[0][1]==halfWidth and kingPositions[1][1]>halfWidth))))))): #the black king can't be on the halfWidth also because it's only one square
            if reflectionMode<2:
                state=boardReflect(state,d)
            kingPositions=[(boardWidth-1-i[0],i[1]) if d==0 else (i[0],boardWidth-1-i[1]) for i in kingPositions]
            if reflectionMode>0:
                reflections[d]=1
    if pawns:
        return state
    if kingPositions[0][0]<kingPositions[0][1] or (kingPositions[0][0]==kingPositions[0][1] and (kingPositions[1][0]<kingPositions[1][1] or (kingPositions[1][0]==kingPositions[1][1] and axialDisparity(state,2)))): #flip white king to bottom-right diagonal half of bottom-left quarter
        if reflectionMode<2:
            state=boardReflect(state,2)
        if reflectionMode>0:
            reflections[2]=1
    return reflections if reflectionMode==2 else [state,reflections] if reflectionMode==1 else state
def positionSymmetry(position,reflectionsToApply,*reverse):
    if symmetryReduction:
        for i,r in enumerate(reversed(reflectionsToApply) if reverse else reflectionsToApply):
            if r:
                position=reflect((2-i if reverse else i),position)
    return position


#print(len(states),"states without turns:",states)
stateTurns=(False,)*len(states) #is less meaningful when turnwise reduction makes turn not always alternate (should be managed by program using tablebase (if not doing regular tablebase things))
def changeTurn(s):
    return tuple((0,0) if q[0]==0 else (q[0],1-q[1]) for q in s)
(newStates,newReflections,newSquareAttacks,newChecks)=zip(*[(*symmetry(changeTurn(s),1),a,c) for t,i,j in zip(combinationTurnwises,combinationIndices[:-1],combinationIndices[1:]) if not symmetryReduction or not t for m,(s,a,c) in enumerate(zip(states[i:j],stateSquareAttacks[i:j],stateChecks[i:j]))])
states+=newStates
stateTurns+=(True,)*len(newStates)
#print(len(states),"states:",states)
stateSquareAttacks+=[symmetry([s[::-1] for s in a],3,r) for a,r in zip(newSquareAttacks,newReflections)] #state formatted [[attacked by white?,attacked by black?] for square in range(boardSquares)] #do not change to "map(reversed,a)" (it will say "TypeError: 'map' object is not subscriptable")
#print(len(stateSquareAttacks),"state square attacks:",stateSquareAttacks)
stateChecks+=[i[::-1] for i in newChecks] #list(map(reversed,newChecks)) causes "TypeError: 'list_reverseiterator' object is not subscriptable" (I hate it so much)

#print("transitions between",len(states),"states:",stateTransitions)
stateIllegalities=[2 if c[1] else (s!=symmetry(s)) for c,s in zip(stateChecks,states)] #0 is good, 1 is incorrect symmetry, 2 is illegal
#print(len(filter(None,stateIllegalities)),"illegal states")
#print("state illegalities",stateIllegalities)
k=iter(range(len(states)))
stateNewIDs=[states.index(symmetry(s)) if i==1 else (None if i==2 else next(k)) for s,i in zip(states,stateIllegalities)]
def pruneIllegalities(stateList):
    return [j for i,j in zip(stateIllegalities,stateList) if i==0]
print(len(states),"states pruned to",len([i for i in stateNewIDs if i!=None]))
stateChecks=[j[0] for i,j in zip(stateIllegalities,stateChecks) if i==0]
states=pruneIllegalities(states)
stateTurns=pruneIllegalities(stateTurns)
stateSquareAttacks=pruneIllegalities(stateSquareAttacks)
turnwise=True #turnwise symmetry reduction (disable if you are using state transition diagram and would like to preserve the property of moving across n edges ^s your turn with n, enable if you like efficiency (enabled by default because I like efficiency))
stateDict=dict(zip((states if turnwise else zip(stateTurns,states)),range(len(states))))
print("state dict done")
#print(min((print(i,j,q,s),len(s)) for i,(s,a) in enumerate(zip(states,stateSquareAttacks)) for j,q in enumerate(a)))
def applyMoveToBoard(state,piece,move):
    return tuple((0,0) if k==piece else ((state[piece][0],1-state[piece][1]) if k==move else (r[0],1-r[1]) if r[0]!=0 else (0,0)) for k,r in enumerate(state)) #must be (0,0) in particular because (0,1) will be for en passant mask
def dictInput(s,i,m):
    return symmetry(applyMoveToBoard(s,i,m)) if turnwise else (1-t,symmetry(applyMoveToBoard(s,i,m)))
stateMoves=[[[m for m in findPieceMoves(s,i,q) if (s[m][0]==0 or q[1]!=s[m][1]) and ((dictInput(s,i,m) in stateDict) if any((i[0] in iterativePieces) for i in s if i!=m) else (q[0]!=1 or a[m][1]==0))] if q[1]==0 else [] for i,q in enumerate(s)] for s,a,t in zip(states,stateSquareAttacks,stateTurns)] #is list of state lists of destination lists for each piece #king can't move to a currently-attacked square (will have to be changed if hopping pieces or something are added, where squares' attackednesses change depending on occupancy)
print("state moves done")
stateTransitions=[[stateDict[dictInput(s,i,m)] for i,q in enumerate(o) for m in q] for s,a,o,t in zip(states,stateSquareAttacks,stateMoves,stateTurns)] #replace stateDict with (print(s),print(tuple(tuple(int(j) for j in i) for i in a)),stateDict[dictInput(s,i,m)]) for diagnostics
print("state transitions done")
stateParents=tuple([[] for i in range(len(states))]) #[[]]*len(states) makes them all point to the same one, it seems
for i,s in enumerate(stateTransitions):
    for t in s:
        stateParents[t].append(i)
print("state parents done")
#stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in [[m[k] for k,l in enumerate(j)] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]] #would use this one except stateMoves is only currently used to convert a list of an origin and destination to a state ID (for which being parallel with stateTransitions is more efficient)
stateMoves=[[m[k] for k in range(len(j))] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]
print("state moves reformatted")

def printWinningnesses(): #could be done inline in the regression loop also to be slightly more efficient (though its performance impact is negligible) and to make it tell you as it finds them instead of at the end (which could take hours for large tablebases)
    i=0
    while i==0 or matesInI!=[0]*3:
        matesInI=[sum(1 for j in stateWinningnesses if j==(w,i)) for w in range(-1,2)]
        if matesInI!=[0]*3:
            print("there are",matesInI[1],"stalemates in "+str(i)+" and",matesInI[2*(i%2)],("wins" if i%2==1 else "losses"),"in",i) #in terms of ply
        i+=1
stateWinningnesses=[(-c,0) if t==[] else (0,None) for t,c in zip(stateTransitions,stateChecks)] #0 if drawing, 1 if winning, -1 if losing (like engine evaluations but only polarity (and relative to side to move like Syzygy, not absolute like engines), not magnitude (due to infinite intelligence))
winningRegressionCandidates=[i for i,w in enumerate(stateWinningnesses) if w[1]!=None]
#it assumes each position is drawing until it learns otherwise (because infinite loops with insufficient material to forcibly stalemate (and be marked as such by the regression) are draws)
#print("state winningnesses:",stateWinningnesses)
#printWinningnesses()
cycles=0
while cycles==0 or stateChanges!=0:
    if cycles%2==0:
        stateChanges=0
        blitStateWinningnesses=stateWinningnesses
        for i in winningRegressionCandidates:
            for p in stateParents[i]:
                if stateWinningnesses[p][1]==None or -stateWinningnesses[i][0]>stateWinningnesses[p][0]: #do not add "or (-stateWinningnesses[i][0]==stateWinningnesses[p][0] and stateWinningnesses[i][1]+1<stateWinningnesses[p][1])" because faster forced win sequences to one which is already winning can't be found (due to it being exhaustive) #stateWinningnesses[i][0] cannot be 1 if changed by previous iteration (it must be drawing or losing, making its identicality)
                    blitStateWinningnesses[p]=(-stateWinningnesses[i][0],stateWinningnesses[i][1]+1)
                    stateChanges+=1
    else:
        blitStateWinningnesses=[]
        winningRegressionCandidates=[]
        for i,(t,w) in enumerate(zip(stateTransitions,stateWinningnesses)):
            bestWinningness=-1
            bestMoves=0
            if t==[] or w[0]!=0: #check/stalemate, existing winning/losing positions (regressed exhaustively already), do not add " or w[1]!=None" for those previously only known to be stalemate (because positions that have a cooperating stalemate as a descendant can be regressed to by those newly found to be winning), respectively
                blitStateWinningnesses.append(w)
            else:
                #print("indices",len(stateWinningnesses),t)
                for k in t:
                    candidateWinningness=-stateWinningnesses[k][0]
                    candidateMoves=None if stateWinningnesses[k][1]==None else stateWinningnesses[k][1]+1
                    if candidateWinningness>=bestWinningness and (candidateWinningness>bestWinningness or (candidateMoves>bestMoves if candidateWinningness==-1 else (candidateMoves!=None and (bestMoves==None or candidateMoves<bestMoves)))): #if neither side can win, it will attempt to stalemate as quickly as possible (but still prolongs mate if losing and does it as quickly as possible if winning)
                        bestWinningness=candidateWinningness
                        bestMoves=candidateMoves
                blitStateWinningnesses.append((bestWinningness,bestMoves))
                if -1==bestWinningness!=w:
                    winningRegressionCandidates.append(i)
        stateChanges=sum(int(b!=w) for b,w in zip(blitStateWinningnesses,stateWinningnesses))
    #print(stateChanges,"states changed")
    stateWinningnesses=blitStateWinningnesses
    #print("new state winningnesses:",stateWinningnesses)
    #printWinningnesses()
    cycles+=1
printWinningnesses()

#print(stateTransitions)

def printBoard(board):
    def underline(input): #from https://stackoverflow.com/a/71034895
        return '{:s}'.format('\u0332'.join(input+' '))[:-1]
    output='''
    '''*boardWidth
    stateToPrint=""
    for i,s in enumerate(board):
        letter=pieceSymbols[s[1]][s[0]]
        stateToPrint+=(underline(letter) if (i%boardWidth+i//boardWidth)%2==1 else letter) #light square underlining #this way is faster than sum(divmod())
        if (i+1)%boardWidth==0:
            output+="\033[F"+stateToPrint
            stateToPrint=""
    return output+"\033["+str(boardWidth-1)+"B"

def initialisePygame(guiMode):
    global clock
    clock=pygame.time.Clock()
    pygame.init()
    global black
    black=(0,0,0)
    global colours
    colours=((236,217,185),(174,137,104),(255,255,255),(0,0,0),(255,0,0),(255,255,0),(0,255,0)) #using lichess's square colours but do not tell lichess
    #light, dark, white, black, red, yellow, green
    global dims
    dims=3
    global size
    size=[1050]*dims
    if guiMode==1: #guiMode van Russom
        size=[i//boardWidth*boardWidth for i in size]
    global screen
    screen = pygame.display.set_mode(size[:2])
    global drawShape
    def drawShape(size,pos,colour,shape):
        if shape==0:
            pygame.draw.rect(screen,colour,pos+size)
        elif shape<5:
            pygame.draw.polygon(screen,colour,[[p+s/2*math.cos(((i+shape/2)/(2 if shape==4 else 4)+di/2)*math.pi) for di,(p,s) in enumerate(zip(pos,size))] for i in range(4 if shape==4 else 8)])
        else:
            pygame.draw.circle(screen,colour,pos,size[0]/2)
    global drawLine
    def drawLine(initial,destination,colour):
        pygame.draw.line(screen,colour,initial,destination)
    global mouse
    mouse=pygame.mouse
    global doEvents
    def doEvents():
        global clickDone
        global run
        clickDone=False
        for event in pygame.event.get():
            run=event.type != pygame.QUIT
            clickDone=event.type == pygame.MOUSEBUTTONUP
        pygame.display.flip()
        clock.tick(FPS)
        screen.fill(black)
    global FPS
    FPS=60

if input("Would you like to play chess with God (y) or see the state transition diagram (n)? ")=="y":
    def whereIs(square):
        return sum(axisLetters[i].index(square[i])*boardWidth**i for i in range(2))
    def parseMove(move,state,thisStateMoves): #supports descriptive and algebraic
        if move[0] in axisLetters:
            return [whereIs(move[2*i:2*i+2]) for i in range(2)]
        else:
            if move[0] in pieceSymbols[1]:
                pieceType=pieceSymbols[1].index(move[0])
                move=move[1:]
            else:
                pieceType=6 #pawn moves (ie. e4) don't begin with P in algebraic notation
            destination=whereIs(move[-2:])
            restrictedAxes=[None]*2
            if len(move)>2:
                for restrictionCharacter in move[:-2]:
                    for i in range(2):
                        if restrictionCharacter in axisLetters[i]:
                            restrictedAxes[i]=axisLetters[i].index(restrictionCharacter)
            #print(pieceSymbols[1].index(move[0]))
            for i,p in enumerate(state[1]):
                if p==(pieceType,state[0]) and [i,destination] in thisStateMoves and (restrictedAxes[0]==None or i%boardWidth==restrictedAxes[0]) and (restrictedAxes[1]==None or i//boardWidth==restrictedAxes[1]):
                    #print(i,p[0],destination)
                    return [i,destination]
    def isOptimal(i):
        #print(stateWinningnesses[i],(-stateWinningnesses[currentIndex][0],stateWinningnesses[currentIndex][1]-1))
        return stateWinningnesses[i][0]==0 if stateWinningnesses[currentIndex][1]==None else stateWinningnesses[i]==(-stateWinningnesses[currentIndex][0],stateWinningnesses[currentIndex][1]-1)
    guiMode=(input("Would you like a GUI? (y/n)")=="y")
    if guiMode:
        def renderBoard(state,thisStateMoves):
            global clickedSquare
            for i,s in enumerate(state):
                squarePosition=[i%boardWidth,(boardWidth-1-i//boardWidth)]
                drawShape([squareSize]*2,[i*squareSize for i in squarePosition],(((0,255,0) if isOptimal(stateTransitions[currentIndex][thisStateMoves.index([selectedSquare,i])]) else (255,0,0)) if selectedness==1 and [selectedSquare,i] in thisStateMoves else colours[sum(squarePosition)%2]),0)
                if s!=(0,0):
                    colour=(0,255,0) if (i==selectedSquare and selectedness==1) else colours[2+s[1]]
                    if s[0]!=0:
                        drawShape([squareSize*3/4]*2,[(i+1/(8 if s[0]==3 else 2))*squareSize for i in squarePosition],colour,(0 if s[0]==3 else s[0]))
                if clickDone and all(0<mousePos[di]/squareSize-squarePosition[di]<1 for di in range(2)):
                    clickedSquare=positionSymmetry(i,boardFlipping,1)
        import pygame
        from pygame.locals import *
        initialisePygame(1)
        selectedSquare=-1
        clickedSquare=-1
        selectedness=0
        squareSize=min(size)//boardWidth
    run=True
    while run:
        moves=1
        currentIndex=random.randrange(len(states)) #use stateWinningnesses.index((-1,20)) to be checkmated in 10 in KNNNvK
        boardFlipping=[0]*3
        humanColour=0 if turnwise else stateTurns[currentIndex] #it includes a u because this is a British program (property of her majesty)
        turn=1
        while moves>0 and run:
            currentState=tuple((i,j) if i==0 else (i,j^turn) for i,j in states[currentIndex])
            moves=len(stateMoves[currentIndex])
            if turnwise:
                turn^=1
            else:
                turn=stateTurns[currentIndex]
            perceivedBoard=symmetry([(i[0],i[1]^turn) for i in currentState],3,boardFlipping)
            print(printBoard(perceivedBoard))
            if moves==0:
                print(("Human" if turn==humanColour else "God"),"is",("checkmated" if stateChecks[currentIndex]==1 else "stalemated"))
            else:
                if turn==humanColour:
                    thisStateMoves=stateMoves[currentIndex]
                    apparentMoves=[[positionSymmetry(j,boardFlipping) for j in i] for i in thisStateMoves]
                    print(thisStateMoves)
                    print(apparentMoves,boardFlipping)
                    if guiMode:
                        moveDone=False
                        while run and not moveDone:
                            doEvents()
                            if clickDone:
                                mousePos=mouse.get_pos()
                                #print([di/squareSize for di in mousePos])
                            renderBoard(perceivedBoard,thisStateMoves)
                            if clickedSquare!=-1:
                                print(clickedSquare)
                                if currentState[clickedSquare][0]==0 or currentState[clickedSquare][1]==humanColour:
                                    if [selectedSquare,clickedSquare] in thisStateMoves:
                                        moveDone=True
                                        parsedMove=[selectedSquare,clickedSquare]
                                        #humanColour^=1
                                else:
                                    selectedness=((not selectedness) or selectedSquare!=clickedSquare)
                                    selectedSquare=clickedSquare
                                    print("s",selectedSquare)
                                clickedSquare=-1
                    else:
                        move=input("state "+str(currentIndex)+", "+("white" if turn==0 else "black")+" to move. ")
                        print(move,(turn,perceivedBoard),thisStateMoves)
                        parsedMove=[positionSymmetry(i,boardFlipping,1) for i in parseMove(move,(turn,perceivedBoard),thisStateMoves)]
                        print(parsedMove)
                    currentIndex=stateTransitions[currentIndex][thisStateMoves.index(parsedMove)]
                    reflections=symmetry(applyMoveToBoard(currentState,parsedMove[0],parsedMove[1]),1)[1]
                    '''if boardFlipping[2]^reflections[2]==1: #inelegant but necessary
                        boardFlipping=[i^j for i,j in zip(boardFlipping[:2],reflections[1::-1])]+[1]
                    else:
                        boardFlipping=[i^j for i,j in zip(boardFlipping[:2],reflections[:2])]+[0]'''
                    boardFlipping=[i^j for i,j in zip(boardFlipping,reflections)]
                    print(boardFlipping)
                else:
                    tablebaseMoves=[i for i,j in enumerate(stateTransitions[currentIndex]) if isOptimal(j)]
                    #print(stateWinningnesses[currentIndex])
                    print("state "+str(currentIndex)+", I play",("the" if len(tablebaseMoves)==1 else "one of "+str(len(tablebaseMoves))),"optimal",str(("losing","drawing","winning")[stateWinningnesses[currentIndex][0]+1]),"move"+"s"*(len(tablebaseMoves)!=1)+".")
                    godMove=tablebaseMoves[random.randrange(len(tablebaseMoves))]
                    parsedMove=stateMoves[currentIndex][godMove]
                    currentIndex=stateTransitions[currentIndex][godMove]
    
    else: exit()
else:
    import pygame
    from pygame.locals import *
    initialisePygame(0)
    cameraPosition=[i/2 for i in size]
    cameraAngle=[[1]+[0]*3,[0]*3]
    clickDone=0
    boardLastPrinted=0
    rad=size[0]/len(states)
    #bitColours=[[int(255*(math.cos((j/n-i/3)*2*math.pi)+1)/2) for i in range(3)] for j in range(n)]
    nodes=[[[[s*rad]+[di/2 for di in size[:3]],[0]+[random.random()/2**8 for di in range(dims-1)]],(rad,)*2, 1, (colours[t],colours[sgn(w[0])+5])] for s,(w,t) in enumerate(zip(stateWinningnesses,stateTurns))]
    #each formatted [position,size,mass,colours]
    drag=0.1
    gravitationalConstant=-(size[0]/10)*(64/len(nodes))**2
    hookeStrength=1/size[0]
    def physics():
        for i in nodes:
            if drag>0:
                absVel=max(1,math.sqrt(sum(di**2 for di in i[0][1]))) #each dimension's deceleration from drag is its magnitude as a component of the unit vector of velocity times absolute velocity squared, is actual component times absolute velocity.
                i[0][1]=[di*(1-absVel*drag) for di in i[0][1]] #air resistance
            i[0][0]=list(map(sum,zip(i[0][0],i[0][1])))
        for i,(it,k) in enumerate(zip(stateTransitions[:-1],nodes[:-1])): #TypeError: 'zip' object is not subscriptable (I hate it so much)
            for j,(jt,l) in enumerate(zip(stateTransitions[i+1:],nodes[i+1:])):
                differences=[li-ki for li,ki in zip(l[0][0],k[0][0])]
                gravity=gravitationalConstant/max(1,sum(di**2 for di in differences)**1.5) #inverse-square law is 1/distance**2, for x axis is cos(angle of distance from axis)/(absolute distance)**2, the cos is x/(absolute), so is x/(abs)**3, however the sum outputs distance**2 so is exponentiated by 1.5 instead of 3
                gravity=(gravity*l[2],gravity*k[2])
                for ni,(ki,li,di) in enumerate(zip(k[0][1],l[0][1],differences)): #we are the knights who say ni
                    #print(ni,di)
                    nodes[i][0][1][ni]+=di*(hookeStrength*(i+1+j in it)+gravity[0])
                    nodes[i+1+j][0][1][ni]-=di*(hookeStrength*(i in jt)+gravity[1])

    def quaternionMultiply(a,b):
        return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]] #this function not to be taken to before 1843

    def quaternionConjugate(q):
        return [q[0]]+[-i for i in q[1:]]

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
        output=[[si-di for si,di in zip(s[0][0],cameraPosition)] for s in nodes]
        if dims==3:
            output=[[i+si/2 for si,i in zip(size,rotateVector([di-si/2 for di,si in zip(s,size)],cameraAngle[0])[1:])] for s in output]
        return output

    gain=1
    angularVelocityConversionFactor=math.tau/FPS
    colourMode=0
    oldSpace=False
    run=True
    while run:
        doEvents()
        cameraPosition=[sum(i[0][0][di] for i in nodes)/len(nodes)-si/2 for di,si in enumerate(size)]
        keys=pygame.key.get_pressed()
        space=keys[pygame.K_SPACE]
        if space==0!=oldSpace:
            colourMode^=1
        oldSpace=space
        if dims==3:
            if mouse.get_pressed()[0]==1:
                mouseChange=mouse.get_rel()
                mouseChange=(-mouseChange[1],mouseChange[0],0)
            else:
                mouse.get_rel() #otherwise it jumps
                mouseChange=(0,)*3
            arrowAccs=[keys[pygame.K_UP]-keys[pygame.K_DOWN],keys[pygame.K_RIGHT]-keys[pygame.K_LEFT],keys[pygame.K_e]-keys[pygame.K_q]] 
            magnitude=math.sqrt(sum(map(abs,arrowAccs)))
            if magnitude!=0:
                arrowAccs=[i/magnitude for i in arrowAccs]
            cameraAngle[1]=[(di+acc*gain*angularVelocityConversionFactor)/(1+drag) for di,acc in zip(cameraAngle[1],arrowAccs)]
            cameraAngle[0]=rotateByScreen(cameraAngle[0],[ci+mi for ci,mi in zip(cameraAngle[1],mouseChange)])
        nodeScreenPositions=findSquareScreenPositions()
        #print(nodeScreenPositions)
        renderOrder=[j for _, j in sorted((p[2],i) for i,p in enumerate(nodeScreenPositions))]
        nodeScreenPositions=[p[:2] for p in nodeScreenPositions]
        physics()
        for sc,st,k,n in zip(nodeScreenPositions,stateWinningnesses,stateTransitions,nodes):
            for l in k:
                drawLine(sc,nodeScreenPositions[l],n[3][colourMode])
        if clickDone:
            mousePos=mouse.get_pos()
        for i,j,n in [(i,nodeScreenPositions[i],nodes[i]) for i in renderOrder]:
            drawShape(n[1],j,n[3][colourMode],5)
            if clickDone and i!=boardLastPrinted and sum((ji-mi)**2 for ji,mi in zip(j,mousePos))<n[1][0]**2:
                print(printBoard(states[i]))
                boardLastPrinted=i
    else: exit()
