from functools import reduce
from itertools import accumulate,pairwise

dbg=(lambda x,*s: (x,print(*s,x))[0]) #debug
revange=(lambda a,b=None,c=1: range(b-c,a-c,-c) if b else range(a-c,-c,-c)) #(lambda *a: reversed(range(*a)))
tap=(lambda func,*iterables: tuple(map(func,*iterables)))
redumulate=(lambda f,l,i=None: accumulate(l,f,initial=i)) #I did (lambda f,l,i=None,accum=False: (accumulate(l,f) if accum else reduce(f,l)) if i==None else (accumulate(l,f,initial=i) if accum else reduce(f,l,i))) but then I didn't use the reduce mode (I don't suppose it comes up much)
funcxp=(lambda f,l: lambda i: reduce(lambda x,i: f(x),range(l),i)) #short for funcxponentiate
construce=(lambda f,l,i=None: reduce(lambda a,b: f(*a,b),l,i)) #reduce for constructing tuple, typically with range (you cannot unpack parameters directly in lambda arguments)
decompose=(lambda n,l=None: (n>>i&1 for i in range(n.bit_length() if l==None else l)) if type(n)==int else chain(*n))
strint=(lambda state,l=None: ''.join(map(lambda o: 'o' if o else ' ',decompose(state,l))))
def iindex(s,i,d=None): #AttributeError: 'map' object has no attribute 'index' :-(
    try:
        n=0
        j=next(s)
        while j!=i:
            n+=1
            j=next(s)
        return(n)
    except StopIteration: return(n if d==None else d)
def whilexp(f,c): #funcxp but with a condition instead
    def g(i):
        while c(i):i=f(i)
        return(i)
    return(g)
def redwhile(f,c,l,i=None): #reduce but with a condition also
    if i==None: i=next(l)
    while c(i): i=f(i,next(l))
    return(i)
'''def shortduce(f,c,l,i=None,o=None,b=None): #separate condition
    if i==None: i=next(l)
    if c(i): return(b(i))
    for j in l:
        i=f(i,j)
        if c(i): return(b(i))
    return(o(i))'''
def shortduce(f,l,i=None,o=None,b=None): #redwhile but with different function depending on shortcut (second element is used only as whether to proceed)
    if i==None: i=next(l)
    i=(i,True)
    for j in l:
        if i[1]: i=f(i[0],j)
        else: return(i[0] if b==None else b(i[0]))
    return((lambda f,i: i if f==None else f(i))(o if i[1] else b,i[0]))

andMasks=(lambda n: (lambda bitWidth: tuple(reduce(lambda n,j: n|n<<(1<<j),range(i+1,bitWidth),(1<<(1<<i))-1) for i in range(bitWidth)))((n-1).bit_length()))

