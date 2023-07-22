from itertools import accumulate,product,pairwise,starmap,count
from math import isqrt
from copy import deepcopy
from bisect import insort
from dronery import dbg,reduce,redumulate,funcxp,tap,tarmap,ORsum,rle,fact,revange,construce,shortduce,factorise
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

#these parts from https://github.com/DroneBetter/DroneLambda/blob/main/DroneLambda.py but without right-associativity special case
strucget=(lambda struc,inds: reduce(lambda a,b: a[b],inds[:-1],struc))
def strucset(struc,inds,val): #function call cannot be assigned to directly for whatever reason
    if len(inds)>1:
        strucget(struc,inds[:-1])[inds[-2]]=val
    else:
        struc=val
    return(struc)
def structrans(struc,f=None,lf=None,rev=False,fints=False):
    inds=[len(struc)-1 if rev else 0]
    b=False
    while len(inds) and type(struc)==list and 0<=inds[0]<len(struc):
        if f:
            (struc,inds)=f(struc,inds)
        if type(strucget(struc,inds))==list:
            if lf:
                (struc,inds)=lf(struc,inds)
            inds.append(len(strucget(struc,inds+[0]))-1 if rev and type(strucget(struc,inds+[0]))==list else 0)
        else:
            del inds[-1]
            if len(inds):
                inds[-1]+=(-1)**rev
        while len(inds) and (type(strucget(struc,inds))==int or (inds[-1]<0 if rev else len(strucget(struc,inds))<=inds[-1])):
            if f and fints and type(strucget(struc,inds))==int:
                (struc,inds)=f(struc,inds)
            del inds[-1]
            if not inds:
                b=True
                break
            inds[-1]+=(-1)**rev
        if len(inds) and b: break
    if f and (type(struc)==list or fints):
        struc=f(struc,[0])[0]
    if lf and type(struc)==list:
        struc=lf(struc,[0])[0]
    return(struc)
def enmax(struc,f,i=None,fints=False,iints=False):
    muc=deepcopy(struc)
    if i:
        muc=structrans(muc,i,fints=iints)
    #print(struc)
    global diff
    diff=True
    while diff:
        diff=False
        muc=structrans(muc,f,fints=fints)
    return(muc)

