import math, random, os
imagePath=os.path.join(os.path.dirname(__file__),"Cburnett_pieces")
from sympy.utilities.iterables import combinations, multiset_permutations #generates permutations where elements are identical, from https://stackoverflow.com/a/60252630
from itertools import pairwise,groupby,starmap,chain
from functools import reduce
def sgn(n):
    return 1 if n>0 else -1 if n<0 else 0
def moddiv(a,b): #big endians get out ree
    return divmod(a,b)[::-1]
def conditionalReverse(reversal,toBe):
    return reversed(toBe) if reversal else toBe
def conditionalFlip(flip,toBe):
    return boardWidth+~toBe if flip else toBe
def lap(func,*iterables): #Python 3 was a mistake
    return list(map(func,*iterables))

boardWidth=8
halfWidth=(boardWidth-1)//2
boardSquares=boardWidth**2
pieceNames=["empty","king","queen","rook","bishop","knight","pawn","nightrider"]
iterativePieces=[           2,      3,     4,                       7]
elementaryIterativePieces=[         3,     4,                       7] #may be optimisable further for nightriders because kings can't move to squares that are only in check after being moved to with them
pieceSymbols=[[" ","K","Q","R","B","N","P","M"],[" ","k","q","r","b","n","p","m"]] #nightriders are M because Wikipedia said to make them N and substitute knights for S (which is shallow and pedantic)
axisLetters=[["a","b","c","d","e","f","g","h"],["1","2","3","4","5","6","7","8"]]

def parseMaterial(materialString): #I think in the endgame material notation, the piece letters are all capitalised but the v isn't
    return [(pieceSymbols[0].index(j),c) for c,i in enumerate(materialString.split("v")) for j in (i[1:] if i[0]=="K" else i)]
def generateCombinations(material):
    return {c for m in range(len(material)+1) for c in combinations(material,m)}
combinations=generateCombinations(parseMaterial("KvK"))
print("combinations:",combinations)
def generatePermutations(material,squares):
    return multiset_permutations(material+((0,0),)*squares)

