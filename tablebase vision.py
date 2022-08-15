import math, random, os
imagePath=os.path.join(os.path.dirname(__file__),"Cburnett_pieces")
from sympy.utilities.iterables import subsets,combinations,multiset_permutations #generates permutations where some elements are identical, from https://stackoverflow.com/a/60252630
from itertools import groupby,starmap,chain,accumulate
try:
    from itertools import pairwise
except: #for non-3.10 users
    def pairwise(iterable):
        return zip(iterable[:-1],iterable[1:])
from functools import reduce
def sgn(n):
    return 1 if n>0 else -1 if n<0 else 0
def moddiv(a,b): #big endians get out ree
    return divmod(a,b)[::-1]
def zeromod(a,b):
    return --0-- a%b if a<0 else a%b #using the spaceship operator (https://bugs.python.org/issue43255#msg387248)
def zerodiv(a,b): #round up when negative (C99 does this by default)
    return --0-- a//b if a<0 else a//b
def conditionalReverse(reversal,toBe,torus=False):
    return ([toBe[0]]+list(reversed(toBe[1:])) if torus else reversed(toBe)) if reversal else toBe
def conditionalFlip(flip,toBe,transitive=False):
    return ((0 if toBe==0 else boardWidth-toBe) if transitive else boardWidth+~toBe) if flip else toBe #torus is only vertex-transitive manifold
def conditionalTranspose(transpose,x,y): #to prevent having to reiterate in each instance or use the less efficient x*boardWidth**(transpose)+y*boardWidth**(1^transpose) (to avoid having to allocate x and y to variables or recompute them)
    return x*boardWidth+y if transpose else y*boardWidth+x
def lap(func,*iterables): #Python 3 was a mistake
    return list(map(func,*iterables))
def minmax(iterable):
    return(min(iterable),max(iterable))

mode=int(input("Would you like chess (0), cellular automata (1) or Shut the Box (2)? "))

boardWidth=3
boardSquares=boardWidth**2
halfWidth=(boardWidth-1)//2
mediumHalfWidth=boardWidth//2
upperHalfWidth=(boardWidth+1)//2
centre=(boardSquares-1)/2
if boardWidth%2:
    centre=int(centre)
manifold=(0,0)
pieceNames=["empty","king","queen","rook","bishop","knight","pawn","nightrider"]
iterativePieces=[           2,      3,     4,                       7]
elementaryIterativePieces=[         3,     4,                       7] #may be optimisable further for nightriders because kings can't move to squares that are only in check after being moved to with them
pieceSymbols=[[" ","K","Q","R","B","N","P","M"],[" ","k","q","r","b","n","p","m"]] #nightriders are M because Wikipedia said to make them N and substitute knights for S (which is shallow and pedantic)
axisLetters=[l[:boardWidth] for l in [["a","b","c","d","e","f","g","h"],["1","2","3","4","5","6","7","8"]]]
def parseMaterial(materialString): #I think in the endgame material notation, the piece letters are all capitalised but the v isn't
    return [(pieceSymbols[0].index(j.upper()),c) for c,i in enumerate(materialString.split("v")) for j in (i[1:] if i[0].upper()=="K" else i)]
if mode==0:
    material=parseMaterial(input("Which endgame would you like? (ie. KRvK)"))
    def generateCombinations(material):
        #if any((6,i) in material for i in range(2)):
        pawns=[[j for j,m in enumerate(material) if m==(6,i)] for i in range(2)]
        if pawns==[[],[]]:
            return {c for m in range(len(material)+1) for c in combinations(material,m)} #subsets(material)
        else:
            promotionses=[[],[]] #we wants it
            for o,p in enumerate(pawns):
                promotions=[6 for i in range(len(p))]
                arm=0 #like the other use of this variable, it is an arm, but not through space
                while arm<len(p):
                    promotions[:arm]=[promotions[arm] for i in range(arm)] #inapplicable on first loop but in subsequent ones is as though it is at the end except guaranteed not to be out of bounds
                    arm=0
                    promotionses[o].append(list(promotions))
                    promotions[0]-=1
                    while promotions[arm]==1:
                        arm+=1
                        if arm<len(promotions) and promotions[arm]>1:
                            promotions[arm]-=1 #would set to 6 if it were standard counting in a base, but this way prevents permutations that reiterate combinations
                        else:
                            break
            promotionses=[[[(t,i) for t in o] for o in p] for i,p in enumerate(promotionses)]
            print(promotionses)
            promotionseses=([i+j for i in promotionses[0] for j in promotionses[1]] if promotionses[1] else promotionses[0]) if promotionses[0] else promotionses[1] #we needs it
            print(promotionseses)
            return {c for p in [[next(i) if m[0]==6 else m for m in material] for i in map(iter,promotionseses)] for m in range(len(material)+1) for c in combinations(p,m)}
    turnwise=True #turnwise symmetry reduction (disable if you are using state transition diagram and would like to preserve the property that moving across n edges ^s your turn with n, enable if you like efficiency (enabled by default because I like efficiency))
    def reduceTurnwise(combinations): #because KPvKP can become both KNvK and KvKN
        return {(c,(2 if sorted(c)==sorted(i) else 1 if i in combinations else 0)) for c,i in ((c,tuple((i,1-j) for (i,j) in c)) for c in combinations) if i not in combinations or sorted(c)<=sorted(i)} if turnwise else {(c,False) for c in combinations} #inelegant but this part doesn't run very much
    combinations=reduceTurnwise(generateCombinations(material))
    print("combinations:",combinations) #first element is combination's piece contents, second is whether it is unique to a single side

def generatePermutations(material,squares):
    return multiset_permutations(material+((0,0),)*squares)

def checkTranslationTuple(position,x,y):
    return all(m or 0<=moddiver+z<boardWidth for m,moddiver,z in zip(manifold,moddiv(position,boardWidth),(x,y))) #I wonder what mod diving would be like (I imagine like regular diving but more modular)
          #(manifold[0] or 0<=position%boardWidth+x<boardWidth and manifold[1] or 0<=position//boardWidth+y<boardWidth)
