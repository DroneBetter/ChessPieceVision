from itertools import groupby
from functools import reduce
'''from itertools import accumulate
redumulate=(lambda f,i,init=None: accumulate(i,f,initial=init))'''
class reducer:
    conditionalReverse=(lambda self,reversal,toBe: reversed(toBe) if reversal else toBe)
    conditionalTranspose=(lambda self,transpose,x,y: x*boardWidth+y if transpose else y*boardWidth+x) #to prevent having to reiterate in each instance or use the less efficient x*boardWidth**(transpose)+y*boardWidth**(1^transpose) (to avoid having to allocate x and y to variables or recompute them)
    ORsum=(lambda self,l: reduce(int.__or__,l,0))
    boardStr=(lambda self,board,inner=True,b='b',o='o',j='\n': j.join((lambda i: "".join(o if i>>self.cellWidth*j&1 else b for j in range(inner,i.bit_length()//self.cellWidth+2-inner)))(board>>(self.cellWidth*self.WIDTH*i if self.OT or self.byteINT else 3*self.WIDTH*(i*3+1)+1)&(1<<self.cellWidth*self.WIDTH)-1) for i in range(inner,self.WIDTH-inner)))
    RLE=(lambda self,board,inner=True,includeRule=False: ("x ="+str(boardWidth)+", y = "+str(boardHeight)+", rule = "+RLErulestring+'\n' if includeRule else '')+''.join((lambda l,q: l*2 if self.niemiec and q==2 else l if q==1 else str(q)+l)(l,len(list(q))) for l,q in groupby(self.boardStr(board,inner,'b','o','$') if self.bitwise else '$'.join(''.join('o' if l else 'b' for l in board[b*boardWidth:(b+1)*boardWidth]) for b in range(boardWidth-1,-1,-1))))+'!')
    def print(self,board,chequerboard=False,delimit=True,multiple=False,spaces=False): #British English program (god save the king)
        part=(lambda board,b: (" "*spaces).join(("_" if letter==" " else letter+'\u0332') if (i+b)%2==0 and chequerboard else letter for i,letter in enumerate(["o" if s else " " for s in map(((lambda s: board>>self.BIAS+s//boardWidth*self.cellBits*self.WIDTH+s%boardWidth*self.cellWidth&1) if self.bitwise else board.__getitem__),range((b-1)*boardWidth,b*boardWidth))])))
        print(( "".join("["*(b==boardWidth)+(" [" if b==boardWidth else "] " if b==1 else "  ").join(part(subboard,b) for subboard in board)+(("]\n" if b==1 else "\n ") if delimit else "\n") for b in range(boardWidth,0,-1))
               if multiple else
                "["*delimit+"".join(part(board,b)+(("]\n" if b==1 else "\n ") if delimit else "\n") for b in range(boardWidth,0,-1))+"\033["+str(boardWidth)+"B"),end="") #ANSI escape sequences
    def setBoardWidth(self,n,new=False):
        global boardWidth,boardSquares,halfWidth,centre,unreflectedLayerIndices,layerTypes,stateNumber
        boardWidth=n
        boardSquares=boardWidth**2
        halfWidth=(boardWidth-1)//2
        centre=(boardSquares-1)/2
        if boardWidth%2:
            centre=int(centre) #>mfw no int= operator
        (unreflectedLayerIndices,layerTypes)=zip(*[(self.layerIndices(x,y),self.layerType(x,y)) for x in range(halfWidth+1) for y in range(x+1)])
        if self.bitwise:
            self.WIDTH=self.HEIGHT=boardWidth+2
            self.COLSHIFT=self.cellBits*self.WIDTH
            self.WRAPSHIFT=self.COLSHIFT*boardWidth
            self.unitNeighbourhood=((1<<self.cellWidth)-1)*self.ORsum(1<<self.COLSHIFT*i for i in range(self.cellHeight))
            self.lastColumn=self.ORsum(self.unitNeighbourhood<<i*self.COLSHIFT for i in range(self.HEIGHT))
            self.lastRow=self.ORsum(self.unitNeighbourhood<<self.cellWidth*i for i in range(self.WIDTH))
            self.BIAS=((self.WIDTH+1)*self.cellWidth if self.OT or self.byteINT else (self.WIDTH*self.cellBits+1)*4)

    layerIndices=(lambda self,x,y: ([centre] if x==0 else #a perfect place                                                                                                                #1, on 1*1 board is [(0,0)]
                               [centre+x*p*(boardWidth if skewedness else 1) for skewedness in range(2) for p in range(-1,3,2)] if y==0 else                                         #2, on 3*3 board is [(0,1),(2,1),(1,0),(1,2)]
                               [centre+x*(xp+yp*boardWidth) for xp in range(-1,3,2) for yp in range(-1,3,2)] if y==x else                                                            #3, on 3*3 board is [(0,0),(0,2),(2,0),(2,2)]
                               [centre+self.conditionalTranspose(skewedness,x*xp,y*yp) for skewedness in range(2) for xp in range(-1,3,2) for yp in range(-1,3,2)]) if boardWidth%2 else  #0, on 5*5 board is [(0,1),(0,3),(4,1),(4,3),(1,0),(3,0),(1,4),(3,4)]
                              ([int(centre+(x+0.5)*xp+(y+0.5)*yp*boardWidth) for xp in range(-1,3,2) for yp in range(-1,3,2)] if y==x else #very suspicious indeed                   #3, on 2*2 board is [(0,0),(0,1),(1,0),(1,1)]
                               [int(centre+self.conditionalTranspose(skewedness,(x+1/2)*xp,(y+1/2)*yp)) for skewedness in range(2) for xp in range(-1,3,2) for yp in range(-1,3,2)]))#0, on 4*4 board is [(0,1),(0,2),(3,1),(3,2),(1,0),(2,0),(1,3),(2,3)]
    layerType=(lambda self,x,y: (1 if x==0 else 2 if y==0 else 3 if y==x else 0) if boardWidth%2 else (3 if y==x else 0))
    layerPriorities=(lambda layer,type: self.instanceReflectionPriorities[type][self.ORsum(l<<i for i,l in enumerate(layer))])
    def constructCellular(self,layers):
        if self.bitwise:
            return(self.ORsum((l>>i&1)<<(j%boardWidth*self.cellWidth+j//boardWidth*self.COLSHIFT+self.BIAS) for k,l in zip(unreflectedLayerIndices,layers) for i,j in enumerate(k)))
        else:
            output=[False]*boardSquares
            '''liter=iter(layers)
            for i,l in ((i,l) for x in range(halfWidth+1) for y in range(x+1) for i,l in zip(layerIndices(x,y),next(liter))): #next(liter) can be layers[x*(x+1)/2+y-1], I think
                output[i]=l'''
            for k,l in zip(unreflectedLayerIndices,layers):
                for i,j in enumerate(k):
                    output[j]=l>>i&1
            return(tuple(output))

    setLayers=(lambda self,state: (lambda layers: (layers,[self.ORsum(m<<i for i,m in enumerate(l)) for l in layers]))([list(map((lambda l: state>>self.BIAS+l%boardWidth*self.cellWidth+l//boardWidth*self.COLSHIFT&1) if self.bitwise else state.__getitem__,l)) for l in unreflectedLayerIndices]))
    def symmetry(self,state,reflectionMode=0):
        if self.symmetryReduction:
            (layers,layerNumbers)=self.setLayers(state)
            newReflections=(1<<8)-1
            l=0
            while l<len(layers):
                newReflections&=self.instanceReflectionAllowednesses[layerTypes[l]][layerNumbers[l]]
                if newReflections:
                    reflections=newReflections
                    l+=1
                else:
                    break
            while l<len(layers):
                m=min(p for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][layerNumbers[l]]) if reflections>>i&1)
                newReflections=reflections&self.ORsum((p==m)<<i for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][layerNumbers[l]])) #may produce multiple but they will all yield the same board
                reflections=newReflections
                if not reflections&reflections-1: #power of 2
                    break
                l+=1
            reflections=next(tuple(i>>a&1 for a in range(3)) for i in range(8) if reflections>>i&1)
        else:
            reflections=(False,)*3
        return reflections if reflectionMode==2 else (self.compoundReflect(state,reflections),reflections) if reflectionMode==1 else self.compoundReflect(state,reflections)
    def generateCellular(self,state,ind):
        if self.symmetryReduction:
            (layers,layerNumbers)=self.setLayers(state)
            branchReflections=reduce(lambda li,i: li+[(lambda li,arm,t,n: (li[-1]&(lambda pr,m: self.ORsum((p==m)<<i for i,p in enumerate(pr)))(*(lambda pr: (pr,min(p for i,p in enumerate(pr) if arm==0 or li[-1]>>i&1)))(self.instanceReflectionPriorities[t][n]))))(li,i[0],*i[1])],enumerate(zip(layerTypes,layerNumbers)),[(1<<8)-1])[1:]#[(1<<8)-1]*len(layerNumbers)
            arm=len(layerNumbers)-1
            #elbow=arm #layer at which it switches from instanceReflectionAllowednesses to self.instanceReflectionPriorities
            for i in range(ind[1]-ind[0]):
                arm=len(layerNumbers)-1
                yield(self.constructCellular(layerNumbers))
                while True:
                    while arm>=0 and layerNumbers[arm]==(1 if layerTypes[arm]==1 else 2**self.typeLengths[layerTypes[arm]]-1):
                        layerNumbers[arm]=0
                        del branchReflections[-1]
                        arm-=1
                    if arm<0:
                        break
                    else:
                        layerNumbers[arm]+=1
                        m=min(p for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[arm]][layerNumbers[arm]]) if len(branchReflections)<=1 or branchReflections[-2]>>i&1)
                        #print(tuple(map(bin,branchReflections)),self.instanceReflectionPriorities[layerTypes[arm]][layerNumbers[arm]],self.ORsum((p==m)<<i for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[arm]][layerNumbers[arm]]) if arm==0 or branchReflections[-2]>>i&1))
                        if (#instanceReflectionAllowednesses[layerTypes[arm]][layerNumbers[arm]]&1 if arm<elbow else 
                            self.instanceReflectionPriorities[layerTypes[arm]][layerNumbers[arm]][0]==m): #legal
                            break
                if arm<0:
                        break
                branchReflections[-1]=((1<<8)-1 if arm==0 else branchReflections[-2])&self.ORsum((p==m)<<i for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[arm]][layerNumbers[arm]])) #formerly &ed by instanceReflectionAllowednesses[layerTypes[arm]][layerNumbers[arm]]
                wibble=(len(layerNumbers)+~arm)
                branchReflections+=[branchReflections[-1]]*(len(layerNumbers)+~arm)
                #print(tuple(map(bin,branchReflections)),wibble)
        else:
            for i in range(ind[1]-ind[0]):
                yield(state)
                j=0
                state[0]^=True
                while not state[j] and j<boardCells-1:
                    j+=1
                    state[j]^=True
    """for i in range(1,8):
        setBoardWidth(i)
        print(len(generateCellular()))#;exit()
        '''if i<4:
            for j in generateCellular():
                print(j==symmetry(j))
                #if j!=symmetry(j):
                print(j)'''"""

    def polya(self,layer,reflections):
        cellTypes=[0]*4
        for l in layerTypes[layer+1:]: #(1 if x==0 else 2 if y==0 else 3 if y==x else 0)
            cellTypes[l]+=self.typeLengths[l]
        n=0
        s=0
        for i in range(8):
            if reflections>>i&1:
                n+=1
                s+=2**(sum(cellTypes) if i==0 else cellTypes[1]+((3*cellTypes[2]+2*cellTypes[3]+2*cellTypes[0])//4 if i==1 or i==2 else (cellTypes[2]+cellTypes[3]+cellTypes[0])//2 if i==3 else (2*cellTypes[2]+3*cellTypes[3]+2*cellTypes[0])//4 if i==4 or i==7 else (cellTypes[2]+cellTypes[3]+cellTypes[0])//4)) #(boardWidth*(--0--boardWidth//2) if i==1 or i==2 else (n**2+n%2)//2 if i==3 else boardWidth*(boardWidth+1)//2 if i==4 or i==7 else n//2*(--0--n//2)+n%2)
        return(s//n if n else 0)

    def index(self,state):
        if self.symmetryReduction:
            state=self.symmetry(state)
            (layers,layerNumbers)=self.setLayers(state)
            reflections=(1<<8)-1
            stateIndex=0
            l=0
            while l<len(layers):
                for n in range(layerNumbers[l]+1):
                    m=min(p for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][n]) if reflections>>i&1)
                    if self.instanceReflectionPriorities[layerTypes[l]][n][0]==m: #legal
                        newReflections=reflections&self.ORsum((p==m)<<i for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][n])) #may produce multiple but they will all yield the same board
                        if n<layerNumbers[l]:
                            stateIndex+=self.polya(l,newReflections)
                        else:
                            break
                reflections=newReflections
                l+=1
            return(stateIndex)
        else:
            return(reduce(int.__or__,(1<<i&s for i,s in enumerate(state))))
    def getter(self,ind):
        if self.symmetryReduction:
            layerNumbers=[0 for l in range(len(layerTypes))]
            newReflections=reflections=(1<<8)-1
            stateIndex=0
            l=0
            while l<len(layerNumbers):
                for n in range(2**self.typeLengths[layerTypes[l]]):
                    m=min(p for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][n]) if reflections>>i&1)
                    if self.instanceReflectionPriorities[layerTypes[l]][n][0]==m: #legal
                        newNewReflections=reflections&self.ORsum((p==m)<<i for i,p in enumerate(self.instanceReflectionPriorities[layerTypes[l]][n])) #may produce multiple but they will all yield the same board
                        nextIndex=stateIndex+self.polya(l,newNewReflections)
                        newReflections=newNewReflections
                        layerNumbers[l]=n
                        if nextIndex>ind:
                            break
                        else:
                            stateIndex=nextIndex
                reflections=newReflections
                l+=1
            return(self.constructCellular(layerNumbers))
        else:
            return(tuple(bool(ind>>j&1) for j in range(boardSquares)))
    def __getitem__(self,ind):
        if type(ind)==slice:
            ind=ind.indices(len(self))
            if ind[2]!=1:
                raise(ValueError("you WILL NOT use increments other than 1"))
            state=self.getter(ind[0])
            return(self.generateCellular(state,ind)) #used because including yield statements in the __getitem__ function itself will cause the return statement (for integer indexes) not to work and for it to be interpreted as generator
        else:
            return(self.getter(ind))
    __len__=(lambda self: self.length)
    def __init__(self,boardWidth,reduction=True,bitwise=True,cellWidth=4,cellHeight=1,OT=True,byteINT=True):
        self.bitwise=bitwise;self.cellWidth=cellWidth;self.cellHeight=cellHeight;self.cellBits=cellWidth*cellHeight;self.OT=OT;self.byteINT=byteINT
        self.symmetryReduction=reduction
        self.setBoardWidth(boardWidth,True)
        self.positionReflect=(lambda self,position,axis: boardWidth+~position+position//boardWidth*boardWidth*2 if axis==0 else position%boardWidth+(boardWidth+~position//boardWidth)*boardWidth if axis==1 else position//boardWidth+(position%boardWidth)*boardWidth if axis==2 else position)
        self.compoundPositionReflect=(lambda self,position,axes,reverse=False: ( ( ( (position+1)*boardWidth+~((boardSquares+1)*(position//boardWidth)))
                                                                               if axes[reverse] else
                                                                                ( boardWidth*(boardWidth+~position)+(1+boardSquares)*(position//boardWidth)))
                                                                             if axes[0]^axes[1] else
                                                                              ( ( ((1-boardSquares)*~(position//boardWidth)-position*boardWidth))
                                                                               if axes[0] else
                                                                                position*boardWidth-(boardSquares-1)*(position//boardWidth))) #position//boardWidth+position%boardWidth*boardWidth=position*boardWidth-(boardSquares-1)*position//boardWidth
                                                                         if axes[2] else
                                                                          ( ( (boardSquares+~position) #(boardWidth-position//boardWidth)*boardWidth+(boardWidth-position%boardWidth)=boardSquares+boardWidth-position
                                                                             if axes[0] else
                                                                              position+boardWidth*(boardWidth+~(2*(position//boardWidth))))
                                                                           if axes[1] else
                                                                            ( boardWidth*(1+2*(position//boardWidth))+~position #position=position%boardWidth+position//boardWidth*boardWidth, so position//boardWidth*boardWidth=position-position%boardWidth, so boardWidth+~position%boardWidth+position//boardWidth*boardWidth=boardWidth+~position%boardWidth+position-position%boardWidth=boardWidth+~2*position%boardWidth+position=boardWidth+~(2*position%boardWidth)+position=~position+boardWidth*(1+2*position//boardWidth)
                                                                             if axes[0] else
                                                                              position))) #some are probably reducible further (depending on whether floor division or modulo is more efficient, but also probably regardless)
        self.shift=(lambda i: '>>'+str(i) if i>0 else '' if i==0 else '<<'+str(-i))
        self.boardReflect=eval( "lambda board,axis: board if axis==-1 else "+''.join('|'.join(f)+(' if axis=='+str(i)+' else ')*(i!=2) for i,f in enumerate((("(board&"+str(self.lastColumn<<self.cellWidth*i)+')'+self.shift(self.cellWidth*(i-(self.WIDTH+~i))) for i in range(self.WIDTH)),
                                                                                                                                                        ("(board&"+str(self.lastRow<<self.COLSHIFT*i)+')'+self.shift(self.COLSHIFT*(i-(self.HEIGHT+~i))) for i in range(self.HEIGHT)),
                                                                                                                                                        ("(board&"+str((lambda x: (x,self.print(x))[0])(self.ORsum(1<<self.cellWidth*(i+(self.WIDTH+1)*j)&self.lastRow<<self.COLSHIFT*j for j in range(self.WIDTH) if i+(self.WIDTH+1)*j>0)))+')'+self.shift(self.cellWidth*(-i*(self.WIDTH-1))) for i in range(1-self.WIDTH,self.WIDTH))))) #inelegant but only runs once :-)
                                                                                                                                                        #("(board&"+str((lambda x: (x,self.print(x))[0])(self.ORsum(1<<self.cellWidth*(i+self.WIDTH+(self.WIDTH-1)*j)&self.lastRow<<self.COLSHIFT*j for j in range(self.WIDTH) if i>(1-self.WIDTH)*j)))+')'+self.shift(self.cellWidth*(i*(self.WIDTH+1)+1)) for i in range(1-self.WIDTH,self.WIDTH)))))) #original accidental y=WIDTH+~x version (could be used if I am one day no longer too lazy to make closed forms for each compoundReflect)
                               if self.bitwise else
                                "lambda board,axis: board if axis==-1 else "+''.join('('+','.join('board['+str(j)+']' for j in l)+')'+(' if axis=='+str(i)+' else ')*(i!=2) for i,l in enumerate(((x for y in range(boardWidth) for x in range((y+1)*boardWidth-1,y*boardWidth-1,-1)),
                                                                                                                                                                                             (x for y in range(boardWidth,0,-1) for x in range((y-1)*boardWidth,y*boardWidth)),
                                                                                                                                                                                             (x for y in range(boardWidth) for x in range(y,y+boardSquares,boardWidth))))))
        self.compoundReflect=(lambda board,axes: board if axes==(0,0,0) else reduce(self.boardReflect,(i for i,a in enumerate(axes) if a),board) if self.bitwise else tuple(x for y in self.conditionalReverse(axes[not axes[2]],range(boardWidth)) for x in self.conditionalReverse(axes[axes[2]],(board[y:y+boardSquares:boardWidth] if axes[2] else board[y*boardWidth:(y+1)*boardWidth]))))
        self.intState=(lambda state: self.ORsum((state&1<<i)<<(self.BIAS+i%boardWidth*self.cellWidth+i//boardWidth*self.COLSHIFT-i) for i in range(boardSquares)) if self.bitwise else tuple(bool(state>>i&1) for i in range(boardSquares)))
        self.niemiec=True
        self.length=( ( (((2**boardSquares+2**((boardSquares+1)//2))//2+2**((boardSquares+3)//4))//2+2**((boardSquares+boardWidth)//2))//2
                       if boardWidth%2 else #from https://oeis.org/A054247 (my beloved)
                        ((2**(boardSquares-1)+3*2**(boardSquares//2-1))+2**(boardSquares//4)+2**((boardSquares+boardWidth)//2))//4)
                     if self.symmetryReduction else
                      2**boardSquares)
        self.typeLengths=(8,1,4,4)
        self.typeBits=(3,0,2,2)
        #this part not optimised but only needs to run once
        #generate (requires boardWidth be 5)
        '''def layerBoard(layer,layerIndices):
            board=[False]*boardSquares
            for n,m in enumerate(layerIndices):
                board[m]=bool(layer>>n&1)
            return(board)
        instances=[[layerBoard(n,i) for n in range(2**l)] for i,l in ((unreflectedLayerIndices[layerTypes.index(i)],l) for i,l in enumerate(typeLengths))]
        print(list(map(list.__len__,instances)))
        self.instanceReflectionPriorities=[[[l.index(f) for f in j] for j,l in zip(i,[sorted(set(j)) for j in i])] for i in [[[compoundReflect(j,[f>>r&1 for r in range(3)]) for f in range(8)] for j in [layerBoard(n,unreflectedLayerIndices[layerTypes.index(i)]) for n in range(2**l)]] for i,l in enumerate(typeLengths)]]
        instanceReflectionAllowednesses=[[self.ORsum((l==0)<<i for i,l in enumerate(j)) for j in i] for i in self.instanceReflectionPriorities]
        def equation(name,ins,nestedness):
            print(name+"=("+(str(ins) if nestedness==0 else ",".join(map(str,ins) if nestedness==1 else (("("+",".join(map(str,i) if nestedness==2 else ("("+",".join(map(str,j))+")" for j in i))+")") for i in ins)))+")")
        #print([[max(j) for j in i] for m,i in enumerate(self.instanceReflectionPriorities)])
        #equation("instanceReflectionAllowednesses",instanceReflectionAllowednesses,2)
        equation("instanceReflectionAllowednesses",[self.ORsum(l<<(8*i) for i,l in enumerate(j)) for j in instanceReflectionAllowednesses],0)
        print(tuple(map(tuple,instanceReflectionAllowednesses))==tuple(tuple((i>>(8*l))&((1<<8)-1) for l in range(2**t)) for t,i in zip(typeLengths,[self.ORsum(l<<(8*i) for i,l in enumerate(j)) for j in instanceReflectionAllowednesses])))
        equation("self.instanceReflectionPriorities",self.instanceReflectionPriorities,3)
        equation("self.instanceReflectionPriorities",tuple(tuple(tuple(j>>(typeBits[m]*l)&(typeLengths[m]-1) for l in range(8)) for j in i) for m,i in enumerate(((self.ORsum(k<<(typeBits[m]*l) for l,k in enumerate(j)) for j in i) for m,i in enumerate(self.instanceReflectionPriorities)))),3)
        equation("self.instanceReflectionPriorities",((self.ORsum(k<<(typeBits[m]*l) for l,k in enumerate(j)) for j in i) for m,i in enumerate(self.instanceReflectionPriorities)),2)
        print(tuple(map(lambda n: tuple(map(tuple,n)),self.instanceReflectionPriorities))==tuple(tuple(tuple(j>>(typeBits[m]*l)&(typeLengths[m]-1) for l in range(8)) for j in i) for m,i in enumerate(((self.ORsum(k<<(typeBits[m]*l) for l,k in enumerate(j)) for j in i) for m,i in enumerate(self.instanceReflectionPriorities)))))'''
        self.instanceReflectionAllowednesses=tuple(tuple((i>>(8*l))&((1<<8)-1) for l in range(2**t)) for t,i in zip(self.typeLengths,(0xff104050203060108090c040a02080f001114010010101108101401020202010020242102202021080028010202020200301011102030201020103012202020304104440241004400404044080808040051040500111401004104440a0208050061040402002664080960440202020600101011002010211020101102002220108180840202008408808084080808080091040102001691080990810808080900a0208502022201080808840a02080a0020101100202020102010211202220020c040444080c040408080c048808080c04040440080404400808044480880804080404400808044408080804808088080f0104500203061008090c40a02080ff,0xffff,0xff50a0f0031122030c44880c0f50a0ff,0xff1144502203661188990c44a02288ff)))
        self.instanceReflectionPriorities=tuple(tuple(tuple(j>>(self.typeBits[m]*l)&(self.typeLengths[m]-1) for l in range(8)) for j in i) for m,i in enumerate(((0,1635557,3959123,799370,12818092,4829193,5087304,10154067,15141658,6894081,7152192,12477633,6390865,13881882,16205448,2396160,5361783,569427,1889510,1635557,9122351,5169255,5943399,5927005,6361619,11362855,12402782,10055773,12822117,13353501,13869597,10154067,9089598,5365885,827482,1667820,4297242,7033404,7807100,5927019,14849716,13226556,16130611,10055787,12818092,13353515,13869611,13881882,2433051,5361783,3522743,569427,9089598,2433051,5419134,5361783,10892350,9032247,4755483,7430255,4297242,9089598,9380413,2433051,7687617,3438995,2892993,3959123,4555976,5437313,5945800,6186817,13511624,11364801,12138945,10315585,15403353,15419208,15935304,12477633,267475,1111390,3950485,799370,6493543,340107,1979285,1700629,12945877,9205070,4985538,8152396,6390410,13091029,15930691,5058625,296154,1111411,1886122,1893731,8881523,2838843,294984,1958698,15075242,2101320,12130272,8152417,13076266,12825386,13600097,5087304,571767,841015,1357111,1635557,6460734,2773239,3547390,569427,10589502,8966391,7611191,5796581,10720500,8827070,4554842,5361783,11415432,2635393,7950145,6056715,10980634,9166024,7810824,6187713,6620808,13229825,14003976,10316481,15141658,15420104,15936200,16205448,2102931,3177118,3951829,3700949,8624798,4646943,295425,1701973,14818517,2101761,13938372,7895692,14883484,14891093,15665804,6894081,2131610,846524,3686186,799825,8624819,2204697,7572145,3831338,15076586,14797930,6850128,10283672,6390865,12826730,15665825,6922760,4299582,841911,1358007,1373862,6461630,4638270,5412414,3265591,10590398,10831415,11339902,2634259,12818092,4297242,13338220,9089598,4757184,7396802,7687617,2892993,9346960,2434752,7744968,5884865,11415432,11358081,4757184,7687617,6620808,13254472,11415432,4757184,2895333,2907604,3423700,3959123,6721428,646604,3550659,1927499,10850196,8970115,9743811,2892993,15109395,6362753,11411330,7687617,6623148,2907618,3423714,3955098,6721442,4374433,5414360,828616,10850210,10833816,11607960,7654864,15141658,14887705,6620808,11415432,585,571767,2895333,799370,4299582,38043,296154,1635557,6623148,2102931,2361042,3959123,6390865,12818092,15141658,0),(0,0),(0,13158,52377,21760,23055,10011,36174,23055,42480,29361,55524,42480,85,13158,52377,0),(0,10011,29361,13158,36174,23055,5140,10011,55524,16705,42480,29361,52377,36174,55524,0))))

if __name__=='__main__':
    r=reducer(4)
    print(len(r))
    print([i for i in r[1:3]])
    import time
    present=time.time() #not anymore
    print("generating cellular")
    states=list(r[:])
    #print(states)
    print("cellular generated",time.time()-present)
    print('')
    #(lambda r: (lambda r,l: (print(l),r.print([i for i in r[l//2:l//2+4]],multiple=True),r.print(tuple(r.boardReflect(r[l//2],i) for i in range(-1,3)),multiple=True)))(r,len(r)))(reducer(8));exit()
    '''present=time.time() #no longer
    print("generating Pólyas")
    polyas=list(map(index,states))
    print("Pólyas generated",time.time()-present)'''
    '''polyas=list(map(states.index,(r[s] for s in range(len(states)))))
    import matplotlib.pyplot as plot
    x=range(len(polyas))
    if False:
        plot.plot(x,polyas)
    else:
        plot.plot(*list(map(lambda n: reduce(tuple.__add__,((i,)*2 for i in n)),(x,polyas))))
        plot.plot(*list(map(lambda n: reduce(tuple.__add__,((i,)*2 for i in n)),(x,)*2)))
    plot.show()
    exit()'''
    #print(list(map(int.__sub__,range(len(states))),polyas));exit()
    import random
    while True:
        i=0
        while i==0 or r.symmetry(state)==r.symmetry(r.symmetry(state)):
            state=r.intState(random.getrandbits(boardSquares))
            print("wibble")
            print(r.RLE(state))
            r.print(state)
            print("wibble",r.__getitem__(states.index(r.symmetry(state))))
            print(r.RLE(r[states.index(r.symmetry(state))]))
            r.print(r[states.index(r.symmetry(state))])
            print(states.index(r.symmetry(state)),r.index(state))
            '''print(state)
            print(symmetry(state))
            print(symmetry(symmetry(state)))'''
            #print(len(set(map(symmetry,(compoundReflect(state,i) for i in ([i>>n&1 for n in range(3)] for i in range(8)))))))
            #print(list(set(map(symmetry,(compoundReflect(state,i) for i in ([i>>n&1 for n in range(3)] for i in range(8)))))),multiple=True)
            if len(set(map(r.symmetry,(r.compoundReflect(state,i) for i in ([i>>n&1 for n in range(3)] for i in range(8))))))!=1:
                print("resultants")
                for n in [compoundReflect(state,[i>>n&1 for n in range(3)]) for i in range(8)]:
                    print((n,symmetry(n)),multiple=True)
                    print("")
            '''for n in set(map(symmetry,(compoundReflect(state,i) for i in ([i>>n&1 for n in range(3)] for i in range(8))))):
                print(n)'''
            i+=1
        break
        #print(i)