increments=(tuple((p,p==1,p*boardWidth**di) for p in range(-1,3,2) for di in range(2)),tuple(((x,y),(x==1,y==1),x+y*boardWidth) for x in range(-1,3,2) for y in range(-1,3,2)),tuple(((x,y),(x>0,y>0),x+y*boardWidth) for s in range(2) for x in range(-1*(2-s),3*(2-s),2*(2-s)) for y in range(-1*(1+s),3*(1+s),2*(1+s))))
def findPieceMoves(boardState,position,piece): #outputs list of squares to which piece can travel
    if piece[0]==0:
        return []
    if piece[0]==2:
        return [j for i in range(3,5) for j in findPieceMoves(boardState,position,i)]
    spatial=moddiv(position,boardWidth)
    if piece[0]==1:
        moves=(spatial[0]!=0)*[position-1]+(spatial[0]!=boardWidth-1)*[position+1]
        horizontalMoves=moves+[position] #allow orthogonal vertical moves
        moves+=(position>=boardWidth)*[i-boardWidth for i in horizontalMoves]+(position<boardSquares-boardWidth)*[i+boardWidth for i in horizontalMoves]
    if piece[0] in elementaryIterativePieces:
        moves=[]
        for i,(p,b,n) in enumerate(increments[elementaryIterativePieces.index(piece[0])]): #indice, (polarity, boolean polarity,increment)
            arm=position
            #armSpatial=(spatial[i%2] if piece[0]==3 else spatial)
            for i in range(conditionalFlip(b,spatial[i%2]) if piece[0]==3 else min(conditionalFlip(bi,s) for s,bi in zip(spatial,b)) if piece[0]==4 else min(conditionalFlip(pi>0,s)//abs(pi) for s,pi in zip(spatial,p))):
                '''if piece[0]==3:
                    armSpatial+=p
                else:
                    armSpatial=map(sum,zip(armSpatial,p))'''
                arm+=n
                moves.append(arm)
                if boardState[arm][0]!=0:
                    #if boardState[arm][1]!=piece[1]: #formerly moves.append(arm) was conditional here, but capturing own colour isn't allowed by stateMoves generator and this way kings won't be able to take pieces defended by iterative pieces (which will be useful if I ever do implement pin masks and such instead of the current use of dict presence)
                    break
    if piece[0]==5:
        if knightMovesPrecomputed:
            return precomputedKnightMoves[position]
        moves=[(position+xPolarity*(2-skewedness)+yPolarity*(1+skewedness)*boardWidth) for skewedness in range(2) for xPolarity in range(-1,3,2) if (spatial[0]<boardWidth-2+skewedness if xPolarity==1 else spatial[0]>1-skewedness) for yPolarity in range(-1,3,2) if (spatial[1]<boardWidth+~skewedness if yPolarity==1 else spatial[1]>skewedness)] #do not touch (you will break it) #could perhaps be made more elegant by XORing skewedness with di to reuse condition
    return moves
def precomputeKnightMoves():
    return [findPieceMoves(((0,0),)*boardSquares,i,(5,0)) for i in range(boardSquares)]
knightMovesPrecomputed=0
precomputedKnightMoves=tuple(precomputeKnightMoves())
knightMovesPrecomputed=1
#print("precomputed knight moves:",precomputedKnightMoves)

def firstDisparity(both): #from https://stackoverflow.com/a/15830697
    return next((a[0]*(1-2*a[1])-b[0]*(1-2*b[1]) for a,b in both if a!=b),0)<0
def axialDisparity(state,axis,flippings=(False,)*3,reverse=True): #the intended board flipping is reversed to find the index of (the square in the intended board) in the current board ((1,0,1) and (0,1,1) are the only flipping tuples that are each other's inverses instead of their own)
    return False if axis==-1 else firstDisparity(
            ((state[i] for i in conditionalReverse(flippings[2],(conditionalFlip(flippings[flippings[2]&reverse],x)+conditionalFlip(flippings[1^flippings[2]&reverse],y)*boardWidth,
                                                                 conditionalFlip(flippings[flippings[2]&reverse],y)+conditionalFlip(flippings[1^flippings[2]&reverse],x)*boardWidth))) for x in range(boardWidth) for y in range(x))
           if axis==2 else
            ((state[conditionalFlip(i^flippings[flippings[2]&reverse],x)*boardWidth**(axis^flippings[2])+conditionalFlip(flippings[1^(flippings[2]&reverse)],y)*boardWidth**(1^axis^flippings[2])] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))
    #equivalent to (but fixed from)
    '''firstDisparity(
            ((state[i] for i in conditionalReverse(flippings[2],
                     ( (boardSquares+~x-y*boardWidth,boardSquares+~y-x*boardWidth)
                      if flippings[0]^(flippings[2]&reverse) else
                       (x+(boardWidth+~y)*boardWidth,y+(boardWidth+~x)*boardWidth))
                    if flippings[0]^flippings[1] else
                     ( ((1+y)*boardWidth+~x,(1+x)*boardWidth+~y)
                      if flippings[0] else
                       (x+y*boardWidth,y+x*boardWidth))))
                    for x in range(boardWidth) for y in range(x)) #hardcoded tuples instead of an i loop because the transposition is otherwise by exponentiation (like the old one uses (see below)) is slow, I think 
           if axis==2 else
            ((state[ ( ( y+conditionalFlip(1-i,x)*boardWidth
                        if flippings[0]^reverse else
                         (boardWidth+~y)+conditionalFlip(i,x)*boardWidth)
                      if flippings[0]^flippings[1] else
                       ( (boardWidth+~y)+conditionalFlip(1-i,x)*boardWidth
                        if flippings[0] else
                         y+conditionalFlip(i,x)*boardWidth))
                    if flippings[2]^axis else #axis either 0 or 1
                    ( (  conditionalFlip(1-i,x)+(boardWidth+~y)*boardWidth
                        if flippings[0] else
                         conditionalFlip(i,x)+(boardWidth+~y)*boardWidth)
                      if flippings[1] else
                       ( conditionalFlip(1-i,x)+y*boardWidth
                        if flippings[0] else
                         conditionalFlip(i,x)+y*boardWidth))
                    ] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))''' #x and y actually only mean first and second iterables
    #old version (from when it was only a special-case exception for x scanning with uncertain y):
    #return firstDisparity(((state[x*boardWidth**i+y*boardWidth**(1-i)] for i in range(2)) for x in range(boardWidth) for y in range(x)) if axis==2 else ((state[conditionalFlip(i,x)*boardWidth**axis+conditionalFlip(suspicious,y)*boardWidth**(1-axis)] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))

def axialReflect(position,axis):
    return boardWidth+~position+position//boardWidth*boardWidth*2 if axis==0 else position%boardWidth+(boardWidth+~position//boardWidth)*boardWidth if axis==1 else position//boardWidth+(position%boardWidth)*boardWidth if axis==2 else position
def checkTranslation(position,displacement,scrollings): #Python recognises all nonzero ints as True, and Möbius scrolling doesn't matter for verifying whether a displacement is legal (the other axis is flipped but its out-of-boundness is the same)
    return ( scrollings[0] or 0<=position%boardWidth+displacement%boardWidth<boardWidth  #True #torus/Klein/real projective
                                                                                        #if scrollings[0] else
                                                                                         #0<=position%boardWidth+displacement%boardWidth<boardWidth) #vertically-scrolling cylinder/Möbius strip
            if scrollings[1] else
             0<=position//boardWidth+displacement//boardWidth<boardWidth #horizontally-scrolling cylinder/Möbius strip #you would multiply both by boardWidth after floordiv but instead divide boardSquares
            if scrollings[0] else
             0<=position+displacement<boardSquares and 0<=position%boardWidth+displacement%boardWidth<boardWidth) #square

def translate(position,displacement,scrollings): #scrollings are 0 for bounded board behaviour, 1 for toroidal, 2 for Möbius
    return (  conditionalFlip((position//boardWidth+displacement//boardWidth)//boardWidth%2,(position+displacement)%boardWidth)+conditionalFlip((position%boardWidth+displacement%boardWidth)//boardWidth,position//boardWidth+displacement//boardWidth)*boardWidth #real projective plane
             if scrollings[0]==2 else
              conditionalFlip((position//boardWidth+displacement//boardWidth)//boardWidth%2,(position+displacement)%boardWidth)+(position//boardWidth+displacement//boardWidth)*boardWidth #vertical Klein bottle if scrollings[0] else vertical Möbius strip (however they're computed the same (the inputs are up to you to get right (with checkTranslation)))
           if scrollings[1]==2 else
            ( (position+displacement)%boardWidth+conditionalFlip((position%boardWidth+displacement%boardWidth)//boardWidth,position//boardWidth+displacement//boardWidth)%boardWidth*boardWidth #horizontal Klein bottle
             if scrollings[0]==2 else
              (position+displacement)%boardWidth+(position//boardWidth+displacement//boardWidth)%boardWidth*boardWidth #torus
             if scrollings[0] else
              (position%boardWidth+displacement%boardWidth)+(position//boardWidth+displacement//boardWidth)%boardWidth*boardWidth) #vertical cylinder
           if scrollings[1] else
            ( (position+displacement)%boardWidth+conditionalFlip((position%boardWidth+displacement%boardWidth)//boardWidth,position//boardWidth+displacement//boardWidth)*boardWidth #horizontal Möbius strip
             if scrollings[0]==2 else
              (position+displacement)%boardWidth+(position//boardWidth+displacement//boardWidth)*boardWidth #horizontal cylinder #equivalent to (position%boardWidth+displacement%boardWidth)%boardWidth+(position//boardWidth+displacement//boardWidth)*boardWidth because (p%w+d%w)%w=(p+d)%w
             if scrollings[0] else
              position+displacement)) #square

def positionReflect(position,axes,reverse=0): #some are probably reducible further (depending on whether floor division or modulo is more efficient, but also probably regardless)
    return ( ( ( boardWidth*(boardWidth+~position)+(1+boardSquares)*position//boardWidth
                if axes[0]^reverse else
                 (position+1)*boardWidth-(boardSquares+1)*(position//boardWidth)-1)
              if axes[0]^axes[1] else
               ( (1-boardSquares)*(~position//boardWidth)-position*boardWidth
                if axes[0] else
                 position//boardWidth+position%boardWidth*boardWidth))
            if axes[2] else
             ( ( boardSquares+~position
                if axes[0] else
                 position+boardSquares-boardWidth*(1+2*position//boardWidth))
              if axes[1] else
               ( boardWidth+~position+2*boardWidth*(position//boardWidth)
                if axes[0] else
                 position)))
    #equivalent to (but more efficient than)
    #return reduce(axialReflect,conditionalReverse(reverse,[i for i,a in enumerate(axes) if a]),position)
def boardReflect(board,axis):
    #return tuple(board[axialReflect(i,axis)] for i in range(boardSquares)) #old one
    return board if axis==-1 else tuple((x for y in range(boardWidth) for x in reversed(board[y*boardWidth:(y+1)*boardWidth])) if axis==0 else (x for y in range(boardWidth,0,-1) for x in board[(y-1)*boardWidth:y*boardWidth]) if axis==1 else (x for y in range(boardWidth) for x in board[y:y+boardSquares:boardWidth]))

symmetryReduction=(input("Would you like reduction by eightfold symmetry? ")=="y")
combinationIndices=[0]
combinationTurnwises=[]
states=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateTurns=[]
stateSquareAttacks=[]
stateChecks=[]
Tralse=(True+False)/2 #very suspicious
#stateKingPositions=[]
#stateKingLinesOfSymmetry=[]
leftHalf=[x+y*boardWidth for y in range(boardWidth) for x in range(math.ceil(boardWidth/2))]
diagonalHalf=[x+y*boardWidth for x in range(boardWidth) for y in range(x+1)]

def generateKingPositions(pawns):
    whiteKingRange=(leftHalf if pawns else [x+y*boardWidth for x in range(math.ceil(boardWidth/2)) for y in range(x+1)]) if symmetryReduction else range(boardSquares)
    #print("permutation lengths (should be "+str(boardSquares)+"):",map(len,piecePermutations))
    kingPositions=[(i,j) for i,iKingMoves in zip(whiteKingRange,[findPieceMoves(((0,0),)*boardSquares,i,(1,0)) for i in whiteKingRange]) for j in ((whiteKingRange if i==(boardSquares-1)/2 else leftHalf if i%boardWidth==(boardWidth-1)/2 else diagonalHalf if i%boardWidth==i//boardWidth and pawns==0 else range(boardSquares)) if symmetryReduction else range(boardSquares)) if not (i==j or j in iKingMoves)]
    kingStates=[tuple((int(k==i or k==j),int(k==j)) for k in range(boardSquares)) for i,j in kingPositions] #each square in each state list (in the list of them) is a list of the piece and its colour
    kingLineOfSymmetry=[2 if i%boardWidth==i//boardWidth and j%boardWidth==j//boardWidth else (0 if i%boardWidth==j%boardWidth==halfWidth else 1 if i//boardWidth==j//boardWidth==halfWidth else -1) if boardWidth%2==1 else -1 for i,j in kingPositions] #-1 for no symmetry, 0 for x, 1 for y, 2 for diagonal
    return (kingPositions,kingStates,kingLineOfSymmetry)

anyPawns=any(p[0]==6 for c in combinations for p in c)

allKingPositions=(generateKingPositions(0),)+(generateKingPositions(1),)*anyPawns

turnwise=True #turnwise symmetry reduction (disable if you are using state transition diagram and would like to preserve the property of moving across n edges ^s your turn with n, enable if you like efficiency (enabled by default because I like efficiency))
def constructState(k,m):
    return (l if l[0]==1 else next(m) for l in k)
def setKingPawnness(pawns):
    global kingPositions
    global kingStates
    global kingLineOfSymmetry
    (kingPositions,kingStates,kingLineOfSymmetry)=allKingPositions[pawns]
def changeTurn(s):
    return tuple((0,0) if q[0]==0 else q if q[0]==1 else (q[0],1-q[1]) for q in s)
def attackSet(state,kings=True): #will have to have exception condition if pawns added (due to not all destination squares being attacked)
    return {(m,q[1]) for i,q in enumerate(state) if kings or q!=1 for m in findPieceMoves(state,i,q)} #kings to be added subsequently
def attackMask(attackSet,kings=False,kingPositions=[0,0],invert=False):
    attacks=[[(k,l) in attackSet for l in conditionalReverse(invert,range(2))] for k in range(boardSquares)]
    if kings:
        for i,p in enumerate(kingPositions):
            for m in findPieceMoves((),p,(1,0)):
                attacks[m][i]=True
    return attacks

for ci,c in enumerate(combinations):
    piecePermutations=tuple(generatePermutations(c,boardSquares-2-len(c))) #leaving as generator expression causes many problems
    if ci==0:
        pawns=any(p[0]==6 for p in c)
        setKingPawnness(pawns)
    elif any(p[0]==6 for p in c)!=pawns:
        pawns^=True
        setKingPawnness(pawns) #pawns prevent eightfold symmetry (I hate them so much)
    playerPieces=[[],[]]
    for i in c:
        playerPieces[i[1]].append(i[0])
        #playerPieces[i[1]].insert(next((j for j,k in enumerate(playerPieces[i[1]]) if i[0]<k),len(playerPieces[i[1]])),i[0]) #would be more elegant but changes O(n*log(n)) to O(n**2) (should use binary search instead)
    combinationTurnwises.append(sorted(playerPieces[0])==sorted(playerPieces[1])) #not very elegant
    tralseToday=turnwise and combinationTurnwises[-1] #it's going to happen soon (but not today)
    aPoStaLin=((attackSet(i,tralseToday),p,i,l) for p,i,l in ((p,tuple(constructState(k,m)),l) for p,k,l in zip(kingPositions,kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations))) #portmanteau for "attack, position, state, line"
    (newStates,newTurns,newSquareAttacks,newChecks)=( zip(*((i,Tralse,attackMask(a),((p[0],1) in a)) for a,p,i,l in aPoStaLin if not symmetryReduction or l==-1 or not axialDisparity(i,l) and (p[1],0) not in a)) #not tuple(boardReflect(constructState(k,m)) if l!=-1 and axialDisparity(constructState(k,m),l) else tuple(constructState(k,m)) for k,l in zip(kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations)) because the reflected (reduced) one will appear anyway
                                                     if tralseToday else
                                                      zip(*chain.from_iterable(((                        i,    False,             attackMask(a,True,p     ),   ((p[0],1) in a)),)*((p[1],0) not in a)+
                                                                               ((boardReflect(changeTurn(i),l), True,boardReflect(attackMask(a,True,p,True),l),((p[0],0) in a)),)*((p[1],1) not in a) for a,p,i,l in aPoStaLin if not symmetryReduction or l==-1 or not axialDisparity(i,l))))
    states+=newStates
    stateTurns+=newTurns
    stateSquareAttacks+=newSquareAttacks
    stateChecks+=newChecks
    combinationIndices.append(len(states))
print(len(states),"states")
stateDict={s:i for i,s in enumerate(states if turnwise else zip(stateTurns,states))}
print("state dict done")
#print(min((print(i,j,q,s),len(s)) for i,(s,a) in enumerate(zip(states,stateSquareAttacks)) for j,q in enumerate(a)))

def isSymmetry(state,kingPositions): #only for those with kings eightfolded already
    if all(i%boardWidth==halfWidth for i in kingPositions) and boardWidth%2==1:
        return axialDisparity(state,0)
    if all(i%boardWidth==i//boardWidth for i in kingPositions):
        return axialDisparity(state,2)
    return False

def compoundReflect(board,axes):
    return board if axes==(0,0,0) else tuple(x for y in conditionalReverse(axes[not axes[2]],range(boardWidth)) for x in conditionalReverse(axes[axes[2]],(board[y:y+boardSquares:boardWidth] if axes[2] else board[y*boardWidth:(y+1)*boardWidth]))) #equivalent to
''' return board if axes==(0,0,0) else tuple( ( (x for y in reversed(range(boardWidth)) for x in reversed(board[y:y+boardSquares:boardWidth])  )
                                               if axes[0] else
                                                (x for y in          range(boardWidth)  for x in reversed(board[y:y+boardSquares:boardWidth])  ))
                                             if axes[1] else
                                              ( (x for y in reversed(range(boardWidth)) for x in          board[y:y+boardSquares:boardWidth]   )
                                               if axes[0] else
                                                (x for y in          range(boardWidth)  for x in          board[y:y+boardSquares:boardWidth]   ))
                                           if axes[2] else
                                            ( ( (x for y in reversed(range(boardWidth)) for x in reversed(board[y*boardWidth:(y+1)*boardWidth]))
                                               if axes[0] else
                                                (x for y in reversed(range(boardWidth)) for x in          board[y*boardWidth:(y+1)*boardWidth] ))
                                             if axes[1] else
                                              ( (x for y in          range(boardWidth)  for x in reversed(board[y*boardWidth:(y+1)*boardWidth]))
                                               if axes[0] else
                                                board)))''' #which is equivalent to (but faster than)
    #return reduce(boardReflect,[i for i,a in enumerate(axes) if a],board)
def symmetry(state,reflectionMode=0): #reflection modes: 0 reduces by eightfold, 1 reduces and reports reflections, 2 only reports, to apply list of reflections use compoundReflect()
    if not symmetryReduction:
        return state
    kingPositions=[moddiv(state.index((1,i)),boardWidth) for i in range(2)]
    pawns=any(s[0]==6 for s in state)
    reflections=[0]*3
    for d,w,b in zip(range(1+(not pawns)),*kingPositions): #iterating through dimensions (pretty cool)
        if w>halfWidth or (boardWidth%2==1 and w==halfWidth and (b>halfWidth or (b==halfWidth and axialDisparity(state,d,([0,(d==0 and (kingPositions[0][1]>halfWidth or (kingPositions[0][1]==halfWidth and kingPositions[1][1]>halfWidth))),0] if d==0 else reflections))))): #the black king can't be on the halfWidth also because it's only one square
            reflections[d]=1
            kingPositions=[(boardWidth+~i[0],i[1]) if d==0 else (i[0],boardWidth+~i[1]) for i in kingPositions]
    if pawns:
        return state
    reflections[2]=(kingPositions[0][0]<kingPositions[0][1] or (kingPositions[0][0]==kingPositions[0][1] and (kingPositions[1][0]<kingPositions[1][1] or (kingPositions[1][0]==kingPositions[1][1] and axialDisparity(state,2,reflections))))) #flip white king to bottom-right diagonal half of bottom-left quarter
    if reflectionMode<2:
        state=compoundReflect(state,reflections)
    return reflections if reflectionMode==2 else (state,reflections) if reflectionMode==1 else state

def applyMoveToBoard(state,piece,move,invert=True):
    return tuple((0,0) if k==piece else (((state[piece][0],1-state[piece][1]) if invert else state[piece]) if k==move else ((r[0],1-r[1]) if invert else r) if r[0]!=0 else (0,0)) for k,r in enumerate(state)) #must be (0,0) in particular because (0,1) will be for en passant mask
def dictInput(s,i,m):
    #printBoard(symmetry(applyMoveToBoard(s,i,m)))
    #print(symmetry(applyMoveToBoard(s,i,m)) in stateDict)
    return symmetry(applyMoveToBoard(s,i,m)) if turnwise else (not s[0],symmetry(applyMoveToBoard(s[1],i,m)))
'''print([[() if s==(None,) else s for s in l] for l in zip(*[list(zip(*([(None,)*2] if r==[[]]*boardSquares else [((i,m[0]),m[1]) for i,q in enumerate(r) for m in q]))) for r in ([[] if q[0]==0 or q[1] else [(m,stateDict[d]) for m,d in ((m,dictInput(s,i,m)) for m in findPieceMoves(s,i,q) if s[m][0]==0 or q[1]!=s[m][1]) if (d in stateDict if True else (q[0]!=1 or not a[m][1]))] for i,q in enumerate(s)] for s,a in zip((((1, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 1), (0, 0), (3, 0), (0, 0)),),([[False, False], [True, True], [False, True], [True, False], [True, True], [False, False], [True, False], [False, True], [True, True]],)))])])
print(*[list(zip(*([(None,)*2] if r==[[]]*boardSquares else [((i,m[0]),m[1]) for i,q in enumerate(r) for m in q]))) for r in ([[] if q[0]==0 or q[1] else [(m,stateDict[d]) for m,d in ((m,dictInput(s,i,m)) for m in findPieceMoves(s,i,q) if s[m][0]==0 or q[1]!=s[m][1]) if (d in stateDict if True else (q[0]!=1 or not a[m][1]))] for i,q in enumerate(s)] for s,a in zip((((1, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 1), (0, 0), (3, 0), (0, 0)),),([[False, False], [True, True], [False, True], [True, False], [True, True], [False, False], [True, False], [False, True], [True, True]],)))])
exit()'''
(stateMoves,stateTransitions)=[[() if mt==(None,) else mt for mt in l] for l in zip(*[list(zip(*([(None,)*2] if r==[[]]*boardSquares else [((i,m[0]),m[1]) for i,q in enumerate(r) for m in q]))) for r in ([[] if q[0]==0 or q[1] else [(m,stateDict[d]) for m,d in ((m,dictInput(s,i,m)) for m in findPieceMoves(s,i,q) if s[m][0]==0 or q[1]!=s[m][1]) if (d in stateDict if True else (q[0]!=1 or not a[m][1]))] for i,q in enumerate(s)] for s,a in zip(states,stateSquareAttacks))])] #you can replace "if True" with "if any((j[0] in iterativePieces) for j in d)", if you make it account for the fact that when king is in check, other pieces are unmovable except to obstruct or capture attacking piece
#replace stateDict with (print(s),print(tuple(tuple(int(j) for j in i) for i in a)),stateDict[d]) for diagnostics
#print("transitions between",len(states),"states:",stateTransitions)
print("state moves and transitions done")
stateParents=tuple([[] for i in range(len(states))]) #[[]]*len(states) makes them all point to the same one, it seems
for i,s in enumerate(stateTransitions):
    for t in s:
        if t!=None:
            stateParents[t].append(i)
print("state parents done")
#stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in [[m[k] for k,l in enumerate(j)] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]] #would use this one except stateMoves is only currently used to convert a list of an origin and destination to a state ID (for which being parallel with stateTransitions is more efficient)
#stateMoves=[m[:len(j)] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]
#print("state moves reformatted")

def printWinningnesses(): #could be done inline in the regression loop also to be slightly more efficient (though its performance impact is negligible) and to make it tell you as it finds them instead of at the end (which could take hours for large tablebases)
    i=0
    while i==0 or matesInI!=[0]*3:
        matesInI=[sum(j==(w,i) for j in stateWinningnesses) for w in range(-1,2)]
        if matesInI!=[0]*3:
            print("there are",matesInI[1],"stalemates in "+str(i)+" and",matesInI[2*(i%2)],("wins" if i%2==1 else "losses"),"in",i) #in terms of ply
        i+=1
stateWinningnesses=[(-c,0) if t==() else (0,None) for t,c in zip(stateTransitions,stateChecks)] #0 if drawing, 1 if winning, -1 if losing (like engine evaluations but only polarity (and relative to side to move like Syzygy, not absolute like engines), not magnitude (due to infinite intelligence))
winningRegressionCandidates=[i for i,w in enumerate(stateWinningnesses) if w[1]!=None]
#it assumes each position is drawing until it learns otherwise (because infinite loops with insufficient material to forcibly stalemate (and be marked as such by the regression) are draws)
#print("state winningnesses:",stateWinningnesses)
#printWinningnesses()
cycles=0
while True:
    if cycles%2==0:
        stateChanges=0
        blitStateWinningnesses=stateWinningnesses
        for i,pa,(w,m) in ((i,stateParents[i],stateWinningnesses[i]) for i in winningRegressionCandidates):
            for p,(pw,pm) in ((p,blitStateWinningnesses[p]) for p in pa):
                if pm==None or -w>pw: #do not add "or (-stateWinningnesses[i][0]==stateWinningnesses[p][0] and stateWinningnesses[i][1]+1<stateWinningnesses[p][1])" because faster forced win sequences to one which is already winning can't be found (due to it being exhaustive) #stateWinningnesses[i][0] cannot be 1 if changed by previous iteration (it must be drawing or losing, making its identicality)
                    blitStateWinningnesses[p]=(-w,m+1)
                    stateChanges+=1
    else:
        blitStateWinningnesses=[w if t==() or w[0]!=0 else (-opponentWinningness,(max(candidates)+1 if opponentWinningness==1 else (None if (m:=min(candidates,default=None)==None) else m+1))) for t,w,(opponentWinningness,candidates) in zip(stateTransitions,stateWinningnesses,((opponentWinningness,(m for w,m in t if w==opponentWinningness and m!=None)) for t,opponentWinningness in ((t,min((w[0] for w in t),default=0)) for t in [[stateWinningnesses[k] for k in t] for t in stateTransitions])))]
        winningRegressionCandidates=[i for i,(b,w) in enumerate(zip(blitStateWinningnesses,stateWinningnesses)) if b[0]==-1!=w[0]]
        stateChanges=sum(b[0]!=w[0] for b,w in zip(blitStateWinningnesses,stateWinningnesses))
        #print([b[0] for b,w in zip(blitStateWinningnesses,stateWinningnesses) if b[0]!=w[0]])
    #print(stateChanges,"states changed on cycle",cycles)
    stateWinningnesses=blitStateWinningnesses
    #print("new state winningnesses:",stateWinningnesses)
    #printWinningnesses()
    if stateChanges==0:
        break
    else:
        cycles+=1
printWinningnesses()

def printBoard(board):
    print("".join(["".join(("_" if letter==" " else letter+'\u0332') if (i+b)%2==0 else letter for i,letter in enumerate([pieceSymbols[s[1]][s[0]] for s in board[(b-1)*boardWidth:b*boardWidth]]))+"\n" for b in range(boardWidth,0,-1)])+"\033["+str(boardWidth-1)+"B",end="") #ANSI escape sequences
                                           #from https://stackoverflow.com/a/71034895      #light squares underlined
def FEN(board,turn=0):
    return "/".join("".join((str(len(list(q))) if l==" " else "".join(q)) for l,q in groupby(pieceSymbols[s[1]][s[0]] for s in board[b*boardWidth:(b+1)*boardWidth])) for b in range(boardWidth-1,-1,-1))+" "+("b" if turn else "w")+" - - 0 1" #castling, en passant, moves from zeroing and moves from origin state (indice beginning at 1) not yet supported

def initialisePygame(guiMode):
    global clock
    clock=pygame.time.Clock()
    pygame.init()
    global black
    black=(0,0,0)
    global colours
    colours=[(236,217,185),(174,137,104),(255,255,255),(0,0,0),(255,0,0),(255,255,0),(0,255,0)] #using lichess's square colours but do not tell lichess
    global averageColours
    def averageColours(colours):
        return tuple([math.sqrt(sum(c[i]**2 for c in colours)/len(colours)) for i in range(3)]) #correct way, I think
    colours.insert(2,averageColours(colours[:2]))
    #light, dark, white, black, red, yellow, green
    global dims
    dims=3
    global size
    size=[1050]*dims
    if guiMode: #guiMode van Russom
        size=[i//boardWidth*boardWidth for i in size]
    global imageMode
    imageMode=True
    global pieceImages
    try:
        pieceImages=[[pygame.image.load(os.path.join(imagePath,"Chess_"+i+("d" if j else "l")+"t45.svg")) for i in pieceSymbols[1][1:6]] for j in range(2)]
    except:
        imageMode=False
    global minSize
    minSize=min(size[:2])
    global halfSize
    halfSize=[s/2 for s in size]
    global screen
    screen = pygame.display.set_mode(size[:2],pygame.RESIZABLE)
    global drawShape
    def drawShape(size,pos,colour,shape):
        if shape==0:
            pygame.draw.rect(screen,colour,pos+size)
        elif shape<5:
            pygame.draw.polygon(screen,colour,[[p+s/2*math.cos(((i+shape/2)/(2 if shape==4 else 4)+di/2)*math.pi) for di,(p,s) in enumerate(zip(pos,size))] for i in range(4 if shape==4 else 8)])
        else:
            pygame.draw.circle(screen,colour,pos,size/2)
    global drawLine
    def drawLine(initial,destination,colour):
        pygame.draw.line(screen,colour,initial,destination)
    global renderBoard
    def renderBoard(state,perceivedMoves,interactive,boardSize=minSize,renderPosition=(0,0)):
        squareSize=boardSize//boardWidth
        for i,s in enumerate(state):
            if interactive:
                m=[selectedSquare,i]
            squarePosition=[i%boardWidth,(boardWidth+~i//boardWidth)] #I hate Pygame's coordinates so much
            screenPosition=[r+s*squareSize for r,s in zip(renderPosition,squarePosition)]
            drawShape([squareSize]*2,screenPosition,(((0,255,0) if isOptimal(stateTransitions[currentIndex][perceivedMoves.index(m)]) else (255,0,0)) if interactive and selectedness and m in perceivedMoves else colours[sum(squarePosition)%2]),0)
            if s!=(0,0):
                colour=(0,255,0) if (interactive and i==selectedSquare and selectedness) else colours[3+s[1]]
                if s[0]!=0:
                    if imageMode and s[0]<7:
                        screen.blit(pygame.transform.scale(pieceImages[s[1]][s[0]-1],[squareSize]*2),screenPosition)
                    else:
                        drawShape([squareSize*3/4]*2,[(i+1/(8 if s[0]==3 else 2))*squareSize for i in squarePosition],colour,(0 if s[0]==3 else s[0]))
        if interactive and clickDone and all(0<=m<boardSize for m in mousePos[:2]):
            global clickedSquare
            clickedSquare=sum(conditionalFlip(di,zm)*boardWidth**di for di,m in enumerate(m//squareSize for m in mousePos[:2]))
            #clickedSquare=positionReflect(clickedSquare,boardFlipping,1)

    global mouse
    mouse=pygame.mouse
    global doEvents
    def doEvents():
        global clickDone
        global run
        clickDone=False
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
            if event.type==pygame.MOUSEBUTTONUP:
                clickDone=1
            if event.type==pygame.WINDOWRESIZED:
                size[:2]=screen.get_rect().size
                minSize=min(size[:2])
                halfSize[:2]=[s/2 for s in size[:2]]
        pygame.display.flip()
        clock.tick(FPS)
        screen.fill(black)
    global FPS
    FPS=60

def compoundFlipping(a,b,reverses=[False]*2): #applies flipping a then b to [0,0,0], returns resultant flipping tuple
    bee=a[2]^(b[2] and reverses[1]) #bee
    aee=a[2] and reverses[0] #the sound when I see a bee
    return [a[aee]^b[bee],a[1-aee]^b[1-bee],a[2]^b[2]] #derived from following ones
''' return ([a[0]   ^b[a[2]],     a[1]       ^b[not a[2]],     a[2]^b[2]] if reverses==[False,False] else
            [a[a[2]]^b[a[2]],     a[not a[2]]^b[not a[2]],     a[2]^b[2]] if reverses==[True, False] else
            [a[0]   ^b[a[2]^b[2]],a[1]       ^b[not a[2]^b[2]],a[2]^b[2]] if reverses==[False, True] else
            [a[a[2]]^b[a[2]^b[2]],a[not a[2]]^b[not a[2]^b[2]],a[2]^b[2]])''' #found by manually enumerating the 64 compound eightfold flippings in each case (you can trust that it is as right as my brain (slightly more credible than my programming))
    #return [a[0]^b[a[2]],a[1]^b[not a[2]],a[2]^b[2]] #if you do not want reverses

if input("Would you like to play chess with God (y) or see the state transition diagram (n)? ")=="y":
    def whereIs(square):
        return sum(axisLetters[i].index(square[i])*boardWidth**i for i in range(2))
    def parseMove(move,turnToMove,state,perceivedMoves): #supports descriptive and algebraic
        if all(m in axisLetters[i] for i,m in enumerate(move[:2])):
            return [whereIs(move[2*i:2*i+2]) for i in range(2)]
        else:
            if move[0] in pieceSymbols[0]:
                pieceType=pieceSymbols[0].index(move[0])
                move=move[1:]
            else:
                pieceType=6 #pawn moves (ie. e4) don't begin with P in algebraic notation
            mandateTaking=(move[0]=="x")
            if mandateTaking:
                move=move[1:]
            destination=whereIs(move[-2:])
            restrictedAxes=[None]*2
            if len(move)>2:
                for restrictionCharacter in move[:-2]:
                    for i in range(2):
                        if restrictionCharacter in axisLetters[i]:
                            restrictedAxes[i]=axisLetters[i].index(restrictionCharacter)
            print(perceivedMoves,turnToMove,restrictedAxes)
            print((pieceType,turnToMove))
            for i,p in enumerate(state):
                print(p,[i,destination],[i%boardWidth,i//boardWidth])
                if p==(pieceType,turnToMove) and [i,destination] in perceivedMoves and (restrictedAxes[0]==None or i%boardWidth==restrictedAxes[0]) and (restrictedAxes[1]==None or i//boardWidth==restrictedAxes[1]):
                    #print(i,p[0],destination)
                    return (i,destination)
    def isOptimal(i):
        #print(stateWinningnesses[i],stateWinningnesses[currentIndex])
        #print(stateWinningnesses[i],(-stateWinningnesses[currentIndex][0],stateWinningnesses[currentIndex][1]-1))
        return stateWinningnesses[i][0]==0 if stateWinningnesses[currentIndex][1]==None else stateWinningnesses[i]==(-stateWinningnesses[currentIndex][0],stateWinningnesses[currentIndex][1]-1)
    guiMode=(input("Would you like a GUI? (y/n)")=="y")
    if guiMode:
        import pygame
        from pygame.locals import *
        initialisePygame(True)
        selectedSquare=-1
        clickedSquare=-1
        selectedness=False
    run=True
    while run:
        currentIndex=random.randrange(len(states)) #use stateWinningnesses.index((-1,20)) to be checkmated in 10 in KNNNvK
        boardFlipping=[0]*3
        humanColour=0 if turnwise else stateTurns[currentIndex] #it includes a u because this is a British program (property of her majesty)
        turn=True
        while run:
            turn=(not turn) if turnwise else stateTurns[currentIndex]
            currentState=tuple((t,(0 if t==0 else c^turn)) for t,c in states[currentIndex])
            moves=len(stateMoves[currentIndex])
            perceivedState=compoundReflect(currentState,boardFlipping)
            printBoard(perceivedState)
            if moves==0:
                print(("Human" if turn==humanColour else "God"),"is",("checkmated" if stateChecks[currentIndex]==1 else "stalemated"))
                break
            elif turn==humanColour:
                thisStateMoves=stateMoves[currentIndex]
                apparentMoves=[[positionReflect(j,boardFlipping) for j in i] for i in thisStateMoves]
                print(thisStateMoves)
                print(apparentMoves,boardFlipping)
                if guiMode:
                    moveDone=False
                    while run and not moveDone:
                        doEvents()
                        if clickDone:
                            mousePos=mouse.get_pos()
                            #print([di/squareSize for di in mousePos])
                        renderBoard(perceivedState,apparentMoves,True)
                        if clickedSquare!=-1:
                            print(clickedSquare)
                            if perceivedState[clickedSquare][0]!=0 and perceivedState[clickedSquare][1]==humanColour:
                                selectedness=((not selectedness) or selectedSquare!=clickedSquare)
                                selectedSquare=clickedSquare
                                print("s",selectedSquare)
                            elif [selectedSquare,clickedSquare] in apparentMoves:
                                moveDone=True
                                parsedMove=thisStateMoves[apparentMoves.index([selectedSquare,clickedSquare])] #very suspicious
                                #humanColour^=1
                            clickedSquare=-1
                else:
                    move=input("state "+str(currentIndex)+", "+("black" if turn else "white")+" to move. ")
                    print(move,(turn,perceivedState),thisStateMoves)
                    parsedMove=[positionReflect(i,boardFlipping,1) for i in parseMove(move,turn,perceivedState,apparentMoves)]
                    print(parsedMove)
                currentIndex=stateTransitions[currentIndex][thisStateMoves.index(tuple(parsedMove))]
                reflections=symmetry(applyMoveToBoard(currentState,*parsedMove,False),1)[1]
                boardFlipping=compoundFlipping(reflections,boardFlipping,[True,False])
                print(boardFlipping)
            else:
                print(stateWinningnesses[currentIndex],[stateWinningnesses[i] for i in stateTransitions[currentIndex]])
                tablebaseMoves=[i for i,j in enumerate(stateTransitions[currentIndex]) if isOptimal(j)]
                #print(stateWinningnesses[currentIndex])
                print("state "+str(currentIndex)+", I play",("the" if len(tablebaseMoves)==1 else "one of "+str(len(tablebaseMoves))),"optimal",str(("losing","drawing","winning")[stateWinningnesses[currentIndex][0]+1]),"move"+"s"*(len(tablebaseMoves)!=1)+".")
                godMove=random.choice(tablebaseMoves)
                parsedMove=stateMoves[currentIndex][godMove]
                currentIndex=stateTransitions[currentIndex][godMove]
    else: exit()
else:
    import pygame
    from pygame.locals import *
    initialisePygame(False)
    rad=halfSize[0]/len(states)
    #bitColours=[[int(255*(math.cos((j/n-i/3)*2*math.pi)+1)/2) for i in range(3)] for j in range(n)]
    nodes=[[[[s*rad]+halfSize[1:],[0]+[random.random()/2**8 for di in range(dims-1)]],(rad,)*2, 1, (colours[2 if t==Tralse else t],colours[6+sgn(w[0])])] for s,(w,t) in enumerate(zip(stateWinningnesses,stateTurns))]
    #each formatted [position,size,mass,colours]
    def averageNode():
        return [sum(i[0][0][di] for i in nodes)/len(nodes)-si for di,si in enumerate(halfSize)]
    cameraPosition=[averageNode(),[0.0]*3] #must be 0.0, not 0 (to be float for the lap(float.__add__))
    cameraAngle=[[1]+[0]*3,[0]*3]
    clickDone=0
    boardLastPrinted=0
    drag=0.1
    gravitationalConstant=-(size[0]/10)*(64/len(nodes))**2
    hookeStrength=1/size[0]
    def physics():
        for i in nodes:
            if drag>0:
                absVel=max(1,math.hypot(*i[0][1])) #each dimension's deceleration from drag is its magnitude as a component of the unit vector of velocity times absolute velocity squared, is actual component times absolute velocity.
                i[0][1]=[di*(1-absVel*drag) for di in i[0][1]] #air resistance
            i[0][0]=lap(float.__add__,i[0][0],i[0][1])
        for i,(it,k) in enumerate(zip(stateTransitions[:-1],nodes[:-1])): #TypeError: 'zip' object is not subscriptable (I hate it so much)
            for j,(jt,l) in enumerate(zip(stateTransitions[i+1:],nodes[i+1:]),start=i+1):
                differences=[li-ki for li,ki in zip(l[0][0],k[0][0])]
                gravity=gravitationalConstant/max(1,sum(di**2 for di in differences)**1.5) #inverse-square law is 1/distance**2, for x axis is cos(angle of distance from axis)/(absolute distance)**2, the cos is x/(absolute), so is x/(abs)**3, however the sum outputs distance**2 so is exponentiated by 1.5 instead of 3
                gravity=(gravity*l[2],gravity*k[2])
                for ni,(ki,li,di) in enumerate(zip(k[0][1],l[0][1],differences)): #we are the knights who say ni
                    #print(ni,di)
                    nodes[i][0][1][ni]+=di*(hookeStrength*(j in it)+gravity[0])
                    nodes[j][0][1][ni]-=di*(hookeStrength*(i in jt)+gravity[1])

    def quaternionMultiply(a,b):
        return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]] #this function not to be taken to before 1843

    def quaternionConjugate(q): #usually conjugation is inverting the imaginary parts but as all quaternion enthusiasts know, inverting all four axes is ineffectual so inverting the first is ineffectually different from inverting the other three 
        return [-q[0]]+q[1:] #(if you care about memory and not computing power, only the other three need to be stored with their polarities relative to it and the first's sign can be fixed and its magnitude computed (because it's a unit vector))

    def rotateVector(v,q): #sR is stereographic radius (to be passed through to perspective function)
        #equivalent to
        #return quaternionMultiply(quaternionMultiply(q,[0]+v),quaternionConjugate(q))[1:]
        #32 lookups and 32 multiplications
        #expands to (when you remove the v[0] components)
        #return [-(q[1]*v[0]+q[2]*v[1]+q[3]*v[2])*q[0]+(q[0]*v[0]+q[2]*v[2]-q[3]*v[1])*q[1]+(q[0]*v[1]-q[1]*v[2]+q[3]*v[0])*q[2]+(q[0]*v[2]+q[1]*v[1]-q[2]*v[0])*q[3], #resolves to 0 (what did nature mean by this)
        #        -(q[1]*v[0]+q[2]*v[1]+q[3]*v[2])*q[1]-(q[0]*v[0]+q[2]*v[2]-q[3]*v[1])*q[0]+(q[0]*v[1]-q[1]*v[2]+q[3]*v[0])*q[3]-(q[0]*v[2]+q[1]*v[1]-q[2]*v[0])*q[2],
        #        -(q[1]*v[0]+q[2]*v[1]+q[3]*v[2])*q[2]-(q[0]*v[0]+q[2]*v[2]-q[3]*v[1])*q[3]-(q[0]*v[1]-q[1]*v[2]+q[3]*v[0])*q[0]+(q[0]*v[2]+q[1]*v[1]-q[2]*v[0])*q[1],
        #        -(q[1]*v[0]+q[2]*v[1]+q[3]*v[2])*q[3]+(q[0]*v[0]+q[2]*v[2]-q[3]*v[1])*q[2]-(q[0]*v[1]-q[1]*v[2]+q[3]*v[0])*q[1]-(q[0]*v[2]+q[1]*v[1]-q[2]*v[0])*q[0]][1:]
        #112 lookups and 64 multiplications (or 84 and 48 without computing real component (that is 0))
        #when simplified and factorised by v terms (to be a rotation matrix), becomes
        #return [(-q[0]**2-q[1]**2+q[2]**2+q[3]**2)*v[0]+2*((q[0]*q[3]-q[1]*q[2])*v[1]-(q[0]*q[2]+q[1]*q[3])*v[2]),
        #        (-q[0]**2+q[1]**2-q[2]**2+q[3]**2)*v[1]+2*((q[0]*q[1]-q[2]*q[3])*v[2]-(q[1]*q[2]+q[0]*q[3])*v[0]),
        #        (-q[0]**2+q[1]**2+q[2]**2-q[3]**2)*v[2]+2*((q[0]*q[2]-q[1]*q[3])*v[0]-(q[0]*q[1]+q[2]*q[3])*v[1])]
        #45 lookups and 36 multiplications
        #and when you remember that q[0]**2+q[1]**2+q[2]**2+q[3]**2=1, you can reduce to an equivalent form to the one on Wikipedia
        return [(2*(q[2]**2+q[3]**2)-1)*v[0]+2*((q[0]*q[3]-q[1]*q[2])*v[1]-(q[0]*q[2]+q[1]*q[3])*v[2]),
                (2*(q[1]**2+q[3]**2)-1)*v[1]+2*((q[0]*q[1]-q[2]*q[3])*v[2]-(q[1]*q[2]+q[0]*q[3])*v[0]),
                (2*(q[1]**2+q[2]**2)-1)*v[2]+2*((q[0]*q[2]-q[1]*q[3])*v[0]-(q[0]*q[1]+q[2]*q[3])*v[1])]
        #39 lookups and 33 multiplications (though of which 6 are doublings)
        #when rotating a million vectors by a million quaternions, original takes 6.034s, new takes 3.524s
         
    pixelAngle=math.tau/max(size)
    def rotateByScreen(angle,screenRotation):
        magnitude=math.hypot(*screenRotation)
        if magnitude==0:
            return angle
        else:
            magpi=magnitude*pixelAngle
            simagomag=math.sin(magpi)/magnitude #come and get your simagomags delivered fresh
            return quaternionMultiply([math.cos(magpi)]+[i*simagomag for i in screenRotation], angle)

    projectionMode=2
    def projectRelativeToScreen(position,radius=rad): #input differences from player position after rotation applied #radius only necessary for stereographic
        (x,y,z)=position
        if projectionMode==0: #weird
            (i,j)=[math.atan2(i, z) for i in (x,y)]
        elif projectionMode==1: #azimuthal equidistant
            h=math.atan2((x**2+y**2),z**2)/math.hypot(x,y)
            return (x*h*minSize+halfSize[0],y*h*minSize+halfSize[1],math.hypot(*position))
        else:
            magnitude=math.atan2(math.hypot(x,y),z) #other azimuthals
            if projectionMode==2: #Lambert equi-area (not to be taken to before 1772)
                magnitude=2*abs(math.sin(magnitude/2)) #formerly math.sqrt(math.sin(magnitude)**2+(math.cos(magnitude)-1)**2)
            elif projectionMode==3: #stereographic (trippy)
                if radius==0:
                    magnitude=1/math.tan(magnitude/2) #equivalent to math.sin(magnitude)/(1-math.cos(magnitude))
                else: #doesn't only find centre but uses fact that circles on the unit sphere of the camera's eye are projected to circles on the plane
                    h=math.hypot(x,y)
                    hh=math.hypot(*position)
                    offset=math.asin(radius/hh)
                    s0=1/math.tan((magnitude-offset)/2) #>mfw no math.cot
                    s1=1/math.tan((magnitude+offset)/2)
                    radius=s1-s0
                    magnitude=(s0+s1)/2
            direction=math.atan2(x,y)
        return (math.sin(direction)*magnitude*minSize+halfSize[0],math.cos(direction)*magnitude*minSize+halfSize[1],(math.hypot(*position) if projectionMode!=3 or radius==0 else radius))

    def findNodeScreenPositions():
        output=[n[0][0] for n in nodes]
        if dims==3:
            output=[rotateVector(lap(float.__sub__,n,cameraPosition[0]),cameraAngle[0]) for n in output]
            if perspectiveMode:
                output=lap(projectRelativeToScreen,output)
        return output

    gain=1
    angularVelocityConversionFactor=math.tau/FPS
    perspectiveMode=True
    colourMode=False
    oldSpace=False
    run=True
    while run:
        keys=pygame.key.get_pressed()
        doEvents()
        if perspectiveMode:
            cameraPosition=[lap(float.__add__,*cameraPosition),lap(float.__add__,cameraPosition[1],rotateVector([keys[pygame.K_d]-keys[pygame.K_a],keys[pygame.K_f]-keys[pygame.K_r],keys[pygame.K_w]-keys[pygame.K_s]],[-cameraAngle[0][0]]+cameraAngle[0][1:4]))]
        else:
            cameraPosition[0]=averageNode()
        space=keys[pygame.K_SPACE]
        if space==0!=oldSpace:
            colourMode^=True
        oldSpace=space
        if dims==3:
            if mouse.get_pressed()[0]:
                mouseChange=mouse.get_rel()
                mouseChange=(-mouseChange[1],mouseChange[0],0)
            else:
                mouse.get_rel() #otherwise it jumps
                mouseChange=(0,)*3
            arrowAccs=[keys[pygame.K_DOWN]-keys[pygame.K_UP],keys[pygame.K_LEFT]-keys[pygame.K_RIGHT],keys[pygame.K_q]-keys[pygame.K_e]] 
            magnitude=math.sqrt(sum(map(abs,arrowAccs)))
            if magnitude!=0:
                arrowAccs=[i/magnitude for i in arrowAccs]
            cameraAngle[1]=[(di+acc*gain*angularVelocityConversionFactor)/(1+drag) for di,acc in zip(cameraAngle[1],arrowAccs)]
            cameraAngle[0]=rotateByScreen(cameraAngle[0],[ci+mi for ci,mi in zip(cameraAngle[1],mouseChange)])
        nodeScreenPositions=findNodeScreenPositions()
        #print(nodeScreenPositions)
        renderOrder=conditionalReverse(perspectiveMode,[j for _, j in sorted((p[2],i) for i,p in enumerate(nodeScreenPositions))]) #perhaps replace with zip(*sorted((p[2],i) for i,p in enumerate(nodeScreenPositions)))[1] (not sure)
        physics()
        for sc,st,k,n in zip(nodeScreenPositions,stateWinningnesses,stateTransitions,nodes):
            for l in k:
                drawLine(sc[:2],nodeScreenPositions[l][:2],n[3][colourMode])
        if clickDone:
            mousePos=mouse.get_pos()
        for i,j,n,s in [(i,nodeScreenPositions[i],nodes[i],states[i]) for i in renderOrder]:
            sezi=2*((j[2] if projectionMode==3 else n[1][0]*minSize/j[2]) if perspectiveMode else n[1][0]) #different from size
            if perspectiveMode and sezi>minSize/64: #they will not notice if it is smaller, I hope
                renderBoard(s,[],False,sezi,[p-sezi/2 for p in j[:2]])
            else:
                drawShape(sezi,j[:2],n[3][colourMode],5)
                if clickDone and i!=boardLastPrinted and sum((ji-mi)**2 for ji,mi in zip(j,mousePos))<n[1][0]**2:
                    printBoard(states[i])
                    boardLastPrinted=i
    else: exit()