class twofold:
    def __init__(self,n):
        self.n=n
        self.length=(1<<(--0--n//2)|1<<n)>>1
        #from reversalParameters in https://gist.github.com/DroneBetter/4f5d775e7c37f062ce750d4a8fefc84a (not sure how else to define instance-specific open-form function (which it must be due to in-places))
        masks=[[[m,1<<i,False],[m,0,True]] for i,m in enumerate(andMasks(n))]
        exceeding=(1<<(n-1).bit_length())-n
        if exceeding:
            endShifts=[-exceeding//2,exceeding//2]
            for i,m in enumerate(masks):
                #print(m[0][1])
                shifter=(lambda i,m: min(m[0][1],m[0][1]-2*(1<<i),key=abs))
                if -endShifts[0]<=shifter(i,m): m[0][1]+=endShifts[0]; m[1][0]>>=-endShifts[0]; break
                else:
                    m[0][0]>>=m[0][1]-endShifts[0]; m[0][1]-=endShifts[0]; m[0][2]=True; m[1][0]>>=-endShifts[0]
                    common=(shifter(i,m) if m[0][1]^(m[0][1]-2*(1<<i))>0 else 0)
                    if common:
                        endShifts[0]=-common
                        if endShifts[0]<m[0][1]: m[0][1]=0
                    else: break
            masks[-1][0][0]>>=endShifts[1]; masks[-1][0][1]+=endShifts[1]
        for i,m in enumerate(masks): m[1][1]=m[0][1]-2*(1<<i)
        conditionalSwap=(lambda x,b,t,f,br: '('*br+x+(t+')'*br+f if b else f+')'*br+t))
        indent=(lambda i,t: " "*((i-len(t))*(i>len(t)))+t)
        marge=[0,0]#[max(len(str((abs if i else hex)(n[i]))) for m in masks for n in m) for i in range(2)]
        self.reverse=eval(dbg(("lambda x: "+"".join("(lambda x: "+'|'.join(conditionalSwap('x',(n[2] and n[1]),"&"+indent(marge[0],str(hex(n[0]))),((">>" if n[1]>0 else "<<")+indent(marge[1],str(abs(n[1]))) if n[1] else ' '*(2+marge[1])),(n[1] and n[2])) for n in m)+')(' for m in masks[::-1])+'x'+')'*len(masks))))

    __len__=(lambda self: self.length)
    strate=(lambda self,s: strint(s,self.n))
    #layer=(lambda self,s,i: s>>(i-1)&2|s>>self.n+~i&1 if i else s<<1&2|s>>self.n-1&1) #no negative shift amounts :-( #terrible
    layer=(lambda self,s,i: s>>i&1|s>>self.n-i-2&2)
    layinc=(lambda self,s,b,i: (lambda l: ((s&~(1<<i|1<<self.n+~i),b),True) if l==3 else ((((s|1<<i,i if i==b+1 else b) if l==2 else (s&~(1<<i)|1<<self.n+~i,b) if l else (s|1<<i,b)) if i>b else (s|1<<self.n+~i,b)) if l else (s|1<<i,min(i,b)),False))(self.layer(s,i))) #2 cannot be reached in layers under symmetry
    branch=(lambda self,s: (lambda i: i+(i==self.n//2 and self.n&1))(iindex(map(lambda i: s>>i&1^s>>self.n+~i&1,range(self.n//2)),1)))
    symmetry=(lambda self,s: funcxp(self.reverse,(lambda b: b<=self.n//2 and self.layer(s,b)==2)(self.branch(s)))(s))
    nexter=(lambda self,s,b: (s|1<<self.n//2,b) if self.n&1 and not s&1<<self.n//2 else shortduce(lambda s,i: self.layinc(*s,i),revange(self.n//2),(s&~(1<<self.n//2) if self.n&1 else s,b))) #internal (for conserving the branch output in between)
    __next__=(lambda self,s: self.nexter(s,self.branch(s))[0]) #will loop upon itself endlessly (I hate StopIteration)
    #__iter__=(lambda self: redumulate(lambda s,i: t.__next__(s),range(len(self)-1),0)) #trivial implementation
    __iter__=(lambda self,l=None,u=None: map(lambda i: i[0],redumulate(lambda s,i: t.nexter(*s),range((len(self) if u==None else u if l==None else u-l)-1),(0,self.n) if l==None else (lambda s: (s,self.branch(s)))(self[l])))) #does not compute branch
    #polya=(lambda self,l,i,b: (3<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+(((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1)))>>1)) if l==3 else (2<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l==2 else (1<<(self.n&~1)-2*(i+1) if i>b else ((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l else 0)
    polya=(lambda self,l,i,b: l<<(self.n&~1)+(~i<<1) if b else (1<<(self.n&~1)+~i)*(l==2)+(l<<(self.n&~1)+(~i<<1))+(1<<(self.n>>1)+~i)>>1 if l else 0)
    index=(lambda self,s,sym=True: (lambda s: (lambda b: sum(map(lambda i: self.polya(self.layer(s,i),i,i>b),range(self.n>>1)))<<(self.n&1)|self.n&s>>(self.n>>1)&1)(self.branch(s)))(funcxp(self.symmetry,sym)(s)))
    #__getitem__=(lambda self,i: reduce(lambda s,i: t.__next__(s),range(i-1),0)) #also trivial (and slow)
    __getitem__=(lambda self,j: self.__iter__(j.start,j.stop) if type(j)==slice else (lambda f: f(j>>1)[0]|(j&1)<<self.n//2 if self.n&1 else f(j)[0])(lambda j: construce(lambda s,j,b,i: (lambda k,m: (s|(k&1)<<i|(k&2)<<(self.n+~i-1),j-m,b|(k&1^k>>1)))(*next(filter(lambda r: r[0][1]<=j<r[1][1],pairwise(map(lambda r: (r,len(self) if r==4 else self.polya(r,i,b)),(0,1,)+(2,)*b+(3,4)))))[0]),range(self.n//2),(0,j%len(self),0))))

if __name__=='__main__':
    t=twofold(5)
    print('|'.join(map(t.strate,t)))
    print(len(t))
    print('|'.join(map(lambda i: t.strate(t[i]),range(len(t)))))
    print('|'.join(map(lambda i: t.strate(t.reverse(t[i])),range(len(t)))))
    print('|'.join(map(lambda i: t.strate(t.symmetry(t.reverse(t[i]))),range(len(t)))))
    #print('|'.join(map(t.strate,t[:4])))
    print(tuple(map(t.index,t))==tuple(range(len(t))))