def flattenTranslation(x,y):
    return ( ( conditionalFlip(y//boardWidth%2,x%boardWidth)+boardWidth*conditionalFlip(x//boardWidth%2,y%boardWidth)
              if manifold[0]==2 else
               x+boardWidth*(y%boardWidth)
              if manifold[0] else
               conditionalFlip(y//boardWidth%2,x%boardWidth)+boardWidth*(y%boardWidth))
            if manifold[1]==2 else
             ( x%boardWidth+boardWidth*(conditionalFlip(x//boardWidth%2,y%boardWidth))
              if manifold[0]==2 else
               x%boardWidth+boardWidth*(y%boardWidth)
              if manifold[0] else
               x+boardWidth*(y%boardWidth))
            if manifold[1] else
             ( x%boardWidth+conditionalFlip(x//boardWidth%2,boardWidth*y)
              if manifold[0]==2 else
               x%boardWidth+boardWidth*y
              if manifold[0] else
               x+boardWidth*y))
def checkTranslation(position,displacement): #Python recognises all nonzero ints as True, and Möbius scrolling doesn't matter for verifying whether a displacement is legal (the other axis is flipped but its out-of-boundness is the same)
    return ( manifold[0] or 0<=position%boardWidth+zeromod(displacement,boardWidth)<boardWidth  #True #torus/Klein/real projective
                                                                                        #if manifold[0] else
                                                                                         #0<=position%boardWidth+zeromod(displacement,boardWidth)<boardWidth) #vertically-scrolling cylinder/Möbius strip
            if manifold[1] else
             0<=position//boardWidth+zerodiv(displacement,boardWidth)<boardWidth #horizontally-scrolling cylinder/Möbius strip
            if manifold[0] else
             0<=position+displacement<boardSquares and 0<=position%boardWidth+zeromod(displacement,boardWidth)<boardWidth) #square

def translateTuple(position,x,y):
    return(None if not checkTranslationTuple(position,x,y) else #for cellular automata mode
            ( conditionalFlip((position//boardWidth+y)//boardWidth%2,(position+x)%boardWidth)+conditionalFlip((position+x)//boardWidth%2,position//boardWidth+y)*boardWidth #real projective plane
             if manifold[0]==2 else
              conditionalFlip((position//boardWidth+y)//boardWidth%2,(position+x)%boardWidth)+(position//boardWidth+y)%boardWidth*boardWidth #vertical Klein bottle
             if manifold[0] else
              conditionalFlip((position//boardWidth+y)//boardWidth%2,position%boardWidth+x)+(position//boardWidth+y)%boardWidth*boardWidth) #vertical Möbius strip
           if manifold[1]==2 else
            ( (position+x)%boardWidth+conditionalFlip((position+x)//boardWidth%2,(position//boardWidth+y)%boardWidth)*boardWidth #horizontal Klein bottle
             if manifold[0]==2 else
              (position+x)%boardWidth+(position//boardWidth+y)%boardWidth*boardWidth #torus
             if manifold[0] else
              (position%boardWidth+x)+(position//boardWidth+y)%boardWidth*boardWidth) #vertical cylinder
           if manifold[1] else
            ( (position+x)%boardWidth+conditionalFlip((position+x)//boardWidth%2,position//boardWidth+y)*boardWidth #horizontal Möbius strip
             if manifold[0]==2 else
              (position+x)%boardWidth+(position//boardWidth+y)*boardWidth #horizontal cylinder
             if manifold[0] else
              position+x+y*boardWidth)) #square

#abandon hope, all ye who enter here
#(it is unclear in some cases whether, for instance, a (-1,1) displacement on a 3*3 horizontal board encoded to a change by 2 is meaning to move 2 cells rightwards or one upwards and one leftwards)
'''def translate(position,displacement): #manifold are 0 for bounded board behaviour, 1 for toroidal, 2 for Möbius
    return(   conditionalFlip(zerodiv(position//boardWidth+zerodiv(displacement,boardWidth),boardWidth)%2,(position+displacement)%boardWidth)+conditionalFlip(zerodiv(position%boardWidth+displacement%boardWidth,boardWidth),(position//boardWidth+zerodiv(displacement,boardWidth))%boardWidth)*boardWidth #real projective plane
             if manifold[0]==2 else
              conditionalFlip(zerodiv(position//boardWidth+zerodiv(displacement,boardWidth),boardWidth)%2,(position+displacement)%boardWidth)+((position//boardWidth+zerodiv(displacement,boardWidth))%boardWidth)*boardWidth #vertical Klein bottle if manifold[0] else vertical Möbius strip (however they're computed the same (the inputs are up to you to get right (with checkTranslation)))
           if manifold[1]==2 else
            ( (position+displacement)%boardWidth+conditionalFlip(zerodiv(position%boardWidth+zeromod(displacement,boardWidth),boardWidth),position//boardWidth+zerodiv(displacement,boardWidth))%boardWidth*boardWidth #horizontal Klein bottle
             if manifold[0]==2 else
              (position+displacement)%boardWidth+(position//boardWidth+zerodiv(displacement,boardWidth))%boardWidth*boardWidth #torus
             if manifold[0] else
              ((position%boardWidth+displacement%boardWidth)+((position//boardWidth*boardWidth+displacement)//boardWidth)%boardWidth*boardWidth))%boardSquares #vertical cylinder
           if manifold[1] else
            ( (position+displacement)%boardWidth+conditionalFlip(zerodiv(position%boardWidth+zeromod(displacement,boardWidth),boardWidth),position//boardWidth+zerodiv(displacement,boardWidth))*boardWidth #horizontal Möbius strip
             if manifold[0]==2 else
              (position+displacement)%boardWidth+((position+displacement)//boardWidth+((position-position%boardWidth)-(position+displacement-(position+displacement)%boardWidth))//boardWidth)*boardWidth #horizontal cylinder
             if manifold[0] else
              position+displacement)) #square'''
    #closed-form version (without some special-case optimisations)
    #return conditionalFlip((manifold[0]==2) and ((position//boardWidth+displacement//boardWidth)//boardWidth)%2,(position+displacement)%boardWidth)+conditionalFlip(manifold[1]==2 and ((position%boardWidth+displacement%boardWidth)//boardWidth),(position//boardWidth+displacement//boardWidth)%boardWidth)*boardWidth
flatTranslations=False #a constant source of pain to me
increments=(tuple((p,p==1,(p*boardWidth**di if flatTranslations else list(conditionalReverse(di,(p,0))))) for p in range(-1,3,2) for di in range(2)),
            tuple(((x,y),(x==1,y==1),(x+y*boardWidth if flatTranslations else (x,y))) for x in range(-1,3,2) for y in range(-1,3,2)),
            tuple((conditionalReverse(s,(x,y)),conditionalReverse(s,(x==1,y==2)),(conditionalTranspose(s,x,y) if flatTranslations else list(conditionalReverse(s,(x,y))))) for x in range(-1,3,2) for y in range(-2,6,4) for s in range(2)))
def findPieceMoves(boardState,position,piece,attackMask=False,moveTuples=False): #outputs list of squares to which piece can travel, moveTuples outputs tuple of piece position, destination and promotion type if it's a pawn
    if piece[0]==0:
        return []
    elif piece[0]==2:
        return [j for i in range(3,5) for j in findPieceMoves(boardState,position,(i,piece[1]),attackMask,moveTuples)]
    else:
        spatial=moddiv(position,boardWidth)
        if piece[0]==1:
            moves=(precomputedKingMoves[position] if kingMovesPrecomputed else [translateTuple(position,x,y) for y in (manifold[1] or position>=boardWidth or mode==1)*[-1]+[0]+[1]*(manifold[1] or position<boardSquares-boardWidth or mode==1) for x in (manifold[0] or spatial[0]!=0 or mode==1)*[-1]+(y!=0 or mode==1)*[0]+[1]*(manifold[0] or spatial[0]!=boardWidth-1  or mode==1)])
        elif piece[0] in elementaryIterativePieces:
            moves=[]
            for i,(p,b,n) in enumerate(increments[elementaryIterativePieces.index(piece[0])]): #indice, (polarity, boolean polarity,increment)
                #armSpatial=(spatial[i%2] if piece[0]==3 else spatial)
                for j in range(1,1+((boardWidth*manifold[i%2] if manifold[i%2] else conditionalFlip(b,spatial[i%2]))
                               if piece[0]==3 else
                                ( ( boardWidth*max(manifold)
                                   if manifold[1] else
                                    conditionalFlip(b[1],spatial[1])
                                 if manifold[0] else
                                  ( conditionalFlip(b[0],spatial[0])
                                   if manifold[1] else
                                    min(conditionalFlip(bi,s) for s,bi in zip(spatial,b)))))
                               if piece[0]==4 else
                                ( ( manifold[i%2]*boardWidth #(periodicity is always dependent on dimension of 1-step increment)
                                   if manifold[1-i%2] else
                                    conditionalFlip(b[1],spatial[1])//abs(p[1])) #now I am oblique for lack of symmetry
                                 if manifold[i%2] else
                                  ( conditionalFlip(b[0],spatial[0])//abs(p[0])
                                   if manifold[1-i%2] else
                                    min(conditionalFlip(bi,s)//abs(pi) for s,pi,bi in zip(spatial,p,b)))))):
                    '''if piece[0]==3:
                        armSpatial+=p
                    else:
                        armSpatial=map(int.__add__,armSpatial,p)'''
                    arm=translate(position,j*n) if flatTranslations else translateTuple(position,j*n[0],j*n[1]) #cannot increment in for loop line because arm doesn't remember own change in orientation when Möbiused
                    if arm!=position:
                        moves.append(arm)
                    if boardState[arm][0]!=0:
                        #if boardState[arm][1]!=piece[1]: #formerly moves.append(arm) was conditional here, but capturing own colour isn't allowed by stateMoves generator and this way kings won't be able to take pieces defended by iterative pieces (which will be useful if I ever do implement pin masks and such instead of the current use of dict presence) and check detection is done properly
                        break
        elif piece[0]==5:
            moves=precomputedKnightMoves[position] if knightMovesPrecomputed else [translateTuple(position,xPolarity*(2-skewedness),yPolarity*(1+skewedness)) for skewedness in range(2) for xPolarity in range(-1,3,2) if manifold[0] or conditionalFlip(xPolarity==1,spatial[0])>1-skewedness for yPolarity in range(-1,3,2) if manifold[1] or conditionalFlip(yPolarity==1,spatial[1])>skewedness]
                                                                                 #[translateTuple(position,*conditionalReverse(skewedness,(xPolarity,yPolarity))) for skewedness in range(2) for xPolarity in range(-2,6,4) if (boardWidth+~spatial[skewedness] if xPolarity==2 else spatial[skewedness])>1 for yPolarity in range(-1,3,2) if (boardWidth+~spatial[1^skewedness] if yPolarity==1 else spatial[1^skewedness])>0] (conditionalReverse inlined) is 25% faster for bounded boards
        elif piece[0]==6:
            vertical=(-1)**piece[1] #>mfw no e**(i*pi*piece[1])
            moves=([translateTuple(position,-1,vertical)]*(manifold[0] or 0<spatial[0])+[translateTuple(position,1,vertical)]*(manifold[0] or spatial[0]<boardWidth-1) if attackMask==1 else [displace(position,vertical+i) for i in range(-1,2,1) if (manifold[0] or 0<=spatial[0]+i<boardWidth) and (boardState[displace(position,vertical+i)][0]==0)^i]+[displace(position,2*vertical)]*(conditionalFlip(piece[1],spatial[1])==1 and manifold[1] or boardWidth>3 and boardState[displace(position,vertical)]==boardState[displace(position,2*vertical)][0]==0)) if manifold[1] or conditionalFlip(not piece[1],spatial[1])>0 else [] #it is inefficient but I like the XOR
    return moves if mode==1 and (piece[0]==1 and not kingMovesPrecomputed or piece[0]==5 and not knightMovesPrecomputed) else ({(position,m,i) for m in moves for i in range(2,6)} if piece[0]==6 and conditionalFlip(not piece[1],spatial[1])==1 else {(position,m) for m in moves}) if moveTuples else set(moves)
def precomputeMoves(piece):
    return tuple(findPieceMoves(((0,0),)*boardSquares,i,(piece,0)) for i in range(boardSquares))
kingMovesPrecomputed=knightMovesPrecomputed=False
precomputedKingMoves=precomputeMoves(1)
precomputedKnightMoves=precomputeMoves(5)
kingMovesPrecomputed=knightMovesPrecomputed=True

def firstDisparity(both):
    return next((a[0]*(1-2*a[1])-b[0]*(1-2*b[1]) for a,b in both if a!=b),0)<0
def axialDisparity(state,axis,flippings=(False,)*3,reverse=True): #the intended board flipping is reversed to find the index of (the square in the intended board) in the current board ((1,0,1) and (0,1,1) are the only flipping tuples that are each other's inverses instead of their own)
    return False if axis==-1 else firstDisparity(
            ( ((state[conditionalFlip(flippings[flippings[2]&reverse],i)+conditionalFlip(flippings[1^flippings[2]&reverse],j)*boardWidth] for i,j in ((x,y),(y,x))) for x in range(1,boardWidth) for y in range(x))
             if axis==2 else
              ((state[conditionalTranspose(axis^flippings[2],conditionalFlip(i,x,manifold[axis]==1 and manifold[1^axis]!=2),conditionalFlip(flippings[1^flippings[2]&reverse],y,manifold[1^axis]==1 and manifold[axis]!=2))] for i in range(2)) for y in range(boardWidth) for x in (range(1,mediumHalfWidth+1) if manifold[axis]==1 and manifold[1^axis]!=2 else range(halfWidth))))
          )^flippings[2 if axis==2 else axis^flippings[2]&reverse]
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
            ((state[ ( ( y+conditionalFlip(1^i,x)*boardWidth
                        if flippings[0]^reverse else
                         (boardWidth+~y)+conditionalFlip(i,x)*boardWidth)
                      if flippings[0]^flippings[1] else
                       ( (boardWidth+~y)+conditionalFlip(1^i,x)*boardWidth
                        if flippings[0] else
                         y+conditionalFlip(i,x)*boardWidth))
                    if flippings[2]^axis else #axis either 0 or 1
                    ( (  conditionalFlip(1^i,x)+(boardWidth+~y)*boardWidth
                        if flippings[0] else
                         conditionalFlip(i,x)+(boardWidth+~y)*boardWidth)
                      if flippings[1] else
                       ( conditionalFlip(1^i,x)+y*boardWidth
                        if flippings[0] else
                         conditionalFlip(i,x)+y*boardWidth))
                    ] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))''' #x and y actually only mean first and second iterables
    #old version (from when it was only a special-case exception for x scanning with uncertain y):
    #return firstDisparity(((state[conditionalTranspose(i,x,y)] for i in range(2)) for x in range(boardWidth) for y in range(x)) if axis==2 else ((state[conditionalTranspose(axis,conditionalFlip(i,x),conditionalFlip(suspicious,y))] for i in range(2)) for x in range(halfWidth) for y in range(boardWidth)))

def positionReflect(position,axis):
    return boardWidth+~position+position//boardWidth*boardWidth*2 if axis==0 else position%boardWidth+(boardWidth+~position//boardWidth)*boardWidth if axis==1 else position//boardWidth+(position%boardWidth)*boardWidth if axis==2 else position

def compoundPositionReflect(position,axes,reverse=False): #some are probably reducible further (depending on whether floor division or modulo is more efficient, but also probably regardless)
    return ( ( ( ( (position//boardWidth+(0 if position%boardWidth==0 else boardWidth-position%boardWidth)*boardWidth if reverse else (0 if position//boardWidth==0 else boardWidth-position//boardWidth)+position%boardWidth*boardWidth)
                  if manifold[reverse]==1 and manifold[1^reverse]!=2 else
                   (position+1)*boardWidth+~((boardSquares+1)*(position//boardWidth)))
                if axes[reverse] else
                 ( ((0 if position//boardWidth==0 else boardWidth-position//boardWidth)+0 if position%boardWidth==0 else boardWidth-position%boardWidth*boardWidth if reverse else position//boardWidth+(position%boardWidth)*boardWidth)
                  if manifold[1^reverse]==1 and manifold[reverse]!=2 else
                   boardWidth*(boardWidth+~position)+(1+boardSquares)*(position//boardWidth)))
              if axes[0]^axes[1] else
               ( ( ((0 if position//boardWidth==0 else boardWidth-position//boardWidth)+(0 if position%boardWidth==0 else boardWidth-position%boardWidth)*boardWidth if manifold[1^reverse]==1 else position//boardWidth+(0 if position%boardWidth==0 else boardWidth-position%boardWidth)*boardWidth)
                  if manifold[reverse]==1 and manifold[1^reverse]!=2 else
                   ((0 if position//boardWidth==0 else boardWidth-position//boardWidth)+(boardWidth+~position%boardWidth)*boardWidth if manifold[1^reverse]==1 and manifold[reverse]!=2 else (1-boardSquares)*~(position//boardWidth)-position*boardWidth))
                if axes[0] else
                 position*boardWidth-(boardSquares-1)*(position//boardWidth))) #position//boardWidth+position%boardWidth*boardWidth=position*boardWidth-(boardSquares-1)*position//boardWidth
            if axes[2] else
             ( ( ( (0 if position==0 else boardWidth-position if position//boardWidth==0 else boardSquares-position if position%boardWidth==0 else boardSquares-boardWidth-position)
                  if manifold[1]==1 else
                   (0 if position%boardWidth==0 else boardWidth-position%boardWidth)+(boardWidth+~(position//boardWidth))*boardWidth) if manifold[0]==1 and manifold[1]!=2 else ((boardWidth+~position%boardWidth+(boardWidth-position//boardWidth)*boardWidth) if manifold[1]==1 and manifold[0]!=2 else boardSquares+~position) #(boardWidth-position//boardWidth)*boardWidth+(boardWidth-position%boardWidth)=boardSquares+boardWidth-position
                if axes[0] else
                 ( (position if position//boardWidth==0 else position+boardWidth*(boardWidth-(2*(position//boardWidth))))
                  if manifold[1]==1 and manifold[0]!=2 else
                   position+boardWidth*(boardWidth+~(2*(position//boardWidth)))))
              if axes[1] else
               ( ( (position if position%boardWidth==0 else boardWidth*(1+2*(position//boardWidth))-position)
                  if manifold[0]==1 and manifold[1]!=2 else
                   boardWidth*(1+2*(position//boardWidth))+~position) #position=position%boardWidth+position//boardWidth*boardWidth, so position//boardWidth*boardWidth=position-position%boardWidth, so boardWidth+~position%boardWidth+position//boardWidth*boardWidth=boardWidth+~position%boardWidth+position-position%boardWidth=boardWidth+~2*position%boardWidth+position=boardWidth+~(2*position%boardWidth)+position=~position+boardWidth*(1+2*position//boardWidth)
                if axes[0] else
                 position)))
    #equivalent to (but more efficient (and supporting more topological manifolds) than)
    #return reduce(positionReflect,conditionalReverse(reverse,*zip(*[(i,(m==1 and r!=2)) for i,(a,m,r) in enumerate(zip(axes,manifold,reverse(manifold))) if a])),position)
def boardReflect(board,axis):
    #return tuple(board[positionReflect(i,axis)] for i in range(boardSquares)) #old one
    return board if axis==-1 else tuple((x for y in range(boardWidth) for x in reversed(board[y*boardWidth:(y+1)*boardWidth])) if axis==0 else (x for y in range(boardWidth,0,-1) for x in board[(y-1)*boardWidth:y*boardWidth]) if axis==1 else (x for y in range(boardWidth) for x in board[y:y+boardSquares:boardWidth]))
def compoundReflect(board,axes):
    return board if axes==(0,0,0) else tuple(x for y in conditionalReverse(axes[not axes[2]],range(boardWidth),manifold[1]) for x in conditionalReverse(axes[axes[2]],(board[y:y+boardSquares:boardWidth] if axes[2] else board[y*boardWidth:(y+1)*boardWidth]),manifold[0])) #equivalent to (but faster than)
    #return reduce(boardReflect,[i for i,a in enumerate(axes) if a],board)
def axialScroll(board,axis,distance): #moves reference frame right/upwards, not board, because more elegant this way
    return board if distance==0 else ( ( tuple(chain.from_iterable(conditionalReverse(distance<0,board[i*boardWidth:(i+1)*boardWidth]) for i in range(distance%boardWidth,boardWidth)))+tuple(chain.from_iterable(conditionalReverse(distance>0,board[i*boardWidth:(i+1)*boardWidth]) for i in range(distance%boardWidth)))
                                        if manifold[1]==2 else
                                         tuple(chain.from_iterable(board[i*boardWidth:(i+1)*boardWidth] for i in chain(range(distance,boardWidth),range(distance)))))
                                      if axis else
                                       ( tuple(chain.from_iterable((i[distance:]+j[:distance] if distance>0 else j[distance:]+i[:distance]) for i,j in zip((board[i*boardWidth:(i+1)*boardWidth] for i in range(boardWidth)),(board[-i*boardWidth:-(i+1)*boardWidth:-1] for i in range(boardWidth)))))
                                        if manifold[0]==2 else
                                         tuple(chain.from_iterable(i[distance:]+i[:distance] for i in (board[i*boardWidth:(i+1)*boardWidth] for i in range(boardWidth))))))
def scroll(board,x,y): #to be optimised
    return( None
           if manifold==(2,2) else
            None
           if manifold==(2,1) else
            None
           if manifold==(1,2) else
            tuple(chain(chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y,boardWidth)),chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y)))) #tuple(chain(chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y,boardWidth)),chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y)))) #tuple(chain(chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y,boardWidth)),chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in range(y)))) #tuple(chain.from_iterable(state[j*boardWidth+x:(j+1)*boardWidth]+state[j*boardWidth:j*boardWidth+x] for j in chain(range(y,boardWidth),range(y)))) #[state[i+j*boardWidth] for j in chain(range(y,boardWidth),range(y)) for i in chain(range(x,boardWidth),range(x))]
           if manifold==(1,1) else
            axialScroll(board,False,x)
           if manifold[0]!=0 else
            axialScroll(board,True,y)
           if manifold[1]!=0 else
            board) #equivalent to axialScroll(axialScroll(board,False,x),True,y) (but ignores scrolls in bounded axes)

symmetryReduction=(mode!=2 and input("Would you like reduction by "+("thirty-two" if manifold==(2,2) else "four" if (2,1)!=manifold!=(1,2) and manifold[0]!=manifold[1] else "eight")+"fold symmetry? (y/n)")=="y") #not mentioning vertex transitivity
transitivityReduction=symmetryReduction #they will probably want it
combinationIndices=[0]
combinationTurnwises=[]
states=[] #list of all legal states (permutations of pieces) as lists of piece types and colours (0 if no piece)
stateTurns=[]
stateSquareAttacks=[]
stateChecks=[]
Tralse=(True+False)/2 #very suspicious
Fruse =(True+3*False)/4 #not very suspicious
Trulse=(3*True+False)/4 #extremely suspicious
#stateKingPositions=[]
#stateKingLinesOfSymmetry=[]
leftHalf=[x+y*boardWidth for y in range(boardWidth) for x in range(upperHalfWidth)]
diagonalHalf=[x+y*boardWidth for x in range(boardWidth) for y in range(x+1)]

def theStates(i=None):
    def stateTuple(i):
        return tuple(bool(i>>j&1) for j in range(boardSquares if mode==1 else flaps))
    return((states if i==None else states[i]) if mode==0 or mode==1 and symmetryReduction else (tuple(map(stateTuple,range(2**(boardSquares if mode==1 else flaps)))) if i==None else stateTuple(i)))
if mode==0:
    def generateKingPositions(pawns):
        whiteKingRange=(0,) if manifold==(1,1) and transitivityReduction else (leftHalf if pawns else [x+y*boardWidth for x in range(upperHalfWidth) for y in range(x+1 if manifold[0]==manifold[1] else upperHalfWidth)]) if symmetryReduction else range(boardSquares)
        #print("permutation lengths (should be "+str(boardSquares)+"):",map(len,piecePermutations))
        kingPositions=[(i,j) for i,iKingMoves in zip(whiteKingRange,[findPieceMoves(((0,0),)*boardSquares,i,(1,0)) for i in whiteKingRange]) for j in ((x+y*boardWidth for x in range(1,mediumHalfWidth+1) for y in range(x)) if manifold==(1,1) and transitivityReduction else ((whiteKingRange if i==centre else leftHalf if i%boardWidth==(boardWidth-1)/2 else diagonalHalf if i%boardWidth==i//boardWidth and pawns==0 else range(boardSquares)) if symmetryReduction else range(boardSquares))) if not (i==j or j in iKingMoves)]
        kingStates=[tuple((int(k==i or k==j),int(k==j)) for k in range(boardSquares)) for i,j in kingPositions] #each square in each state list (in the list of them) is a list of the piece and its colour
        kingLineOfSymmetry=[2 if i%boardWidth==i//boardWidth and j%boardWidth==j//boardWidth and manifold[0]==manifold[1] and not pawns else (0 if (j%boardWidth==0 or boardWidth%2==0 and j%boardWidth==mediumHalfWidth if manifold[0]==1 and manifold[1]!=2 else i%boardWidth==j%boardWidth==halfWidth) else 1 if (j//boardWidth==0 or boardWidth%2==0 and j//boardWidth==mediumHalfWidth if manifold[1]==1 and manifold[0]!=2 else i//boardWidth==j//boardWidth==halfWidth) and not pawns else -1) if boardWidth%2==1 else -1 for i,j in kingPositions] #-1 for no symmetry, 0 for x, 1 for y, 2 for diagonal
        return (kingPositions,kingStates,kingLineOfSymmetry)
    
    anyPawns=any(p[0]==6 for c in combinations for p in c[0])
    
    allKingPositions=(generateKingPositions(False),)+(generateKingPositions(True),)*anyPawns
    
    def constructState(k,m):
        return (l if l[0]==1 else next(m) for l in k)
    def setKingPawnness(pawns):
        global kingPositions
        global kingStates
        global kingLineOfSymmetry
        (kingPositions,kingStates,kingLineOfSymmetry)=allKingPositions[pawns]
    def changeTurn(s):
        return tuple((0,0) if q[0]==0 else q if q[0]==1 else (q[0],1-q[1]) for q in s)
    def attackSet(state,kings=True):
        return {(m,q[1]) for i,q in enumerate(state) for m in findPieceMoves(state,i,q,True) if q!=6 or (m-i)%boardWidth!=0 and (kings or q[0]!=1)} #if kings false, they are to be added subsequently
    def attackMask(attackSet,kings=False,kingPositions=[0,0],invert=False):
        attacks=[[(k,l) in attackSet for l in conditionalReverse(invert,range(2))] for k in range(boardSquares)]
        if kings:
            for i,p in enumerate(kingPositions):
                for m in precomputedKingMoves[p]:
                    attacks[m][i]=True
        return attacks
    
    def conditions(s,l):
        return (not symmetryReduction or l==-1 or not axialDisparity(s,l)) and not (pawns and 6 in s[:boardWidth]+s[boardSquares-boardWidth:])
    for ci,(c,s) in enumerate(combinations):
        piecePermutations=tuple(generatePermutations(c,boardSquares-2-len(c))) #leaving as generator expression causes many problems
        if ci==0:
            pawns=any(p[0]==6 for p in c)
            setKingPawnness(pawns)
        elif any(p[0]==6 for p in c)!=pawns:
            pawns^=True
            setKingPawnness(pawns) #pawns prevent eightfold symmetry (I hate them so much)
        '''playerPieces=[[],[]]
        for i in c:
            playerPieces[i[1]].append(i[0])
            #playerPieces[i[1]].insert(next((j for j,k in enumerate(playerPieces[i[1]]) if i[0]<k),len(playerPieces[i[1]])),i[0]) #would be more elegant but changes O(n*log(n)) to O(n**2) (should use binary search instead)
        combinationTurnwises.append(sorted(playerPieces[0])==sorted(playerPieces[1]))''' #not very elegant (now replaced with the second element of each combination tuple)
        tralseToday=turnwise and s==2 #combinationTurnwises[-1] #it's going to happen soon (but not today)
        aPoStaLin=((attackSet(i,tralseToday),p,i,l) for p,i,l in ((p,tuple(constructState(k,m)),l) for p,k,l in zip(kingPositions,kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations))) #portmanteau for "attack, position, state, line"
        (newStates,newTurns,newSquareAttacks,newChecks)=zip(*(((i,Tralse,attackMask(a,True,p),((p[0],1) in a)) for a,p,i,l in aPoStaLin if ((p[1],0) not in a) and conditions(i,l))
                                                                    #not tuple(boardReflect(constructState(k,m)) if l!=-1 and axialDisparity(constructState(k,m),l) else tuple(constructState(k,m)) for k,l in zip(kingStates,kingLineOfSymmetry) for m in map(iter,piecePermutations)) because the reflected (reduced) one will appear anyway
                                                        if tralseToday else
                                                        chain.from_iterable(((                        i,    (False if s==0 else Fruse),             attackMask(a,True,p     ),   ((p[0],1) in a)),)*((p[1],0) not in a)+
                                                                            ((boardReflect(changeTurn(i),l),(True if s==0 else Trulse),boardReflect(attackMask(a,True,p,True),l),((p[0],0) in a)),)*((p[1],1) not in a) for a,p,i,l in aPoStaLin if conditions(i,l))))
        states+=newStates
        stateTurns+=newTurns
        stateSquareAttacks+=newSquareAttacks
        stateChecks+=newChecks
        combinationIndices.append(len(states))
    def printBoard(board):
        print("".join(["".join(("_" if letter==" " else letter+'\u0332') if (i+b)%2==0 else letter for i,letter in enumerate([pieceSymbols[s[1]][s[0]] for s in board[(b-1)*boardWidth:b*boardWidth]]))+"\n" for b in range(boardWidth,0,-1)])+"\033["+str(boardWidth-1)+"B",end="") #ANSI escape sequences
                                            #from https://stackoverflow.com/a/71034895      #light squares underlined
    def FEN(board,turn=0):
        return "/".join("".join((str(len(list(q))) if l==" " else "".join(q)) for l,q in groupby(pieceSymbols[s[1]][s[0]] for s in board[b*boardWidth:(b+1)*boardWidth])) for b in range(boardWidth-1,-1,-1))+" "+("b" if turn else "w")+" - - 0 1" #castling, en passant, moves from zeroing and moves from origin state (indice beginning at 1) not yet supported
    
    def isSymmetry(state,kingPositions): #only for those with kings eightfolded already
        if all(i%boardWidth==halfWidth for i in kingPositions) and boardWidth%2==1:
            return axialDisparity(state,0)
        if all(i%boardWidth==i//boardWidth for i in kingPositions):
            return axialDisparity(state,2)
        return False

    def symmetry(state,reflectionMode=0): #reflection modes: 0 reduces by eightfold, 1 reduces and reports reflections, 2 only reports, to apply list of reflections use compoundReflect()
        if symmetryReduction:
            kingPositions=[state.index((1,i)) for i in range(2)]
            if manifold!=(0,0):
                offset=moddiv(kingPositions[0],boardWidth)
                reflections=[False]*3
                for i,(o,m,r) in enumerate(zip(offset,manifold,reversed(manifold))):
                    if (m==1 or m==2) and r!=2:
                        state=axialScroll(state,i,o)
                        kingPositions=[p%boardWidth+(p//boardWidth-o)%boardWidth*boardWidth if i else (p%boardWidth-o)%boardWidth+p//boardWidth*boardWidth for p in kingPositions]
                        reflections.append(o)
                    else:
                        reflections.append(0)
                #if boardWidth%2==0 and kingPositions[1]==(boardSquares+boardWidth)//2:
                    #will have to fix cellular automaton reduction algorithm to use here (this is the same problem, axial disparities are used as not tiebreakers but the basis of reduction)
                #else:
                if not (boardWidth%2==0 and kingPositions[1]==(boardSquares+boardWidth)//2):
                    #print("\ni")
                    #printBoard(state)
                    kingPositions=moddiv(kingPositions[1],boardWidth) #this part currently only for toruses (not yet single-axis vertex transitivity)
                    reflections[:3]=( [axialDisparity(state,0,[False,(kingPositions[1]>mediumHalfWidth),False]),(kingPositions[1]>mediumHalfWidth),False]
                                     if kingPositions[0]==0 or boardWidth%2==0 and kingPositions[0]==mediumHalfWidth else
                                      [(kingPositions[0]>mediumHalfWidth),axialDisparity(state,1,[(kingPositions[0]>mediumHalfWidth),False,False]),True]
                                     if kingPositions[1]==0 or boardWidth%2==0 and kingPositions[1]==mediumHalfWidth else
                                      [(kingPositions[0]>mediumHalfWidth)]*2+[axialDisparity(state,2,[(kingPositions[0]>mediumHalfWidth)]*2+[False])]
                                     if manifold[0]==manifold[1] and kingPositions[0]==kingPositions[1] else
                                      ([True,False] if kingPositions[0]>mediumHalfWidth else [False,True])+[axialDisparity(state,2,([True,False,False] if kingPositions[0]>mediumHalfWidth else [False,True,False])+[False])]
                                     if manifold[0]==manifold[1] and kingPositions[0]==boardWidth-kingPositions[1] else
                                      [(kingPositions[0]>mediumHalfWidth),(kingPositions[1]>mediumHalfWidth),(conditionalFlip(kingPositions[0]>mediumHalfWidth,kingPositions[0])<conditionalFlip(kingPositions[1]>mediumHalfWidth,kingPositions[1]))])
            else:
                if boardWidth%2==1 and kingPositions[0]==centre:
                    kingPositions=moddiv(kingPositions[1],boardWidth)
                    reflections=( [axialDisparity(state,0,[False,(kingPositions[1]>halfWidth),False]),(kingPositions[1]>halfWidth),False]
                                 if kingPositions[0]==halfWidth else
                                  [(kingPositions[0]>halfWidth),axialDisparity(state,1,[(kingPositions[0]>halfWidth),False,False]),True]
                                 if kingPositions[1]==halfWidth else
                                  [(kingPositions[0]>halfWidth)]*2+[axialDisparity(state,2,[(kingPositions[0]>halfWidth)]*2+[False])]
                                 if kingPositions[0]==kingPositions[1] else
                                  ([True,False] if kingPositions[0]>halfWidth else [False,True])+[axialDisparity(state,2,([True,False,False] if kingPositions[0]>halfWidth else [False,True,False])+[False])]
                                 if kingPositions[0]==boardWidth+~kingPositions[1] else
                                  [(kingPositions[0]>halfWidth),(kingPositions[1]>halfWidth),(conditionalFlip(kingPositions[0]>halfWidth,kingPositions[0])<conditionalFlip(kingPositions[1]>halfWidth,kingPositions[1]))]) #my English is how you say inelegant
                else:
                    kingPositions=[moddiv(p,boardWidth) for p in kingPositions]
                    reflections=( [(kingPositions[1][0]>halfWidth or kingPositions[1][0]==halfWidth and axialDisparity(state,0,[False,(kingPositions[0][1]>halfWidth),False])),(kingPositions[0][1]>halfWidth),False]
                                 if boardWidth%2==1 and kingPositions[0][0]==halfWidth else
                                  [(kingPositions[0][0]>halfWidth),(kingPositions[1][1]>halfWidth or kingPositions[1][1]==halfWidth and axialDisparity(state,1,[(kingPositions[0][0]>halfWidth),False,False])),True]
                                 if boardWidth%2==1 and kingPositions[0][1]==halfWidth else
                                  [(kingPositions[0][0]>halfWidth)]*2+[(axialDisparity(state,2,[(kingPositions[0][0]>halfWidth)]*2+[False]) if kingPositions[1][0]==kingPositions[1][1] else (kingPositions[1][0]<kingPositions[1][1])^(kingPositions[0][0]>halfWidth))]
                                 if kingPositions[0][0]==kingPositions[0][1] else
                                  ([True,False] if kingPositions[0][0]>halfWidth else [False,True])+[(axialDisparity(state,2,([True,False,False] if kingPositions[0][0]>halfWidth else [False,True,False])+[False]) if kingPositions[1][0]==boardWidth+~kingPositions[1][1] else (kingPositions[1][0]<boardWidth+~kingPositions[1][1])^(kingPositions[0][0]>halfWidth))]
                                 if kingPositions[0][0]==boardWidth+~kingPositions[0][1] else
                                  [(kingPositions[0][0]>halfWidth),(kingPositions[0][1]>halfWidth),(conditionalFlip(kingPositions[0][0]>halfWidth,kingPositions[0][0])<conditionalFlip(kingPositions[0][1]>halfWidth,kingPositions[0][1]))])
            #equivalent to (but faster than (I hope))
            #print(state)
            #print("tree     ",reflections)
            '''kingPositions=[moddiv(state.index((1,i)),boardWidth) for i in range(2)]
            pawns=any(p[0]==6 for p in state)
            reflections=[False]*3
            for d,w,b in zip(range(1+(not pawns)),*kingPositions): #iterating through dimensions (pretty cool)
                if w>halfWidth or (boardWidth%2==1 and w==halfWidth and (b>halfWidth or (b==halfWidth and axialDisparity(state,d,([0,(kingPositions[0][1]>halfWidth or (kingPositions[0][1]==halfWidth and kingPositions[1][1]>halfWidth)),0] if d==0 else reflections))))): #the black king can't be on the halfWidth also because it's only one square
                    reflections[d]=True
                    kingPositions=[(boardWidth+~i[0],i[1]) if d==0 else (i[0],boardWidth+~i[1]) for i in kingPositions]
            if pawns:
                return state
            reflections[2]=(manifold[0]==manifold[1]) and (kingPositions[0][0]<kingPositions[0][1] or (kingPositions[0][0]==kingPositions[0][1] and (kingPositions[1][0]<kingPositions[1][1] or (kingPositions[1][0]==kingPositions[1][1] and axialDisparity(state,2,reflections))))) #flip white king to bottom-right diagonal half of bottom-left quarter'''
        else:
            reflections=[False]*(3+sum(m for m in manifold if m==1))
        return reflections if reflectionMode==2 else (compoundReflect(state,reflections),reflections) if reflectionMode==1 else compoundReflect(state,reflections)
elif mode==1:
    def printBoard(board,chequerboard=False,delimit=True): #British English program (god save the queen)
        print("["*delimit+"".join(["".join(("_" if letter==" " else letter+'\u0332') if (i+b)%2==0 and chequerboard else letter for i,letter in enumerate(["o" if s else " " for s in board[(b-1)*boardWidth:b*boardWidth]]))+(("]\n" if b==1 else "\n ") if delimit else "\n") for b in range(boardWidth,0,-1)])+"\033["+str(boardWidth)+"B",end="") #ANSI escape sequences
    def layerIndices(x,y):
        return (([centre] if x==0 else #a perfect place                                                                                                               #1, on 1*1 board is [(0,0)]
                 [centre+x*p*(boardWidth if skewedness else 1) for skewedness in range(2) for p in range(-1,3,2)] if y==0 else                                        #2, on 3*3 board is [(0,1),(2,1),(1,0),(1,2)]
                 [centre+x*(xp+yp*boardWidth) for xp in range(-1,3,2) for yp in range(-1,3,2)] if y==x else                                                           #3, on 3*3 board is [(0,0),(0,2),(2,0),(2,2)]
                 [centre+conditionalTranspose(skewedness,x*xp,y*yp) for skewedness in range(2) for xp in range(-1,3,2) for yp in range(-1,3,2)]) if boardWidth%2 else #0, on 5*5 board is [(0,1),(0,3),(4,1),(4,3),(1,0),(3,0),(1,4),(3,4)]
                ([int(centre+x*(xp+1/2+(yp+1/2)*boardWidth)) for xp in range(-1,3,2) for yp in range(-1,3,2)] if y==x else #very suspicious indeed                    #3, on 2*2 board is [(0,0),(0,1),(1,0),(1,1)]
                 [int(centre+conditionalTranspose(skewedness,(x+1/2)*xp,(y+1/2)*yp)) for skewedness in range(2) for xp in range(-1,3,2) for yp in range(-1,3,2)]))    #0, on 4*4 board is [(0,1),(0,2),(3,1),(3,2),(1,0),(2,0),(1,3),(2,3)]
    def constructCellular(layers):
        output=[False]*boardSquares
        liter=iter(layers)
        for i,l in ((i,l) for x in range(halfWidth+1) for y in range(x+1) for i,l in zip(layerIndices(x,y),next(liter))): #next(liter) can be layers[x*(x+1)/2+y-1], I think
            output[i]=l
        return tuple(output)
    def layerSymmetry(l,t,f=False): #layer, type, fourth axis (y==boardWidth+~x)
        return [True]*(3+f) if t==1 else [l[0]==l[1],l[2]==l[3],l[2:0:-1]==l[0:6:3]]+[l[2::-2]==l[1:5:2]]*f if t==2 else [l[0:2]==l[2:4],l[0:4:2]==l[1:5:2],l[2]==l[1]]+[l[0]==l[3]]*f if t==3 else [l[4:8:2]+l[0:2]==l[5:9:2]+l[2:4],l[0:4:2]+l[4:6]==l[1:5:2]+l[6:8],l[4:6]+l[2:4]==l[0:2]+l[6:8]]+[l[5::-4]+l[4::-4]==l[2:10:4]+l[3:11:4]]*f
    def suspiciousSymmetry(l,f=False):
        return layerSymmetry(*l,f)
    def illegalAxes(l,t,s=[True,True,True]): #layer (contents), type, symmetry, returns whether the greater of any of the first disparities (outwards, across all preserved lines of symmetry) lies on the higher-indiced side
            #x flipping                                  y flipping                                  y==z reflection (transposition)         y==boardWidth+~x reflection
        return([(s[0] and            l[0]<l[1]           ),(s[1] and            l[2]<l[3]           ),(s[2] and     l[2:0:-1]<l[0:6:3]     ),(len(s)==4 and s[3] and          l[2::-2]<l[1:5:2]           )] if t==2 else
               [(s[0] and          l[0:2]<l[2:4]         ),(s[1] and        l[0:4:2]<l[1:5:2]       ),(s[2] and          l[2]<l[1]         ),(len(s)==4 and s[3] and              l[0]<l[3]               )] if t==3 else
               [(s[0] and l[4:8:2]+l[0:2]<l[5:9:2]+l[2:4]),(s[1] and l[0:4:2]+l[4:6]<l[1:5:2]+l[6:8]),(s[2] and l[4:6]+l[2:4]<l[0:2]+l[6:8]),(len(s)==4 and s[3] and l[5::-4]+l[4::-4]<l[2:10:4]+l[3:11:4])] if t==0 else
               [False]*4)
    def isLayerIllegal(l,t,s=[True,True,True]):
        return any(illegalAxes(l,t,s))
    def layerType(x,y):
        return ((1 if x==0 else 2 if y==0 else 3 if y==x else 0) if boardWidth%2==1 else (3 if y==x else 0))
    def symmetry(state,reflectionMode=0):
        #print("i",state)
        if symmetryReduction:
            def additionalSymmetry(l,a): #car's parked in the sun
                #print("wibble",l,a)
                #print("wobble",lap(bool.__and__,l,suspiciousSymmetry(a,f=True)))
                return lap(bool.__and__,l,suspiciousSymmetry(a,f=True))
            '''#print(len(state),[layerIndices(x,y) for x in range(halfWidth+1) for y in range(x+1)])
            layers=[([state[i] for i in layerIndices(x,y)],layerType(x,y)) for x in range(halfWidth+1) for y in range(x+1)]
            def eitherOr(a,b):
                return lap(bool.__or__,a,b)
            branchSymmetry=accumulate(layers,func=additionalSymmetry,initial=[True]*4)
            #for (l,t),s in zip(layers,branchSymmetry):
                #print("isLayerIllegal("+str(l)+","+str(t)+","+str(s)+")")
            #print(len(layers),len([i for i,j in zip(*zip(*layers))]),len([i for i in branchSymmetry]))
            #print(lap(isLayerIllegal,zip(*layers),branchSymmetry))
            axesOfIllegality=reduce(eitherOr,map(illegalAxes,*zip(*layers),branchSymmetry))
            #print("axes",axesOfIllegality)
            reflections=axesOfIllegality[:2]+[axesOfIllegality[3]^axesOfIllegality[1] if axesOfIllegality[0]^axesOfIllegality[1] else axesOfIllegality[2]] #if the y axis is flipped, the one that is transposition in the compound basis (whichever one it is in the initial basis) will have its disparity reversed 
            #print("a",axesOfIllegality,"\nr",reflections,"\no",compoundReflect(state,reflections))'''
            '''for i in ((r,[compoundPositionReflect(i,r) for i in range(boardSquares)]) for r in ([i>>j &1 for j in range(3)] for i in range(8))):
                print(i)
            exit()'''
            (unreflectedLayerIndices,layerTypes)=zip(*[(layerIndices(x,y),layerType(x,y)) for x in range(halfWidth+1) for y in range(x+1)])
            reflectedLayerStates=([[state[compoundPositionReflect(c,r)] for c in l] for l in unreflectedLayerIndices] for r in ([i>>j &1 for j in range(3)] for i in range(8))) #eightfold
            def isLayerStateLegal(state,layerTypes):
                branchSymmetry=list(accumulate(zip(state,layerTypes),func=additionalSymmetry,initial=[True]*3))[:3]
                return not any(isLayerIllegal(l,t,s) for l,t,s in zip(state,layerTypes,branchSymmetry))
            legalIndice=next(i for i,l in enumerate(isLayerStateLegal(s,layerTypes) for s in reflectedLayerStates) if l) #[isLayerStateLegal(s,layerTypes) for s in reflectedLayerStates].index(True) checks redundant ones
            reflections=[legalIndice>>j &1 for j in range(3)] #expensive but averts problems like the [False,False, True,
                                                                                                      #False,False,False,
                                                                                                      # True,False,False] board (that has an illegal disparity in only the x and y axes, cancelling each other out), may perhaps fix original one
        else:
            reflections=[False]*3
        #print("r",reflections)
        #print("o",compoundReflect(state,reflections))
        return reflections if reflectionMode==2 else (compoundReflect(state,reflections),reflections) if reflectionMode==1 else compoundReflect(state,reflections)
    def generateCellular(): #eightfold symmetry reduction is harder when there are no kings, and requires counting on basis of sets of cells with the same displacement from the centre, "layers" (if a layer violates a line of symmetry in the wrong direction (that hasn't been already violated by another layer less far), it is incremented again and all layers further out are skipped)
        if symmetryReduction:
            #may be used if caching such things allows speedup
            '''configurations=[            # duplicates resolved by lexicographically minimal
                                           # i, x,y,t,r, duplicate of  #r symmetry in y=-x line of symmetry, inapplicable
                (False,False,False,False), # 0, 1,1,1,1
                ( True,False,False,False), # 1, 1,0,0,0
               #(False, True,False,False), # 2, 0,1,0,0, duplicate of 1
                ( True, True,False,False), # 3, 0,0,1,0
               #(False,False, True,False), # 4, 0,1,0,0, duplicate of 1
               #( True,False, True,False), # 5, 0,0,0,1, duplicate of 3
                (False, True, True,False), # 6, 1,1,0,0
                ( True, True, True,False), # 7, 1,0,0,0
               #(False,False,False, True), # 8, 1,0,0,0, duplicate of 1
               #( True,False,False, True), # 9, 1,1,0,0, duplicate of 6
               #(False, True,False, True), #10, 0,0,0,1, duplicate of 3
               #( True, True,False, True), #11, 0,1,0,0, duplicate of 7
               #(False,False, True, True), #12, 0,0,1,0, duplicate of 3
               #( True,False, True, True), #13, 0,1,0,0, duplicate of 7
               #(False, True, True, True), #14, 1,0,0,0, duplicate of 7
                ( True, True, True, True)] #15, 1,1,1,1
                                            #asymmetricalities:
                                            #x=c[1]^c[2]
                                            #y=c[0]^c[3]
                                            #t=c[0]^c[1]|c[2]^c[3]
                                            #r=c[0]^c[2]|c[1]^c[3]
            #on 3*3 board, squares ordered orthogonal [(1,0),(0,1),(2,1),(1,2)]
                                            #diagonal [(0,0),(2,0),(0,2),(2,2)]
            #so diagonal indice comparisons for (x,y,t,r)=orthogonal ones for (t,r,x,y)'''
            global layerTypes
            layerTypes=[layerType(x,y) for x in range(halfWidth+1) for y in range(x+1)]
            typeLengths=[8,1,4,4]
            layers=[[False]*typeLengths[l] for l in layerTypes]
            #print(layerTypes,layers)
            branchSymmetry=[[True]*3]*len(layers)
            arm=len(layers)-1
            cellulars=[constructCellular(layers)] #[[False]*boardSquares]
            #cellularSymmetries=[branchSymmetry]
            do=True
            while True:
                layers[arm][0]^=True
                finger=0
                #print("finger",arm,layers[arm][0])
                while not layers[arm][finger]: #carry the 1
                    finger+=1
                    if finger==len(layers[arm]):
                        #layers[arm:len(layers)]=[[False]*typeLengths[l] for l in layerTypes[arm:len(layers)]] #would be arm+1 but is done before
                        arm-=1
                        #print("regress",arm)
                        if arm<0:
                            break
                        else:
                            #del branchSymmetry[-1]
                            #print("del",len(branchSymmetry))
                            layers[arm][0]^=True
                            finger=0
                            #print("continue from arm",arm)
                            #break #bypasses while's else (if broken, this layer had no more legal states and the next must be regressed to instead) #edit: continues inline
                    else:
                        layers[arm][finger]^=True
                #print(arm,len(layers),len(layerTypes))
                #print(layers[arm],layerTypes[arm],branchSymmetry[-2],len(branchSymmetry))
                if arm<0:
                    break
                #print(len(layers),len(layerTypes),arm,len(branchSymmetry))
                elif not isLayerIllegal(layers[arm],layerTypes[arm],branchSymmetry[arm]):
                    #print(len(branchSymmetry),len(layers)+1-len(branchSymmetry))
                    branchSymmetry[arm+1:]=[lap(bool.__and__,branchSymmetry[arm],layerSymmetry(layers[arm],layerTypes[arm]))]*(len(layers)-(arm+1)) #[b and l for b,l in zip(branchSymmetry[-2],layerSymmetry(layers[arm],layerTypes[arm]))] doesn't work either, it isn't a problem with map
                    arm=len(layers)-1
                    cellulars.append(constructCellular(layers))
                    #printBoard(cellulars[-1])
                    #print(branchSymmetry)
                    #cellularSymmetries.append(branchSymmetry)
        else:
            cellulars=[]
            '''current=[False]*boardSquares
            for i in range(2**boardSquares):
                cellulars.append(tuple(current))
                j=0
                while (j==0 or not current[j-1]) and j<len(current):
                    current[j]^=True
                    j+=1'''
            #cellulars=[[False]*(boardSquares-(len(bin(i))-2))+[bool(int(j)) for j in list(bin(i))[2:]] for i in range(2**boardSquares)] #not sure whether faster but I dislike it (though I don't like the current one either (though if you want speed, the point of symmetry is to be faster))
        return cellulars
    
    states=generateCellular()
    niemiec=True #whimsical
    def RLE(board,rule=""):
        return ("x ="+str(boardWidth)+", y = "+str(boardWidth)+", rule = "+rule+"\n")*bool(rule)+"$".join("".join(l*2 if niemiec and q==2 else l if q==1 else str(q)+l for l,q in [(("o"if l else "b"),len(list(q))) for l,q in groupby(board[b*boardWidth:(b+1)*boardWidth])]) for b in range(boardWidth-1,-1,-1))+"!"
    
    def stateInt(state):
        return sum(s<<i for i,s in enumerate(state))
    def intState(integer):
        return [integer>>i &1 for i in range(boardSquares)]
    transitions=["b0c","b1c","b2c","b3c","b2n","b4c","b1e","b2a","b2k","b3n","b3i","b4n","b3q","b3y","b4y","b5e","b2e","b3a","b3j","b4a","b4w","b5a","b3k","b4q","b4k","b5j","b5k","b6e","b3e","b4r","b4j","b5n","b5i","b6a","b5q","b5y","b6k","b7e","b2i","b3r","b4i","b4t","b5r","b4z","b6i","b4e","b5c","b6c","b7c","b6n","b8","s0","s1c","s2c","s3c","s2n","s4c","s1e","s2a","s2k","s3n","s3i","s4n","s3q","s3y","s4y","s5e","s2e","s3a","s3j","s4a","s4w","s5a","s3k","s4q","s4k","s5j","s5k","s6e","s3e","s4r","s4j","s5n","s5i","s6a","s5q","s5y","s6k","s7e","s2i","s3r","s4i","s4t","s5r","s4z","s6i","s4e","s5c","s6c","s7c","s6n","s8c"]
    totalTransitions=[{"c"}, #using c for 0 and 8 because otherwise no distinction from empty set
                      {"c","e"},
                      {"c","e","k","a","i","n"},
                      {"c","e","k","a","i","n","y","q","j","r"},
                      {"c","e","k","a","i","n","y","q","j","r","t","w","z"},
                      {"c","e","k","a","i","n","y","q","j","r"},
                      {"c","e","k","a","i","n"},
                      {"c","e"},
                      {"c"}] #if squares had more edges and vertices, it would approach a normal distribution, I think (or would it, due to the symmetry reduction (hmm))
    reducedTransitions=[0,1,5,69,257,325,2,3,66,67,7,71,259,322,323,327,10,11,14,15,78,79,266,267,270,271,334,335,42,43,106,107,47,111,299,362,363,367,130,131,195,135,199,387,455,170,171,175,239,427,495,16,17,21,85,273,341,18,19,82,83,23,87,275,338,339,343,26,27,30,31,94,95,282,283,286,287,350,351,58,59,122,123,63,127,315,378,379,383,146,147,211,151,215,403,471,186,187,191,255,443,511] #indices in neighbourhood list (3*3 state) of each transition
    unreducedTransitions=[0,1,6,7,1,2,7,10,6,7,16,17,8,9,18,19,51,52,57,58,52,53,58,61,57,58,67,68,59,60,69,70,6,8,16,18,7,9,17,19,38,39,28,29,39,40,29,32,57,59,67,69,58,60,68,70,89,90,79,80,90,91,80,83,1,2,8,9,4,3,12,11,7,10,18,19,12,11,20,21,52,53,59,60,55,54,63,62,58,61,69,70,63,62,71,72,8,13,22,24,12,14,23,25,39,41,30,31,43,42,34,33,59,64,73,75,63,65,74,76,90,92,81,82,94,93,85,84,6,8,38,39,8,13,39,41,16,18,28,29,22,24,30,31,57,59,89,90,59,64,90,92,67,69,79,80,73,75,81,82,16,22,28,30,18,24,29,31,28,30,45,46,30,35,46,47,67,73,79,81,69,75,80,82,79,81,96,97,81,86,97,98,7,9,39,40,12,14,43,42,17,19,29,32,23,25,34,33,58,60,90,91,63,65,94,93,68,70,80,83,74,76,85,84,18,24,30,35,20,26,34,36,29,31,46,47,34,36,49,48,69,75,81,86,71,77,85,87,80,82,97,98,85,87,100,99,1,4,8,12,2,3,9,11,8,12,22,23,13,14,24,25,52,55,59,63,53,54,60,62,59,63,73,74,64,65,75,76,7,12,18,20,10,11,19,21,39,43,30,34,41,42,31,33,58,63,69,71,61,62,70,72,90,94,81,85,92,93,82,84,2,3,13,14,3,5,14,15,9,11,24,25,14,15,26,27,53,54,64,65,54,56,65,66,60,62,75,76,65,66,77,78,9,14,24,26,11,15,25,27,40,42,35,36,42,44,36,37,60,65,75,77,62,66,76,78,91,93,86,87,93,95,87,88,7,12,39,43,9,14,40,42,18,20,30,34,24,26,35,36,58,63,90,94,60,65,91,93,69,71,81,85,75,77,86,87,17,23,29,34,19,25,32,33,29,34,46,49,31,36,47,48,68,74,80,85,70,76,83,84,80,85,97,100,82,87,98,99,10,11,41,42,11,15,42,44,19,21,31,33,25,27,36,37,61,62,92,93,62,66,93,95,70,72,82,84,76,78,87,88,19,25,31,36,21,27,33,37,32,33,47,48,33,37,48,50,70,76,82,87,72,78,84,88,83,84,98,99,84,88,99,101] #indices in transitions list of each neighbourhood
    """if input("see states? ")=="y":
        print("["+",".join([str(stateInt(s)) for s in states])+"]")
        '''if boardWidth==3 and not symmetryReduction:
            unreducedTransitions=[reducedTransitions.index(stateInt(symmetry(s))) for s in states]
            print(unreducedTransitions)
            exit()'''
        if boardWidth==3 and symmetryReduction:
            for s in states:
                print((stateInt(s)==stateInt(symmetry(s))),stateInt(s),stateInt(symmetry(s)))
            for s,t in zip(states,transitions):
                printBoard(s)
                print(t+"\n")
            print("["+",".join(str(stateInt(s)) for s in states)+"]")
        print("\n".join(["("*(boardWidth==3 and not symmetryReduction)+"["+",".join(" "*i+str(i) for i in (s[0] if boardWidth==3 and symmetryReduction else s))+"]"+(transitions[reducedTransitions.index(stateInt(symmetry(s[0] if boardWidth==3 and symmetryReduction else s)))]+")")*(boardWidth==3 and not symmetryReduction) for s in (zip(states,transitions) if boardWidth==3 and symmetryReduction else states)]))
        '''for s in (zip(states,transitions) if boardWidth==3 else states):
            printBoard(s[0] if boardWidth==3 else s)
            print((RLE(s[0])+" "+s[1] if boardWidth==3 else RLE(s))+"\n")'''
        exit()
    else:"""
    rule=input("Which rule would you like? ").lower().replace("/","").replace("b","").split("s")
    ruleTotalTransitions=[[set() for __ in range(9)] for _ in range(2)]
    for i,r in enumerate(rule):
        accumulator=""
        for t in reversed(r):
            if t in {"0","1","2","3","4","5","6","7","8"}:
                ruleTotalTransitions[i][int(t)]=(totalTransitions[int(t)] if accumulator=="" else totalTransitions[int(t)]-set(accumulator) if "-" in accumulator else set(accumulator))
                accumulator=""
            else:
                accumulator+=t
    #print(ruleTotalTransitions)
    rule={("s" if i else "b")+str(j)+t for i,s in enumerate(ruleTotalTransitions) for j,ss in enumerate(s) for t in ss}
    #print(rule)
    rule=[(t in rule) for t in transitions]
    if manifold[0]==0 or manifold[1]==0:
        (b1e,b2a,b1c,b2c,b3i)=(rule[transitions.index("b1e")],rule[transitions.index("b2a")],rule[transitions.index("b1c")],rule[transitions.index("b2c")],rule[transitions.index("b3i")])
        if not any(manifold):
            corners=b1c
            nearCorners=(b1e or b2a)
        edges=(b1c or b1e or b2a or b3i)
    #print(rule)
    rule=[rule[t] for t in unreducedTransitions]
    #print(rule)
    #edgeNeighbourhoods=
    def iterateCellular(state,rule,index=False): #index makes it return the state's index in the list (done here due to optimisation for non-symmetry-reduced mode)
        iterated=[rule[stateInt([False if k==None else state[k] for k in precomputedKingMoves[i]])] for i in range(boardSquares)]
        return (((stateDict[symmetry(iterated)] if symmetryReduction else stateInt(iterated)) if index else iterated),(edges and any((b1c and (s==(True,False,False) or s==(False,False,True)) or b1e and s==(False,True,False) or b2c and s==(True,False,True) or b3i and s==(True,True,True)) for s in (manifold[1]==0)*[state[i:i+3] for n in (0,boardSquares-boardWidth) for i in range(n,n+boardWidth-2)]+(manifold[0]==0)*[state[i:i+3*boardWidth:boardWidth] for n in (0,boardWidth-1) for i in range(n,n+boardSquares-2*boardWidth,boardWidth)]) or
                                                                                                                       corners and any(state[0],state[boardWidth-1],state[boardSquares-boardWidth],state[boardSquares-1]) or
                                                                                                                       nearCorners and any(state[x*(boardWidth-1)+y*(boardSquares-boardWidth):x*(boardWidth-1)+y*(boardSquares-boardWidth)+boardWidth**s*(-1)**(y if s else x):boardWidth**s*(-1)**(y if s else x)] for x in range(2) for y in range(2) for s in range(2)))) #replace precomputedKingMoves with precomputedKnightMoves if you would like to have some fun
else:
    def stringBoard(board):
        return((" " if len(board)>10-1 else "").join(str(i) for i,c in enumerate(board,start=1) if c))
    def printBoard(board):
        print(stringBoard(board)) #we can't hardcode 9 in case a different number becomes 1 less than 10
    faces=6
    flaps=boardWidth=int(input("How many flaps would you like? "))
    consecutiveTurns=(input("Would you like to roll again instead of changing to the other player's turn when your turn is successful? (y/n)")=="y")
    def dice(s):
        return(--0--(max((i for i,s in enumerate(s,start=1) if s),default=0))//faces)
    stateDice=tuple(i-1 for i in map(dice,theStates()))
    diceNumbers=tuple(tuple(range(s,s*faces+1)) for s in range(1,--0--flaps//faces+1))
    #diceProbabilities=tuple(tuple(reduce(int.__mul__,range(1,6*n+1))/reduce(int.__mul__,(reduce(int.__mul__,range(1,i+1),1) for i in (x,6*n-x))) for x in range(n,6*n)) for n in range(1,--0--flaps//faces+1))
    #not working (I hate multinomials)
    def addDice(existingAmplitudes,ignore):
        return([sum(existingAmplitudes[i-f] for f in range(faces) if 0<=i-f<len(existingAmplitudes)) for i in range(len(existingAmplitudes)+(faces-1))])
    diceProbabilities=list(accumulate(range(--0--flaps//faces-1),addDice,initial=[1]*faces))
    diceProbabilityDenominators=[faces**i for i in range(1,--0--flaps//faces+1)]
    def subsetSums(Set):
        #return map(sum,combinations(Set))
        return([(sum(1<<(i-1) for i in c),sum(c)) for c in (c for r in range(len(Set)+1) for c in combinations(Set,r))])
    #print([(s,list(zip(d,(list(zip(mi,ti)) for mi,ti in zip(m,t))))) for s,d,m,t in zip(states,stateDice,stateMoves,stateTransitions)])
    #print(diceProbabilities)
    #print(stateTransitions)
correctNumber=(int( (1/8)*(2**boardSquares+2*2**((boardSquares+3)/4)+2**((boardSquares+1)/2)+4*2**((boardSquares+boardWidth)/2))
                   if boardWidth%2 else #from https://oeis.org/A054247 (my beloved)
                    (1/8)*(2**boardSquares+2*2**(boardSquares/4)+3*2**(boardSquares/2)+2*2** ((boardSquares+boardWidth)/2)))
                   if symmetryReduction else
                    2**boardSquares)
def plural(num,name):
    return str(num)+" "+name+"s"*(num!=1)
print(plural(len(states),"state")+", "+(str(stateChecks.count(True))+(" in check" if mode==0 else " exceeding bounds"))*(mode!=2)+(("correct" if len(states)==correctNumber else "should be "+(str(correctNumber)+",")) if symmetryReduction else "they will be generated in-place")*(mode!=0)) #boundary exceedings currently computed with state transitions

if mode==0 or symmetryReduction: #not necessary when no symmetry reduction in cellular automata mode due to each state's binary representation being its index
    stateDict={s:i for i,s in enumerate(states if mode==1 or turnwise else zip(stateTurns,states))}
    print("state dict done")
#print(min((print(i,j,q,s),len(s)) for i,(s,a) in enumerate(zip(states,stateSquareAttacks)) for j,q in enumerate(a)))

if mode==0:
    def applyMoveToBoard(state,move,invert=True):
        return boardReflect(tuple(((move[2] if len(move)==3 else state[move[0]][0]),(state[move[0]][1]^invert)) if k==move[1] else (0,0) if k==move[0] or r[0]==0 else (r[0],r[1]^invert) for k,r in enumerate(state)),(1 if anyPawns and any(q[0]==6 for q in state) else -1)) #board flipped such that pawns of turn to move are always upwards
    def dictInput(s,m):
        #printBoard(symmetry(applyMoveToBoard(s,m)))
        return symmetry(applyMoveToBoard(s,m)) if turnwise else (not s[0],symmetry(applyMoveToBoard(s[1],m)))
    (stateMoves,stateTransitions)=[[() if mt==(None,) else mt for mt in l] for l in zip(*[list(zip(*([(None,)*2] if r==[[]]*boardSquares else [m for q in r for m in q]))) for r in ([[] if q[0]==0 or q[1] else [(m,stateDict[d]) for m,d in ((m,dictInput(s,m)) for m in findPieceMoves(s,i,q,False,True) if s[m[1]][0]==0 or q[1]!=s[m[1]][1]) if (d in stateDict if True else (q[0]!=1 or not a[m[1]][1]))] for i,q in enumerate(s)] for s,a in zip(states,stateSquareAttacks))])] #you can replace "if True" with "if any((j[0] in iterativePieces) for j in d)", if you make it account for the fact that when king is in check, other pieces are unmovable except to obstruct or capture attacking piece
    #replace stateDict with (print(s),print(tuple(tuple(int(j) for j in i) for i in a)),stateDict[d]) for diagnostics
elif mode==1:
    #(stateTransitions,stateChecks)=zip(*[((stateDict[symmetry(c)] if symmetryReduction else stateInt(c)),i) for c,i in (iterateCellular((s if symmetryReduction else intState(s)),rule) for s in (states if symmetryReduction else range(2**boardSquares)))])
    (stateTransitions,stateChecks)=zip(*([iterateCellular(s,rule,True) for s in states] if symmetryReduction else [iterateCellular(intState(s),rule,True) for s in range(2**boardSquares)]))
else:
    stateMoves=[[[ess for ess,ss in subsetSums([i for i,si in enumerate(s,start=1) if si]) if ss==di] for di in diceNumbers[d]] for s,d in zip(theStates(),stateDice)] #different tasks call for different conventions
    stateTransitions=[[[sum((de>>i&1^f)<<i for i,f in enumerate(s)) for de in di] for di in m] for s,m in zip(theStates(),stateMoves)] #de&1<<i^f<<i=(de>>i&1^f)<<i
#print("transitions between",len(states),"states:",stateTransitions)
print("state "+"moves and "*(mode==0)+"transitions done"+(", "+str(stateChecks.count(True))+" states exceeding bounds")*(mode==1))
stateCount=(len(states) if mode==0 or symmetryReduction else 2**(boardSquares if mode==1 else flaps))
if mode==2:
    stateParents=tuple(tuple(sorted({s^(i&~s) for i in range(s+1,2**flaps) if sum(((i&~s)>>n&1)*(n+1) for n in range(flaps)) in diceNumbers[stateDice[i&~s]]})) for s in range(stateCount)) #would be slightly nicer if dice began at 0
else:
    stateParents=tuple([[] for i in range(stateCount)]) #[[]]*len(states) makes appends affect all elements
    for i,s in enumerate(stateTransitions):
        if mode==0:
            for t in s:
                if t!=None:
                    stateParents[t].append(i)
        else:
            stateParents[s].append(i)
print("state parents done,",stateParents.count([]),"orphans") #orphans guaranteed to be universal orphans (not only in the tablebase) if there are no pawns (the only piece with different capturing behaviour), or if the king to move is in double-check that couldn't have been discovered or is attacked by a sliding piece and another behind it that couldn't have another piece obstructing them both on the previous turn
#stateMoves=[[[m[1] for m in s if m[0]==i] for i in range(boardSquares)] for s in [[m[k] for k,l in enumerate(j)] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]] #would use this one except stateMoves is only currently used to convert a list of an origin and destination to a state ID (for which being parallel with stateTransitions is more efficient)
#stateMoves=[m[:len(j)] for j,m in zip(stateTransitions,[[[i,k] for i,j in enumerate(s) for k in j] for s in stateMoves])]
#print("state moves reformatted")

if mode==0:
    def printWinningnesses(): #could be done inline in the regression loop also to be slightly more efficient (though its performance impact is negligible) and to make it tell you as it finds them instead of at the end (which could take hours for large tablebases)
        i=0
        while i==0 or matesInI!=[0]*3:
            matesInI=[sum(j==(w,i) for j in stateWinningnesses) for w in range(-1,2)]
            if matesInI!=[0]*3:
                print("there are",matesInI[1],"stalemates in "+str(i)+" and",matesInI[2*(i%2)],("wins" if i%2==1 else "losses"),"in",i) #in terms of ply
            i+=1
        global maximumDTM
        maximumDTM=i-2
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
elif mode==1:
    def displacements(oscillator): #intakes list of oscillator's states
        if any(any(o) for o in oscillator):
            cellTouchednesses=[any(o[i] for o in oscillator) for i in range(boardSquares)]
            boundingBox=(*minmax([i%boardWidth for i,s in enumerate(cellTouchednesses) if s]),*minmax([i//boardWidth for i,s in enumerate(cellTouchednesses) if s]))
            return {compoundReflect(scroll(o,-x,-y),[f>>i &1 for i in range(3)]) for o in oscillator for x in range(-boundingBox[0],boardWidth-boundingBox[1]) for y in range(-boundingBox[2],boardWidth-boundingBox[3]) for f in range(8)} #reflect after displacement to avoid having to displace by different values depending on reflectedness
        else: #"The stars are receding. Oh, the vast emptiness!"
            return {tuple(o) for o in oscillator} #"Yeah, yeah, I can take a hint."
    stateLoops=[None]*stateCount
    stateSearchednesses=[False]*stateCount
    if symmetryReduction:
        loops=[]
    oscillators=[]
    for i in range(stateCount):
        j=i
        jLoop=[]
        while j not in jLoop:
            if stateChecks[j] or stateSearchednesses[j]:
                break
            jLoop.append(j)
            j=stateTransitions[j]
        else:
            collision=jLoop.index(j)
            jLoopLength=len(jLoop)-collision
            for j in jLoop:
                stateSearchednesses[j]=True
            jLoop=jLoop[collision:]
            for j in jLoop:
                stateLoops[j]=i
            if symmetryReduction:
                loops.append([states[j] for j in jLoop])
            else:
                oscillators.append(lap(intState,jLoop))
    if symmetryReduction:
        for l in loops: #find non-modulo true periods (for which reflections don't count)
            asymmetricLoop=[]
            s=list(l[0])
            while s not in asymmetricLoop:
                asymmetricLoop.append(s)
                s=iterateCellular(s,rule)
                if s[1]:
                    break
                else:
                    s=s[0]
            else: #if not broken
                oscillators.append(asymmetricLoop)
    for i,o in enumerate(oscillators,start=1): #different tasks call for different conventions
        for d in displacements(o):
            removals=[ni for ni,no in enumerate(oscillators[i:],start=i) if list(d) in no] #run away
            '''if len(removals)>0:
                print("wibble")
                printBoard(d)
                printBoard(oscillators[removals[0]][0])'''
            for r in removals:
                del oscillators[r]
                if i==len(oscillators):
                    break
    oscillatoryPeriods=[]
    periodInstances=[]
    for o in oscillators:
        if len(o) in oscillatoryPeriods:
            periodInstances[oscillatoryPeriods.index(len(o))]+=1
        else:
            oscillatoryPeriods.append(len(o))
            periodInstances.append(1)
    if oscillators==[]:
        print("no self-sustaining patterns :(")
    else:
        (oscillatoryPeriods,periodInstances)=zip(*sorted(zip(oscillatoryPeriods,periodInstances)))
        print((plural(periodInstances[oscillatoryPeriods.index(1)],"still life")+", " if 1 in oscillatoryPeriods else "")+(plural(sum(len(o)!=1 for o in oscillators),"oscillator") if len(oscillatoryPeriods)-(1 in oscillatoryPeriods)>0 else ""))
        for p,i in zip(oscillatoryPeriods[(1 in oscillatoryPeriods):],periodInstances[(1 in oscillatoryPeriods):]):
            print(plural(i,"period "+str(p)+" oscillator"))
        if input("print all "+(("self-sustaining patterns" if len(oscillatoryPeriods)>1 else "still lifes") if 1 in oscillatoryPeriods else "oscillators")+"? (y/n)")=="y":
            for o in oscillators:
                print("still life" if len(o)==1 else ("period "+str(len(o))+" oscillator"),RLE(o[0]))
                for s in o:
                    printBoard(s)
else:
    stateMoveWinningnesses=[[[None]*len(mi) for mi in m] for m in stateMoves]
    stateWinningnesses=[None]*2**flaps
    stateWinningnesses[0]=((1,1) if consecutiveTurns else (0,1)) #they are fractions
    #print(stateWinningnesses)
    def invert(winningness):
        return([winningness[1]-winningness[0],winningness[1]])
    def unfraction(fraction):
        return(fraction[0]/fraction[1])
    def weightedFractionAverage(weights,fractionSets): #if fraction is empty, its coefficient is multiplied by its opposite, x=(a*b+c*(1-x))/(a+c), x-c*(1-x)/(a+c)=a*b/(a+c), x*(1+c/(a+c))-c/(a+c)=a*b/(a+c), x=(a*b+c)/(1+c/(a+c))/(a+c)=(a*b+c)/((1+c/(a+c))*(a+c))=(a*b+c)/((a+c)+c)=(a*b+c)/(a+2*c)
        (moveWeights,optimalMoves)=zip(*[(w,max(f,key=unfraction)) for w,f in zip(weights,fractionSets) if len(f)>0])
        emptyWeight=sum(w for w,f in zip(weights,fractionSets) if len(f)==0)
        commonMultiplier=math.lcm(*[m[1] for m in optimalMoves])
        returnFraction=[sum(w*commonMultiplier//m[1]*m[0] for w,m in zip(moveWeights,optimalMoves))+commonMultiplier*emptyWeight,(sum(moveWeights)+2*emptyWeight)*commonMultiplier]
        simplifier=math.gcd(*returnFraction)
        return([f//simplifier for f in returnFraction])
    cycles=0
    while cycles==0 or statesChanged!=0:
        statesChanged=0
        for i,(s,d,m,t,w) in enumerate(zip(theStates(),(diceNumbers[d] for d in stateDice),stateMoves,stateTransitions,stateWinningnesses)):
            for ii,(di,mi,ti) in enumerate(zip(d,m,t)):
                for iii,(mii,tii) in enumerate(zip(mi,ti)):
                    if stateMoveWinningnesses[i][ii][iii]==None and stateWinningnesses[tii]!=None:
                        stateMoveWinningnesses[i][ii][iii]=stateWinningnesses[tii] if consecutiveTurns else invert(stateWinningnesses[tii])
                        #print(s,di,mii,tii)
            if w==None and not any(None in w for w in stateMoveWinningnesses[i]):
                #print(statesChanged)
                #print(stateMoveWinningnesses[i])
                stateWinningnesses[i]=weightedFractionAverage(diceProbabilities[dice(s)-1],stateMoveWinningnesses[i])
                statesChanged+=1
        cycles+=1
    print(cycles)
    print(stateWinningnesses[-1])

def initialisePygame(guiMode):
    global clock
    clock=pygame.time.Clock()
    pygame.init()
    global black
    black=(0,0,0)
    global colours
    colours=[(236,217,185),(174,137,104),(255,255,255),(0,0,0),(255,0,0),(255,255,0),(0,255,0)] #using lichess's square colours but do not tell lichess
    global angleColour
    def angleColour(angle):
        return tuple((math.cos(angle-math.tau*i/3)+1)*255/2 for i in range(3))
    global averageColours
    def averageColours(*colours):
        return tuple(math.sqrt(sum(c[i]**2 for c in colours)/len(colours)) for i in range(3)) #correct way, I think
    global weightedAverageColours
    def weightedAverageColours(*colours):
        return tuple(math.sqrt(sum(c[1][i]**2*c[0] for c in colours)/sum(c[0] for c in colours)) for i in range(3))
    colours.insert(2,averageColours(*colours[:2]))
    for i in range(2):
        colours.insert(i+3,averageColours(colours[i],colours[2]))
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
    global cellColours
    maximum=(--0--boardWidth//faces*faces if mode==2 else boardSquares)
    cellColours=tuple(angleColour(c*math.tau/maximum) for c in range(maximum))
    global renderBoard
    def renderBoard(state,perceivedMoves,interactive,boardSize=minSize,renderPosition=(0,0)):
        squareSize=boardSize//boardWidth
        for i,s in enumerate(state):
            if interactive:
                m=[selectedSquare,i]
            squarePosition=[i%boardWidth,((boardWidth-1)/2 if mode==2 else boardWidth+~i//boardWidth)] #I hate Pygame's coordinates so much
            screenPosition=[r+s*squareSize for r,s in zip(renderPosition,squarePosition)]
            drawShape([squareSize]*2,screenPosition,((((0,255,0) if isOptimal(stateTransitions[currentIndex][perceivedMoves.index(m)]) else (255,0,0)) if interactive and selectedness and m in perceivedMoves else colours[sum(squarePosition)%2]) if mode==0 else ((cellColours[i] if colourMode else (255,255,255)) if s else (48,48,48))),0) #Golly colour
            if mode==0:
                if s!=(0,0):
                    colour=(0,255,0) if (interactive and i==selectedSquare and selectedness) else colours[5+s[1]]
                    if s[0]!=0:
                        if imageMode and s[0]<7:
                            screen.blit(pygame.transform.scale(pieceImages[s[1]][s[0]-1],[squareSize]*2),screenPosition)
                        else:
                            drawShape([squareSize*3/4]*2,[(i+1/(8 if s[0]==3 else 2))*squareSize for i in squarePosition],colour,(0 if s[0]==3 else s[0]))
        if interactive and clickDone and all(0<=m<boardSize for m in mousePos[:2]):
            global clickedSquare
            clickedSquare=sum(conditionalFlip(di,m)*boardWidth**di for di,m in enumerate(m//squareSize for m in mousePos[:2]))
            #clickedSquare=compoundPositionReflect(clickedSquare,boardFlipping,1)

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

if mode==0 or mode==2 and input("Would you like to play "+("chess" if mode==0 else "Shut the Box")+" with God (y) or see the state transition diagram (n)? ")=="y":
    run=True
    if mode==0:
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
                        for i,l in enumerate(axisLetters):
                            if restrictionCharacter in l:
                                restrictedAxes[i]=l.index(restrictionCharacter)
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
        while run:
            currentIndex=stateWinningnesses.index(((-1)**(maximumDTM+1),maximumDTM))#random.randrange(len(states)) #use stateWinningnesses.index((-1,maximumDTM)) to see longest decisive position
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
                    apparentMoves=[[compoundPositionReflect(j,boardFlipping) for j in i] for i in thisStateMoves]
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
                        promotionType=pieceNames[0].index(move[-1]) if move[-2]=="=" else 0
                        if promotionType!=0:
                            move=move[:-2]
                        print(move,(turn,perceivedState),thisStateMoves)
                        parsedMove=[compoundPositionReflect(i,boardFlipping,1) for i in parseMove(move,turn,perceivedState,apparentMoves)]+[promotionType]*promotionType!=0
                        print(parsedMove)
                    currentIndex=stateTransitions[currentIndex][thisStateMoves.index(tuple(parsedMove))]
                    reflections=symmetry(applyMoveToBoard(currentState,parsedMove,False),2)
                    print(reflections)
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
        def rollDice(diceIndex):
            roll=random.random()*diceProbabilityDenominators[diceIndex]
            for d,p in zip(diceNumbers[stateDice[currentIndex]],diceProbabilities[diceIndex]):
                roll-=p
                if roll<0:
                    break #there is a 1/(floating point precision) chance that it will be exhausted (if random.random() is upper-inclusive) but that's a risk I'm willing to take
            return(d)
        print("states and flipping combinations represented by "+("space-delimited" if flaps>10-1 else "concatenated")+" indexes of open flaps, moves similar but for flaps that will be closed")
        while run:
            currentIndex=stateCount-1
            while run:
                print("board: "+stringBoard(theStates(currentIndex))+", chance of winning:","/".join(lap(str,stateWinningnesses[currentIndex])))
                diceIndex=(len(diceNumbers[stateDice[currentIndex]])+1)//faces-1
                d=rollDice(diceIndex)
                print("you have rolled",d)
                if len(stateMoves[currentIndex][d+~stateDice[currentIndex]])>0:
                    humanChoices=lap(stringBoard,map(theStates,stateMoves[currentIndex][d+~stateDice[currentIndex]])) #0th stateDice is one die so subtracts 1, 1th is two dice so subtracts 2, etc., so bitwise NOT
                    move=humanChoices.index(input("you can close "+", ".join(humanChoices)+". "))
                    currentIndex=stateTransitions[currentIndex][d+~stateDice[currentIndex]][move]
                    if currentIndex==0:
                        print("won")
                        break
        else: exit()
else:
    if stateCount>512:
        input(plural(stateCount,"state")+", will be slow")
    import pygame
    from pygame.locals import *
    initialisePygame(False)
    rad=halfSize[0]/stateCount
    #bitColours=[[int(255*(math.cos((j/n-i/3)*2*math.pi)+1)/2) for i in range(3)] for j in range(n)]
    nodes=[[[[i*rad]+halfSize[1:],[0]+[random.random()/2**8 for di in range(dims-1)]],(rad,)*2, 1, ((colours[2 if t==Tralse else 3 if t==Fruse else 4 if t==Trulse else t],
                                                                                                     colours[8+w[0]],
                                                                                                     (63,63,63) if w[0]==0 else weightedAverageColours((w[1],(63,63,63)),(maximumDTM-w[1],angleColour(math.pi*(w[0]-1)/-2))),
                                                                                                     weightedAverageColours((boardWidth/math.sqrt(2)-math.hypot(*s),(63,63,63)),(math.hypot(*s),angleColour(math.atan2(*s)))))
                                                                                                    if mode==0 else ((127,127,127),)*2)] for i,(s,w,t) in enumerate(zip((([i-boardWidth/(4 if manifold==(1,1) and transitivityReduction else 2)+1/2 for i in moddiv(s.index((1,1) if manifold==(1,1) and transitivityReduction else (1,0)),boardWidth)] if mode==0 else [0,0]) for s in theStates()),*((stateWinningnesses,stateTurns) if mode==0 else (range(stateCount),)*2)))] #sorry for inelegance but iterator variables can't be forgone in list comprehensions
    #each formatted [position,size,mass,colours]
    def averageNode():
        return [sum(i[0][0][di] for i in nodes)/len(nodes)-si for di,si in enumerate(halfSize)]
    cameraPosition=[averageNode(),[0.0]*3] #must be 0.0, not 0 (to be float for the lap(float.__add__))
    cameraAngle=[[1/3,-1/6,math.sqrt(3)/2,-1/3],[0]*3] #these values make it point towards the diagram (there are probably ones that aren't askew but I like it (it has soul))
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
            i[0][0]=lap(float.__add__,*i[0])
        for i,(it,k) in enumerate(zip(stateTransitions[:-1],nodes[:-1])): #TypeError: 'zip' object is not subscriptable (I hate it so much)
            for j,(jt,l) in enumerate(zip(stateTransitions[i+1:],nodes[i+1:]),start=i+1):
                differences=lap(float.__sub__,l[0][0],k[0][0])
                gravity=gravitationalConstant/max(2,sum(di**2 for di in differences)**1.5) #inverse-square law is 1/distance**2, for x axis is cos(angle of distance from axis)/(absolute distance)**2, the cos is x/(absolute), so is x/(abs)**3, however the sum outputs distance**2 so is exponentiated by 1.5 instead of 3
                gravity=(gravity*l[2],gravity*k[2])
                for ni,(ki,li,di) in enumerate(zip(k[0][1],l[0][1],differences)): #we are the knights who say ni
                    ins=((j in it,i in jt) if mode==0 else (it==j,jt==i) if mode==1 else (any(j in iti for iti in it),any(i in jti for jti in jt)))
                    if bidirectionalMode:
                        springStrength=any(ins)/2
                    nodes[i][0][1][ni]+=di*(hookeStrength*(springStrength if bidirectionalMode else ins[0])+gravity[0])
                    nodes[j][0][1][ni]-=di*(hookeStrength*(springStrength if bidirectionalMode else ins[1])+gravity[1])

    def quaternionMultiply(a,b):
        return [a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
                a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
                a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
                a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]] #this function not to be taken to before 1843

    def quaternionConjugate(q): #usually conjugation is inverting the imaginary parts but as all quaternion enthusiasts know, inverting all four axes is ineffectual so inverting the first is ineffectually different from inverting the other three 
        return [-q[0]]+q[1:4] #(if you care about memory and not computing power, only the other three need to be stored with their polarities relative to it and the first's sign can be fixed and its magnitude computed (because it's a unit vector))

    def rotateVector(v,q):
        #equivalent to
        #return quaternionMultiply(quaternionMultiply(q,[0]+v),quaternionConjugate(q))[1:]
        #32 lookups and 32 multiplications
        #expands to (when you remove the v[0] components)
        #return [-(q[1]*v[0]+q[2]*v[1]+q[3]*v[2])*q[0]+(q[0]*v[0]+q[2]*v[2]-q[3]*v[1])*q[1]+(q[0]*v[1]-q[1]*v[2]+q[3]*v[0])*q[2]+(q[0]*v[2]+q[1]*v[1]-q[2]*v[0])*q[3], #resolves to 0 (what did nature mean by this)
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

    projectionMode=2*(dims==3)
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
    perspectiveMode=(True and dims==3)
    colourMode=False
    physicsMode=True
    halfConnectionMode=False
    bidirectionalMode=False
    inPlaceBoards=perspectiveMode
    toggleKeys=(pygame.K_SPACE,pygame.K_z,pygame.K_x,pygame.K_c,pygame.K_v)
    oldToggles=[False]*len(toggleKeys)
    run=True
    def normalise(vector):
        magnitude=math.sqrt(sum(map(abs,vector)))
        return (vector if magnitude==0 or magnitude==1 else [i/magnitude for i in vector])
    def average(*vectors):
        l=len(vectors)
        return [sum(i)/l for i in zip(*vectors)]
    while run:
        keys=pygame.key.get_pressed()
        doEvents()
        if perspectiveMode:
            cameraPosition=[lap(float.__add__,*cameraPosition),([0.0]*3 if keys[pygame.K_LSHIFT] else lap(float.__add__,cameraPosition[1],rotateVector(normalise([keys[pygame.K_d]-keys[pygame.K_a],keys[pygame.K_f]-keys[pygame.K_r],keys[pygame.K_w]-keys[pygame.K_s]]),quaternionConjugate(cameraAngle[0]))))]
        else:
            cameraPosition[0]=averageNode()
        toggles=[keys[k] for k in toggleKeys]
        for i,(k,o) in enumerate(zip(toggles,oldToggles)):
            if not k and o:
                if i==0: #space (between turn to move, winningness and DTM)
                    colourMode=(colourMode+1)%(4 if mode==0 else 2)
                elif i==1: #z
                    physicsMode^=True #(because it can be in real time without O(n*(n-1)/2) gravity simulation)
                elif i==2: #x
                    halfConnectionMode^=True
                elif i==3:
                    bidirectionalMode^=True
                elif i==4:
                    inPlaceBoards^=True
        oldToggles=toggles
        if dims==3:
            if mouse.get_pressed()[0]:
                mouseChange=mouse.get_rel()
                mouseChange=(-mouseChange[1],mouseChange[0],0)
            else:
                mouse.get_rel() #otherwise it jumps
                mouseChange=(0,)*3
            cameraAngle[1]=[(di+acc*gain*angularVelocityConversionFactor)/(1+drag) for di,acc in zip(cameraAngle[1],normalise([keys[pygame.K_DOWN]-keys[pygame.K_UP],keys[pygame.K_LEFT]-keys[pygame.K_RIGHT],keys[pygame.K_q]-keys[pygame.K_e]]))]
            cameraAngle[0]=rotateByScreen(cameraAngle[0],[ci+mi for ci,mi in zip(cameraAngle[1],mouseChange)])
        nodeScreenPositions=findNodeScreenPositions()
        #print(nodeScreenPositions)
        renderOrder=range(len(nodes)) if dims==2 else conditionalReverse(perspectiveMode,[j for _, j in sorted((p[2],i) for i,p in enumerate(nodeScreenPositions))]) #perhaps replace with zip(*sorted((p[2],i) for i,p in enumerate(nodeScreenPositions)))[1] (not sure)
        if physicsMode:
            physics()
        for i,(sc,k,n) in enumerate(zip(nodeScreenPositions,stateTransitions,nodes)):
            if mode==0:
                for l in k:
                    drawLine(sc[:2],(average(sc[:2],nodeScreenPositions[l][:2]) if halfConnectionMode else nodeScreenPositions[l][:2]),(colours[7+3+~stateWinningnesses[l][0]] if colourMode==1 else n[3][colourMode]))
            elif mode==2:
                for j,l in enumerate(k):
                    for m in l:
                        drawLine(sc[:2],(average(sc[:2],nodeScreenPositions[m][:2]) if halfConnectionMode else nodeScreenPositions[m][:2]),(cellColours[diceNumbers[stateDice[i]][j]-1] if colourMode==1 else n[3][colourMode]))
            else:
                drawLine(sc[:2],(average(sc[:2],nodeScreenPositions[k][:2]) if halfConnectionMode else nodeScreenPositions[k][:2]),n[3][colourMode])
        if clickDone:
            mousePos=mouse.get_pos()
        for i,j,n,s in [(i,nodeScreenPositions[i],nodes[i],theStates(i)) for i in renderOrder]:
            sezi=2*((j[2] if projectionMode==3 else n[1][0]*minSize/j[2]) if dims==3 and perspectiveMode else n[1][0]) #different from size
            if inPlaceBoards and (sezi>minSize*boardSquares/4096 or not perspectiveMode): #they will not notice if it is smaller, I hope
                renderBoard(s,[],False,sezi,[p-sezi/2 for p in j[:2]])
            else:
                drawShape(sezi,j[:2],n[3][colourMode],5)
                if clickDone and i!=boardLastPrinted and sum((ji-mi)**2 for ji,mi in zip(j,mousePos))<n[1][0]**2:
                    printBoard(s)
                    boardLastPrinted=i
    else: exit()