andMasks=(lambda n: (lambda bitWidth: tuple(reduce(lambda n,j: n|n<<(1<<j),range(i+1,bitWidth),(1<<(1<<i))-1) for i in range(bitWidth)))((n-1).bit_length()))
class twofold:
    def stractorise(self,struc,inds): #structure factorise
        global diff
        if (lambda g: type(g)==int and g!=1)(strucget(struc,inds)) and (lambda g: len(g)==inds[-2]+1 or type(g[inds[-2]+1])==int)(strucget(struc,inds[:-1])):
            diff=True
            struc=strucset(struc,inds,(lambda g: [g,list(factorise(g))[1:-1]])(strucget(struc,inds)))
        return(struc,inds)
    primate=(lambda self,n: () if n==1 else (lambda p: p if p else ((n,1),))(tuple(filter(lambda p: p[1],map(lambda p: (p,shortduce(lambda i: (i[0],False) if i[1]%p else ((i[0]+1,i[1]//p),True),i=(0,n))),reduce(lambda t,i: t+(i,)*all(map(lambda p: i%p,t)),range(2,n),())))))) #perhaps I will make a range(2,isqrt(n)+1) version one day
    phi=(lambda self,n: 1 if n==1 else reduce(int.__mul__,starmap(lambda p,e: p**(e-1)*(p-1),self.primate(n)),1))
    mu=(lambda self,n: (lambda p: 0 if any(map(lambda f: f[1]>1,p)) else (-1)**len(p))(self.primate(n)))
    lengther=(lambda self,n,o: sum(map(lambda f: o(f)<<n//f,factorise(n)))//n if n else 1)
    def __init__(self,n,symmetry=True,scroll=False,subperiods=True):
        self.n=n
        self.sym=symmetry
        self.bits=(1<<n)-1
        self.rightHalf=(1<<(self.n>>1))-1 #not including centre
        self.scroll=scroll
        self.subperiods=subperiods
        if scroll:
            prime=(lambda n: len(self.primate(n))==2) #Donald Knuth would be rolling in his grave
            self.factors=factorise(n)
            #print('n',n,self.factors)#,tap(self.phi,self.factors))
            depthen=(lambda f: lap(lambda f: list(factorise(f)),f[:-1])+[f[-1]])
            self.factree=enmax([n],self.stractorise,fints=True)[0]
            #print(self.factree)
            self.sublengths=tap(lambda f: self.lengther(f,self.mu),factorise(n)) #number of period-f tapes
            #print('l',self.length,self.sublengths)
            self.actions=tuple(range(n))
            self.compositions=tap(lambda a: tap(lambda i: a*i%n,range(n)),self.actions)
            self.roots=tap(lambda a: tap(lambda i: tap(lambda n: n[0],filter(lambda n: n[1]==a,starmap(lambda e,r: (e,r[i]),enumerate(self.compositions)))),range(n)),self.actions)
            #print('a',self.actions)
            #print('c',self.compositions)
            #print('r\n'+'\n'.join(starmap(lambda i,r: str(i)+' '+str(r),enumerate(self.roots))))
            invariants=(lambda p: (lambda m: tap(lambda i: i*m,range(1<<p)))(ORsum(map(lambda i: 1<<p*i,range(n//p)))))
            #self.struc=tap(invariants,self.factors)
            #self.struc=tap(lambda f: (lambda m: tuple(filter(lambda i: all(map(lambda m: i^(i>>m|i<<n-m&self.bits),m[:-1])),invariants(f))))(factorise(f)),self.factors)
            #print('s',tap(lambda s: tap(bin,s),self.struc))
        self.length=((lambda l: (l>>1)+(1<<(n>>1) if n&1 else 0b11<<(n>>1)-2) if symmetry else l)(self.lengther(n,self.phi)) if scroll else ((1<<(n+1>>1)|1<<n)>>1 if symmetry else 1<<n))
        #from reversalParameters in https://gist.github.com/DroneBetter/4f5d775e7c37f062ce750d4a8fefc84a (not sure how else to define instance-specific open-form function (which it must be due to in-places))
        def reversalParameters(n):
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
                        common=(m[0][1]^(m[0][1]-2*(1<<i))>0 and shifter(i,m))
                        if common:
                            endShifts[0]=-common
                            if endShifts[0]<m[0][1]: m[0][1]=0
                        else: break
                masks[-1][0][0]>>=endShifts[1]; masks[-1][0][1]+=endShifts[1]
            for i,m in enumerate(masks): m[1][1]=m[0][1]-2*(1<<i)
            conditionalSwap=(lambda x,b,t,f,br: '('*br+x+(t+')'*br+f if b else f+')'*br+t))
            indent=(lambda i,t: " "*((i-len(t))*(i>len(t)))+t)
            marge=[0,0]#[max(len(str((abs if i else hex)(n[i]))) for m in masks for n in m) for i in range(2)] except it is one line
            return(eval("lambda x: "+"".join("(lambda x: "+'|'.join(conditionalSwap('x',(n[2] and n[1]),"&"+indent(marge[0],str(hex(n[0]))),((">>" if n[1]>0 else "<<")+indent(marge[1],str(abs(n[1]))) if n[1] else ' '*(2+marge[1])),(n[1] and n[2])) for n in m)+')(' for m in masks[::-1])+'x'+')'*len(masks)))
        self.reversed=reversalParameters(n)
        self.halfverse=reversalParameters(n>>1)
        if scroll:
            self.subreverses=tap(reversalParameters,range(n+1))

    __len__=(lambda self: self.length)
    strate=(lambda self,s: ''.join(map(lambda i: 'o' if s>>i&1 else ' ',range(self.n))))
    #layer=(lambda self,s,i: s>>(i-1)&2|s>>self.n+~i&1 if i else s<<1&2|s>>self.n-1&1) #no negative shift amounts :-( #terrible
    layer=(lambda self,s,i: s>>i&1|s>>self.n-i-2&2)
    layinc=(lambda self,s,b,i: (lambda l: ((s&~(1<<i|1<<self.n+~i),b),True) if l==3 else ((((s|1<<i,i if i==b+1 else b) if l==2 else (s&~(1<<i)|1<<self.n+~i,b) if l else (s|1<<i,b)) if i>b else (s|1<<self.n+~i,b)) if l else (s|1<<i,min(i,b)),False))(self.layer(s,i))) #2 cannot be reached in layers under symmetry
    branch=(lambda self,s: (lambda i: i+(i==self.n//2 and self.n&1))(iindex(map(lambda i: s>>i&1^s>>self.n+~i&1,range(self.n//2)),1)))
    symmetry=(lambda self,s: min(map(lambda s: min(redumulate(lambda s,i: s>>1|(s&1)<<self.n-1,range(self.n),s)),((s,self.reversed(s)) if self.sym else (s,)))) if self.scroll else funcxp(self.reversed,(lambda b: b<=self.n//2 and self.layer(s,b)==2)(self.branch(s)))(s) if self.sym else s)
    canonical=(lambda self,s: s==self.symmetry(s)) #whether it is canonical (in scrolling version) #(lambda self,s,l: (lambda b: b>l//2 or (s>>b&1 or not s>>l+~b&1))((lambda i: i+(i==l//2 and l&1))(iindex(map(lambda i: s>>i&1^s>>l+~i&1,range(l//2)),1)))) breaks down for n>=11, unfortunately
    def nexter(self,w,l): #internal (for conserving the l or b output in between)
        if self.scroll:
            while True: #runs for asymptotically constantly many iterations before termination
                t=(w&~w-1).bit_length()
                if t<self.n:
                    l=self.n-t
                    w=reduce(lambda w,i: w|w>>(l<<i),range(l and (self.n//l).bit_length()),(w>>t^1)<<t)
                    if (not self.n%l if self.subperiods else self.n==l) and (not self.sym or self.canonical(w)):
                        return(w,l)
                else:
                    raise(StopIteration)
        else:
            return((w|1<<self.n//2,l) if self.n&1 and not w&1<<self.n//2 else shortduce(lambda w,i: self.layinc(*w,i),revange(self.n//2),(w&~(1<<self.n//2) if self.n&1 else w,l)))
    period=(lambda self,w: next(filter(lambda m: not w^(w>>m|w<<self.n-m&self.bits),self.factors)))
    __next__=(lambda self,s: self.nexter(s,(self.period if self.scroll else self.branch)(s))[0] if self.sym or self.scroll else s+1&(1<<self.n)-1) #will loop upon itself endlessly (I hate StopIteration)
    #__iter__=(lambda self: redumulate(lambda s,i: t.__next__(s),range(len(self)-1),0)) #trivial implementation
    __iter__=(lambda self,l=None,u=None: map(lambda i: i[0],redumulate(lambda s,i: self.nexter(*s),range((len(self) if u==None else u if l==None else u-l)-1),(0,1 if self.scroll else self.n) if self.scroll or l==None else (lambda s: (s,self.branch(s)))(self[l]))) if self.sym or self.scroll else iter(range(len(self)) if l==None else range(l) if u==None else range(l,u))) #does not compute branch or l
    #polya=(lambda self,l,i,b: (3<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+(((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1)))>>1)) if l==3 else (2<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l==2 else (1<<(self.n&~1)-2*(i+1) if i>b else ((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l else 0)
    polya=(lambda self,l,i,b: l<<(self.n&~1)+(~i<<1) if b else (l<<(self.n&~1)+(~i<<1))+(1<<(self.n>>1)+~i)>>1 if l else 0)
    index=(lambda self,s,sym=True: (lambda s: (lambda b: sum(map(lambda i: self.polya(self.layer(s,i),i,i>b),range(self.n>>1)))<<(self.n&1)|self.n&s>>(self.n>>1)&1)(self.branch(s)))(funcxp(self.symmetry,sym)(s)) if self.sym else s&(1<<self.n)-1)
    #__getitem__=(lambda self,i: reduce(lambda s,i: t.__next__(s),range(i-1),0)) #also trivial (and slow)
    __getitem__=(lambda self,j: self.__iter__(j.start,j.stop) if type(j)==slice else (lambda f: f(j>>1)|(j&1)<<(self.n>>1) if self.n&1 else f(j))(lambda j: construce(lambda s,j,b,i: (lambda k,m: (s|(k&1)<<i|(k&2)<<(self.n+~i-1),j-m,b|k&1^k>>1))(*next(filter(lambda r: r[0][1]<=j<r[1][1],pairwise(map(lambda r: (r,len(self) if r==4 else self.polya(r,i,b)),(0,1,)+(2,)*b+(3,4)))))[0]),range(self.n//2),(0,j%len(self),0))[0]) if self.sym else j&(1<<self.n)-1)

    """def otheriter(self):
        w=0
        yield(w)
        for i in range(len(self)-1):
            '''if 1&self.n&~i:''' #removed due to preventing odd generation from being sorted
            '''    yield(w|1<<(self.n>>1))
            else:''' #the else wouuld enclose remainder of loop
            w+=1
            if not w&self.rightHalf:
                '''if self.n&1:
                    w+=1<<(self.n>>1)'''
                w|=self.halfverse(w>>(self.n+1>>1))
            yield(w)
        print(len(self))""" #old version (returns sorted list, albeit not necessarily of lexicographic minima)

    """def otheriter(self): #compute smallest half of state by standard binary counting, every time largest half is incremented, reinitialise smallest from its reflected value
        wibble=0
        w=0
        yield(w)
        count=0
        for i in range(1<<(self.n>>1)):
            for j in range((self.rightHalf-count)<<(self.n&1)):
                w+=1
                yield(w)
            count=self.halfverse(w>>(self.n+1>>1))
            if self.n&1:
                wibble+=1
                #print(self.strate(w))
                yield(w)
            w+=1#<<(self.n>>1)
            w&=~((1<<(self.n>>1))-1)
            w|=count
        if not self.n&1:
            yield(self.bits)
        print(len(self),wibble)"""
    
    def redstone(self):
        '''rights=[]'''
        rights=list(range(1<<(self.n>>1)))
        for left in range(1<<(self.n>>1)):
            for right in range(1<<(self.n>>1)):
                if right not in rights:
                    yield(left<<(self.n>>1)|right)
            #print(rights.index(self.halfverse(left))) #converges to reversed(A233931)
            del(rights[rights.index(self.halfverse(left))])
            '''insort(rights,self.halfverse(left))
            #print(rights.index(self.halfverse(left))) #A264596
            for right in rights:
                yield(left<<(self.n>>1)|right)'''

if __name__=='__main__':
    '''t=twofold(5)
    print('|'.join(map(t.strate,t)))
    print(len(t))
    print('|'.join(map(lambda i: t.strate(t[i]),range(len(t)))))
    print(t.strate(t[5]))
    print('|'.join(map(lambda i: t.strate(t.reversed(t[i])),range(len(t)))))
    print('|'.join(map(lambda i: t.strate(t.symmetry(t.reversed(t[i]))),range(len(t)))))
    #print('|'.join(map(t.strate,t[:4])))
    print(tuple(map(t.index,t))==tuple(range(len(t))));exit()'''
    '''for l in range(5):
        print((lambda n: '\n'.join(map(n.strate,n.redstone())))(twofold(2*l)))
        print(tuple(twofold(2*l).redstone()))'''
    #print((lambda n: '\n'.join(map(n.strate,n)))(twofold(12,False,True)))
    #print((lambda n: '\n'.join(map(n.strate,sorted(map(n.symmetry,n)))))(twofold(6)));exit()
    #print((lambda n: '\n'.join(map(n.strate,n.otheriter())))(twofold(6)))#;exit()
    #print('\n'.join((lambda n,o: map(lambda s: n.strate(s)+' '+str(s in o),sorted(n)))(*(lambda n: (n,tap(n.symmetry,n.otheriter())))(twofold(6)))))#;exit()
    #print('\n'.join(map(lambda n: (lambda n: str((len(n),(lambda t: (len(t),len(t)-len(set(t))))(tuple(n.otheriter())))))(twofold(n)),range(16))))
    #print((lambda n: '\n'.join(map(n.strate,n.otheriter())))(twofold(6)))
    #print('excludeds')
    #print((lambda n: '\n'.join(starmap(lambda a,b: a+'|'+b,zip(map(n.strate,sorted(n)),map(n.strate,n.otheriter())))))(twofold(6)))
    #print((lambda n: '\n'.join(starmap(lambda a,b: a+'|'+b,zip(map(n.strate,sorted(n)),map(n.strate,sorted(map(n.symmetry,n.otheriter())))))))(twofold(6)));exit()
    #print((lambda n: '\n'.join(starmap(lambda a,b: a+'|'+b,zip(map(n.strate,n),map(n.strate,(lambda s: filter(lambda m: m not in s and n.reversed(m) not in s,n))(set(n.otheriter())))))))(twofold(6)));exit()
    #print((lambda n,o: str(o==tuple(sorted(o)))+'\n'+'\n'.join(tap(lambda o: '|'.join(map(n.strate,o))+' '+str(o[0]==o[1]),zip(o,sorted(o)))))(*(lambda n: (n,tuple(n.otheriter())))(twofold(5))));exit()
    #print((lambda n: '\n'.join(map(lambda o: n.strate(o)+' '+str(o<=n.reversed(o)),n.otheriter())))(twofold(6)));exit()
    from time import time
    ankos=('0',        '~(p|q|r)',    '~p&~q&r',    '~(p|q)',      '~(p|r)&q',   '~(p|r)',      '~p&(q^r)',   '~(p|q&r)',      '~p&q&r',       '~(p|q^r)',      '~p&r',        'p^(p|~q|r)',    'p&q^q',       'p^(p|q|~r)',    'p^(p|q|r)',   '~p',
           'p&~q&~r',  '~(q|r)',      '(p^q^r)&~q', '~(p&r|q)',    '(p^q)&~r',   '~(p&q|r)',    'p^p&q&r^q^r','p^(p^~q|q^r)',  '(p^q)&(p^r)',  'p&q&r^q^~r',    'p^(p&q|r)',   'p^(p^~q|r)',    'p^(p&r|q)',   'p^(p^~r|q)',    'p^(q|r)',     '~(p&(q|r))',
           'p&~q&r',   '~(p^q^r|q)',  '~q&r',       '(~p|q|r)^q',  '(p^q)&(q^r)','p^p&q&r^~r',  '(p&q|r)^q',  '(p^~q|r)^q',    '(p^q)&r',      '~(p&q|p^q^r)',  'p&q&r^r',     'p^(p^r|p^~q)',  '(p&(q|r))^q', 'p^(q|~r)',      'p&q^(q|r)',   '~p|~q&r',
           'p&~q',     '(p|q|~r)^q',  '(p|q|r)^q',  '~q',          '(p|q&r)^q',  '(p|q^~r)^q',  '(p|r)^q',    '~((p|r)&q)',    'p^(p|r)&q',    '(p|~r)^q',      '(p|q^r)^q',   '~p&r|~q',       'p^q',         'p^(p|q|r)^~q',  'p&q^(p|q|r)', '~(p&q)',
           'p&q&~r',   '~(p^q|r)',    '(p^r)&(q^r)','p^p&q&r^~q',  'q&~r',       '(~p|q|r)^r',  '(p&r|q)^r',  '(p^~r|q)^r',    'p&q^q&r',      '~(p&r|p^q^r)',  'p&(q|r)^r',   'p^(~q|r)',      'p&q&r^q',     'p^(p^q|p^~r)',  'p^(p^q|r)',   '~p|q&~r',
           'p&~r',     '(p|~q|r)^r',  '(p|q&r)^r',  '(p|q^~r)^r',  '(p|q|r)^r',  '~r',          '(p|q)^r',    '~((p|q)&r)',    'p^(p|q)&r',    '(p|~q)^r',      'p^r',         'p^~(p|q|r)^r',  '(p|q^r)^r',   '~((p|~q)&r)',   'p&r^(p|q|r)', '~(p&r)',
           'p&(q^r)',  '~(p^q^r|q&r)','(p|r)&q^r',  '(~p|r)^q',    '(p|q)&r^q',  'p^p&q^~r',    'q^r',        '~(p|q|r)^q^r',  'p^(p|q|r)^q^r','p^q^~r',        'p&q^r',       'p^(p|q|~r)^q^r','(p&r)^q',     'p^(p|~q|r)^q^r','(~p&q&r)^q^r','~p|q^r',
           'p^p&q&r',  'p^~(p^q|p^r)','(p^q|r)^q',  'p&~r|~q',     '(p|q)^q&r',  'p&~q|~r',     '(p|q|r)^q&r','~(q&r)',        'p^q&r',        'p^(~p|q|r)^q^r','p^(p&~q&r)^r','~((p^q^r)&q)',  'p^(p&q&~r)^q','p^q|~r',        'p^q|p^r',     '~(p&q&r)',
           'p&q&r',    '~(p^q|p^r)',  '(p^q^r)&r',  'p^p&q&~r^~q', '(p^q^r)&q',  'p^p&~q&r^~r', 'p&(q|r)^q^r','~p^q&r',        'q&r',          '(~p|q|r)^q^r',  '(p&~q&r)^r',  '~((p|q)^q&r)',  '(~p|r)&q',    'p^(p^q|~r)',    'p^(p^q|p^r)', '~p|q&r',
           'p&(p^q^r)','~p&q&r^q^~r', 'p^(p|r)&q^r','p&r^~q',      'p^(p|q)&r^q','p&q^~r',      'p^q^r',      'p^~(p|q|r)^q^r','(p|q|r)^q^r',  'q^~r',          'p^p&q^r',     '(p|q|~r)^q^r',  'p^p&r^q',     '(p|~q|r)^q^r',  'p^q^r|q&r',   '~(p&(q^r))',
           'p&r',      'p^(p|~q|r)^r','(p|~q)&r',   '(~p|q^r)^q',  'p^(p|q|r)^r','p^~r',        'p&q^q^r',    'p^(p|q|~r)^r',  '(p|q)&r',      '~(p|q)^r',      'r',           '~(p|q)|r',      'p&(q^r)^q',   'p^~r|q&r',      'p&q^q|r',     '~p|r',
           'p&(~q|r)', 'p^~(p^q|r)',  '(p^q|p^r)^q','p&r|~q',      'p^q^q&r',    'p^(~p|q|r)^r','p&r|p^q^r',  'p^q^r|~q',      'p^p&q^q&r',    'p&r|q^~r',      'p&~q|r',      '~q|r',          'p^p&q&r^q',   'p^q|p^~r',      'p^q|r',       '~p|~q|r',
           'p&q',      'p^(p|q|~r)^q','p^(p|q|r)^q','p^~q',        '(p|~r)&q',   '~(p|q^r)^q',  'p&r^q^r',    'p^(p|~q|r)^q',  '(p|r)&q',      '~(p|r)^q',      'p&(q^r)^r',   'p^~q|q&r',      'q',           '~(p|r)|q',      '~p&r|q',      '~(p&~q)',
           'p&(q|~r)', '~(p&q^(q|r))','p^q&r^r',    'p^(~p|q|r)^q','(p^q|p^r)^r','p&q|~r',      'p&q|p^q^r',  '~((p^q)&r)',    'p^(p^q)&r',    'p&q|q^~r',      'p^p&q&r^r',   'p^r|p^~q',      'p&~r|q',      'q|~r',          'p^q^r|q',     '~(p&~q&r)',
           'p&(q|r)',  'p^~(q|r)',    'p&q^q&r^r',  'p&r|p^~q',    '(p^q)&r^q',  'p&q|p^~r',    'p&q&r^q^r',  'p^~q|q^r',      'p&q|(p|q)&r',  'p^p&q&r^q^~r',  'p&q|r',       'p^~q|r',        'p&r|q',       'p^~r|q',        'q|r',         '~p|q|r',
           'p',        'p|~(q|r)',    'p|~q&r',     'p|~q',        'p|q&~r',     'p|~r',        'p|q^r',      'p|~q|~r',       'p|q&r',        'p|q^~r',        'p|r',         'p|~q|r',        'p|q',         'p|q|~r',        'p|q|r',       '-1') #2064 characters (834 operators (170 ~s, 171 &s, 283 ^s, 210 |s), 918 lookups (311 p's, 313 q's, 294 r's), 156 bracket pairs) transcribed from https://www.wolframscience.com/ankos/notes-3-2--rule-expressions-for-cellular-automata/ and deliberately only brackets reduced by precedence (you wouldn't steal a logic gate configuration)
    alpha=('0',       '~(p|q|r)',     '~(p|q)&r',   '~(p|q)',        '~(p|r)&q',   '~(p|r)',        '~p&(q^r)',   '~(p|q&r)',      '~p&q&r',       '~(p|q^r)',        '~p&r',     '~p&(~q|r)',       '~p&q',       '~p&(q|~r)',       '~p&(q|r)',   '~p',
           'p&~q&~r', '~(q|r)',       '(p^r)&~q',   '~(p&r|q)',      '(p^q)&~r',   '~(p&q|r)',      'p&q&r^p^q^r','p^(p^~q|q^r)',  '(p^q)&(p^r)',  '~(p&q|q^r)',      'p^(p&q|r)','p^(p^~q|r)',      'p^(p&r|q)',  'p^(p^~r|q)',      'p^(q|r)',    '~(p&(q|r))',
           'p&~q&r',  '~(p^q^r|q)',   '~q&r',       '~q&(r|~p)',     '(p^q)&(q^r)','~(p&q|p^r)',    '(p&q|r)^q',  '(p^~q|r)^q',    '(p^q)&r',      '~(p&q|p^q^r)',    '~(p&q)&r', 'p^(p^r|p^~q)',    '(p^q)&(q|r)','p^(q|~r)',        'p&q^(q|r)',  '~p|~q&r',
           'p&~q',    '~q&(p|~r)',    '~q&(p|r)',   '~q',            '(p|q&r)^q',  '(p|q^~r)^q',    '(p|r)^q',    '~((p|r)&q)',    'p^(p|r)&q',    '(p|~r)^q',        '(p|q^r)^q','~p&r|~q',         'p^q',        '~(p|r)|p^q',      'r&~p|p^q',   '~(p&q)',
           'p&q&~r',  '~(p^q|r)',     '(p^r)&(q^r)','~(p&r|p^q)',    'q&~r',       '~r&(q|~p)',     '(p&r|q)^r',  '~p^q&(p^r)',    'q&(p^r)',      '~(p&r|p^q^r)',    'p&(q|r)^r','p^(~q|r)',        'q&~(p&r)',   'p^(p^q|p^~r)',    'p^(p^q|r)',  '~p|q&~r',
           'p&~r',    '(p|~q)&~r',    '(p|q&r)^r',  '~q^p&(q^r)',    '(p|q)&~r',   '~r',            '(p|q)^r',    '~((p|q)&r)',    'p^(p|q)&r',    '(p|~q)^r',        'p^r',      '~(p|q)|p^r',      '(p|q^r)^r',  '~((p|~q)&r)',     'q&~p|p^r',   '~(p&r)',
           'p&(q^r)', '~(p^q^r|q&r)', '(p|r)&q^r',  '(~p|r)^q',      '(p|q)&r^q',  '(~p|q)^r',      'q^r',        '~(p|q)|q^r',    'p^(p|q|r)^q^r','p^q^~r',          'p&q^r',    '~((p|q)&(p^q^r))','(p&r)^q',    '~((p|r)&(p^q^r))','q&~p|q^r',   '~p|q^r',
           'p&~(q&r)','p^~(p^q|p^r)', '(p^q|r)^q',  'p&~r|~q',       '(p|q)^q&r',  'p&~q|~r',       'p&~q|q^r',   '~(q&r)',        'p^q&r',        '~((q|r)&(p^q^r))','p&~q|p^r', '~q|p^r',          'p&~r|p^q',   'p^q|~r',          'p^q|p^r',    '~(p&q&r)',
           'p&q&r',   '~(p^q|p^r)',   'r&~(p^q)',   '~(p^q)&(r|~p)', 'q&~(p^r)',   '~(p^r)&(q|~p)', 'p&(q|r)^q^r','~p^q&r',        'q&r',          '(~p|q|r)^q^r',    'r&(q|~p)', '~r^(q|p^r)',      '(~p|r)&q',   'p^(p^q|~r)',      'p^(p^q|p^r)','~p|q&r',
           'p&~(q^r)','~(q^r)&(p|~q)','p^(p|r)&q^r','p&r^~q',        'p^(p|q)&r^q','p&q^~r',        'p^q^r',      '~(p|q)|p^q^r',  '(p|q|r)^q^r',  'q^~r',            'p&~q^r',   '~((p|q)&(q^r))',  'p^p&r^q',    '~((p|r)&(q^r))',  'p^q^r|q&r',  '~(p&(q^r))',
           'p&r',     'p^(p|~q|r)^r', '(p|~q)&r',   '(~p|q^r)^q',    'p^(p|q|r)^r','p^~r',          'r^q&~p',     '~((p|q)&(p^r))','(p|q)&r',      '~(p|q)^r',        'r',        '~(p|q)|r',        'p&(q^r)^q',  'p^~r|q&r',        'r|q&~p',     '~p|r',
           'p&(~q|r)','p^~(p^q|r)',   '(p^q|p^r)^q','p&r|~q',        'p^q&~r',     '~((q|r)&(p^r))','p&r|p^q^r',  'p^q^r|~q',      'p^q&(p^r)',    'p&r|q^~r',        'p&~q|r',   '~q|r',            'p&r|p^q',    'p^q|p^~r',        'p^q|r',      '~p|~q|r',
           'p&q',     'p^(p|q|~r)^q', 'p^q^(p|q|r)','p^~q',          '(p|~r)&q',   '~(p|q^r)^q',    'p&r^q^r',    '~((p|r)&(p^q))','(p|r)&q',      '~(p|r)^q',        'p&(q^r)^r','p^~q|q&r',        'q',          '~(p|r)|q',        '~p&r|q',     '~(p&~q)',
           'p&(q|~r)','~p^(q|p^r)',   'p^~q&r',     '~((q|r)&(p^q))','(p^q|p^r)^r','p&q|~r',        'p&q|p^q^r',  '~((p^q)&r)',    'p^(p^q)&r',    'p&q|q^~r',        'p&q|p^r',  'p^r|p^~q',        'p&~r|q',     'q|~r',            'q|p^r',      '~(p&~q&r)',
           'p&(q|r)', 'p^~(q|r)',     'r^q&(p^r)',  'p&r|p^~q',      '(p^q)&r^q',  'p&q|p^~r',      'p&q|q^r',    'p^~q|q^r',      'p&q|(p|q)&r',  'p&q|p^q^~r',      'p&q|r',    'p^~q|r',          'p&r|q',      'p^~r|q',          'q|r',        '~p|q|r',
           'p',       'p|~(q|r)',     'p|~q&r',     'p|~q',          'p|q&~r',     'p|~r',          'p|q^r',      'p|~q|~r',       'p|q&r',        'p|q^~r',          'p|r',      'p|~q|r',          'p|q',        'p|q|~r',          'p|q|r',      '-1') #2021 characters (799 operators (193 ~s, 169 &s, 233 ^s, 204 |s), 860 lookups (303 p's, 288 q's, 269 r's), 181 bracket pairs), from WolframAlpha
    wolfram=tap(lambda s: eval('lambda p,q,r: '+s),alpha)
    #print(all(starmap(lambda i,w: ORsum(map(lambda i: (w(i>>2,i>>1&1,i&1)&1)<<i,range(8)))==i,enumerate(wolfram))))
    #print(tap(lambda x: map(hex,x),filter(lambda x: x[0]!=x[1],enumerate(starmap(lambda i,w: ORsum(map(lambda i: (w(i>>2,i>>1&1,i&1)&1)<<i,range(8))),enumerate(wolfram))))))
    verbose=False
    #rule=150
    maxes=[]
    maximalPeriods=False
    for rule in range(256):
        fun=wolfram[rule]
        print(rule,tarmap(lambda i,s: s&~(~0<<(i<<1|1)),enumerate(redumulate(lambda r,i: fun(r<<1|1,r<<2|3,r<<3|7)>>1 if rule&1 and r>>(i<<1|1)&1 else fun(r,r<<1,r<<2),range(1<<4),1))))
        if maximalPeriods:
            boundaries=0 #left and right fixed edges
            scroll=True
            cut=True #takes linear space this way, to avoid running over high-period oscillators too many times
            symmetry=False#(lambda r: ~(r|r>>2&1)&1)(rule>>1^rule>>4) #~((rule>>1^rule>>4)|(rule>>3^rule>>6))&1
            hybrid=True or scroll #do not use symmetry-reduced indexing methods (only twofold.__iter__)
            reduction=True #reduce state by symmetry but do not use optimal-space searcheds list
            fast=3#+(rule==150)
            wr=(lambda s: (fun(s>>1|(s&1)<<w-1,s,(s&(1<<w-1)-1)<<1|s>>w-1) if scroll else fun(s>>1|boundaries>>1<<w-1,s,s<<1|boundaries&1))&mask)
            canon=(lambda p: min(map(f.symmetry,p)))
            periods=[]
            allPeriods=set()
            iterations=0
            yujh=(lambda s: '     o\n    o o\n    '+' o'[s&1]+'o o\n'+'\n'.join(map(lambda i: ' '*i+' o'[bool(i)]+' o'+' o'[s>>i&1]+(' '+' o'[s>>i+1&1]+'o'+' o'*(i<w-3))*(i<w-2),range(w)))+'\n'+' '*w+'o' if w>1 else ':-(') #b34kz5e7c8s23-a4ityz5k :-)
            yujhMode=False
            for w in range(1,16):
                isotropic=(symmetry and w>2) #otherwise layer requires negative shift
                mask=(1<<w)-1
                #print('width',w)
                n=1<<16
                if fast<3: print(w,isotropic,scroll)
                f=twofold(w,isotropic,scroll)
                if cut: searcheds=[False for _ in range(1<<w if hybrid else len(f))]
                finals=set()
                t=time()
                for i,s in enumerate(f):
                    if i and not i%n:
                        print((lambda t: str(i)+'/'+str(len(f))+' ('+str(100*i//len(f))+'%) in '+str(int(t*1000)/1000)+'s, '+str(int(n//t))+' soups/s, '+str(int((len(f)-i)*t)//n)+'s remaining')(time()-t))
                        t=time()
                    past=[]
                    while not(cut and searcheds[s if hybrid else i] or s in past):
                        past.append(s)
                        iterations+=1
                        if cut and hybrid:
                            searcheds[s]=True
                        s=wr(s)
                        if reduction or cut and not hybrid:
                            s=f.symmetry(s)
                            if cut and not hybrid:
                                searcheds[i]=True
                                i=f.index(s,sym=False)
                        #print(f.strate(s))
                    if s in past:
                        p=len(past)-past.index(s)
                        a=(p if fast else (p,canon(past[-p:])))
                        if a not in finals:
                            if 1<=fast<3:
                                print(f.strate(canon(past[-p:]))+'|'+str(a))
                            finals.add(a)
                        if p not in allPeriods:
                            if rule==150 and yujhMode:
                                print('p'+str(p))
                                print(yujh(canon(past[-p:])))
                            allPeriods.add(p)
                if fast<3: print(finals)
                periods.append(tuple(sorted(finals)))
                if not fast:
                    m=max(p for p,s in finals)
                    for p,s in finals:
                        if p>2 or m==2:
                            print('\n'*(not fast)+'s',p)
                            if fast:
                                print(f.strate(s))
                            else:
                                for i in range(p):
                                    print(f.strate(s))
                                    s=wr(s)
            if verbose: print(iterations,'iterations')
            #print('\n'.join(map(str,periods)))
            maxes.append(tap(max,periods))
            #print(rule,maxes[-1])
    if maximalPeriods:
        classification=tuple(sorted(range(256),key=lambda r: maxes[r][::-1]))
        print('\n'.join(map(lambda r: str(r)+','+str(maxes[r]),classification)))

    b=0
    A211667=lambda n: n and (n.bit_length()-1).bit_length()
    #flip=lambda l,n,k=0: flip(l-1,n>>1,k<<1|n&1) if l else k #'linear time' (pfft)
    def niceA030101(d,n):
        b=d-1#d.bit_length()-1
        l=b.bit_length()
        o=c=(1<<(1<<l))-1
        for i in range(l):
            s=1<<l+~i #s=1<<i
            o^=o<<s #o=c//((1<<(s<<1))-1)*((1<<s)-1)
            n=(n&o)<<s|n>>s&o
        return(n>>1+(~d^~0<<d.bit_length()) if d&d-1 else n)
    '''A063511=lambda n: n and 1<<A211667(n) #first power of 2 >= bit length ('word size')
    print(tap(lambda n: niceA030101(4,n),range(1<<4)))
    interesting=lambda n: n if n<2 else ORsum(map(lambda i: 1<<niceA030101(A211667(n),i),filter(lambda i: n>>i&1,range(n.bit_length()))))
    print(tuple(zip(sorted(tap(interesting,range(1<<4))),tuple(range(1<<4)))))
    print(tap(lambda n: (bin(n),bin(interesting(n))),range(1<<6)))
    import matplotlib.pyplot as plot
    from numpy import array
    r=1<<16
    plot.scatter(range(r),tap(interesting,range(r)),s=1)
    plot.show();exit() #:-)'''
    reflect=(lambda axes,i,reverse=False: #x,y,transpose
     ( ( (i+1)*w+~(i//w*(1+w**2))
        if axes>>reverse&1 else
         w*(w+~i)+i//w*(1+w**2))
      if (axes^axes>>1)&1 else
       ( (1-w**2)*~(i//w)-i*w)
        if axes&1 else
         i*w+i//w*(1-w**2))
    if axes>>2&1 else
     ( ( w**2+~i
        if axes&1 else
         i+w*(w+~(i//w<<1)))
      if axes>>1&1 else
       ( w*(i//w<<1|1)+~i
        if axes&1 else
         i)))
    wolframs=lambda n: 2**2**n+2**(2**n+2**(n+1>>1)>>1)+2**(2**(n-1)+n%2)>>2 #lambda n: ((1<<(1<<n))+((1<<(1<<n))+(1<<(n+1>>1))>>1)+(1<<(1<<n-1)+n%2))>>2
    #print(tuple(map(wolframs,range(1,5))));exit()

    keepid=False
    blackwhite=True
    shiftener=lambda f: eval('lambda n: '+'|'.join(starmap(lambda s,a: 'n'+bool(s)*(('>>' if s<0 else '<<')+str(abs(s)))+'&'+str(bin(ORsum(map(lambda a: 1<<a[1],a)))),rle(sorted(map(lambda b: (lambda a: (a-b,a))(f(b)),range(b)),key=lambda t: t[0]),lambda t: t[0],False))))
    dims=2
    for w in range(1,3):
        print('w='+str(w))
        b=1<<w**dims;r=1<<b
        id=lambda n: n
        NOT=lambda n: r-1^niceA030101(b,n)
        if dims==1:
            flipacts=(id,flipact:=shiftener(lambda n: niceA030101(w,n)))
            #flipact=lambda n: n>>3&0b00001010|n&0b10100101|n<<3&0b01010000 #for w=3
        elif dims==2:
            flipacts=tap(lambda f: shiftener(lambda n: ORsum(map(lambda b: (n>>b&1)<<reflect(f,b),range(w**dims)))),range(8)) #(inelegance is allowed when it is only running in generating another function :-)
        group=flipacts+blackwhite*tap(lambda f: lambda n: NOT(f(n)),flipacts)#tap(lambda f: lambda n: reduce(lambda n,f: f(n),f,n),product(*map(lambda f: (id,f),(NOT,)+flipacts)))
        #group=(id,group[1],group[8],group[9])
        print('f',len(flipacts))#;input()
        if w<(5 if dims==1 else 3):
            representatives=tuple(filter(lambda n: n==min(map(lambda f: f(n),group)),range(r)))
            print(len(representatives),bin(len(representatives)))
            print(str(len(tuple(filter(lambda n: n==NOT(n),range(r)))))+',1<<'+str(len(tuple(filter(lambda n: n==flipacts[1](n),range(r)))).bit_length()-1))
            #print(''.join(map(lambda c: '|-\n|'+','.join(map(str,c[1]))+'\n|'+'NSIOA'[c[0]]+'\n|'*2+'\n',sorted(tap(lambda n: ((3+(n!=NOT(n))) if n==flipact(NOT(n)) else 2 if n==NOT(n) else int(n==flipact(n)),sorted(set((n,flipact(n),NOT(n),flipact(NOT(n)))))),representatives)))));input()
            #print(str(len(tuple(filter(lambda n: flipact(NOT(n))==NOT(flipact(n)),range(r)))))+'/'+str(r))
            #print('\n'.join(map(lambda n: str(tap(bin,(n,flipact(n),NOT(n),flipact(NOT(n)),NOT(flipact(n))))),range(r>>1,r>>1|255))))
            #print('\n'.join(map(lambda n: str(tap(bin,(n,flipact(n),NOT(n),flipact(NOT(n)),NOT(flipact(n))))),range(r))))

        periods=[];cycles=[];strobings=[]
        for j,a in enumerate(group):
            strobings.append(a(0)==r-1)
            periods.append([])
            for c in range(b):
                o=s=(1<<c,)+(0,)*keepid
                i=0
                while True:
                    i+=1
                    print(j,bin(o[0]),bin(s[0]));input()
                    s=tap(a,s)
                    if s==o: break
                periods[-1].append(i)
            cycles.append(sum(map(r.__floordiv__,periods[-1]))//r)
        #if True or w==3: print(tap(rle,periods))
        print(tuple(zip(map(int,strobings),cycles,periods)),sum(map(lambda s,c: 1<<c-s,strobings,cycles))//len(group))#>>(fact(dims)<<dims+1)
        print(tap(lambda s,c: (1<<c-s)//len(group),strobings,cycles))

        '''import numpy as np
        import matplotlib.pyplot as plot
        print(tap(lambda n: len(twofold(n)),range(4)))
        for n in range(1,16):
            data=np.array(tap(lambda r: tap(lambda r: tap(lambda i: i in r,range(n)),r),twofold(n,False,True).roots))#tap(lambda r: tap(len,r),twofold(n,False,True).roots)
            print(data)
            ax=plot.figure().add_subplot(projection='3d')
            ax.voxels(data)
            plot.show()'''
