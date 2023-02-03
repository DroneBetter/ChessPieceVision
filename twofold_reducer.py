from functools import reduce
from itertools import accumulate,pairwise,starmap

dbg=(lambda x,*s: (x,print(*s,x))[0]) #debug
revange=(lambda a,b=None,c=1: range(b-c,a-c,-c) if b else range(a-c,-c,-c)) #(lambda *a: reversed(range(*a)))
ORsum=(lambda l: reduce(int.__or__,l,0))
tap=(lambda func,*iterables: tuple(map(func,*iterables)))
redumulate=(lambda f,l,i=None: accumulate(l,f,initial=i)) #I did (lambda f,l,i=None,accum=False: (accumulate(l,f) if accum else reduce(f,l)) if i==None else (accumulate(l,f,initial=i) if accum else reduce(f,l,i))) but then I didn't use the reduce mode (I don't suppose it comes up much)
funcxp=(lambda f,l: lambda i: reduce(lambda x,i: f(x),range(l),i)) #short for funcxponentiate
construce=(lambda f,l,i=None: reduce(lambda a,b: f(*a,b),l,i)) #reduce for constructing tuple, typically with range (you cannot unpack parameters directly in lambda arguments)
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
    def __init__(self,n,symmetry=True):
        self.n=n
        self.sym=symmetry
        self.length=((1<<(n+1>>1)|1<<n)>>1 if symmetry else 1<<n)
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
        self.reverse=eval(("lambda x: "+"".join("(lambda x: "+'|'.join(conditionalSwap('x',(n[2] and n[1]),"&"+indent(marge[0],str(hex(n[0]))),((">>" if n[1]>0 else "<<")+indent(marge[1],str(abs(n[1]))) if n[1] else ' '*(2+marge[1])),(n[1] and n[2])) for n in m)+')(' for m in masks[::-1])+'x'+')'*len(masks)))

    __len__=(lambda self: self.length)
    strate=(lambda self,s: ''.join(map(lambda i: 'o' if s>>i&1 else ' ',range(self.n))))
    #layer=(lambda self,s,i: s>>(i-1)&2|s>>self.n+~i&1 if i else s<<1&2|s>>self.n-1&1) #no negative shift amounts :-( #terrible
    layer=(lambda self,s,i: s>>i&1|s>>self.n-i-2&2)
    layinc=(lambda self,s,b,i: (lambda l: ((s&~(1<<i|1<<self.n+~i),b),True) if l==3 else ((((s|1<<i,i if i==b+1 else b) if l==2 else (s&~(1<<i)|1<<self.n+~i,b) if l else (s|1<<i,b)) if i>b else (s|1<<self.n+~i,b)) if l else (s|1<<i,min(i,b)),False))(self.layer(s,i))) #2 cannot be reached in layers under symmetry
    branch=(lambda self,s: (lambda i: i+(i==self.n//2 and self.n&1))(iindex(map(lambda i: s>>i&1^s>>self.n+~i&1,range(self.n//2)),1)))
    symmetry=(lambda self,s: funcxp(self.reverse,(lambda b: b<=self.n//2 and self.layer(s,b)==2)(self.branch(s)))(s) if self.sym else s)
    nexter=(lambda self,s,b: (s|1<<self.n//2,b) if self.n&1 and not s&1<<self.n//2 else shortduce(lambda s,i: self.layinc(*s,i),revange(self.n//2),(s&~(1<<self.n//2) if self.n&1 else s,b))) #internal (for conserving the branch output in between)
    __next__=(lambda self,s: self.nexter(s,self.branch(s))[0] if self.sym else s+1&(1<<self.n)-1) #will loop upon itself endlessly (I hate StopIteration)
    #__iter__=(lambda self: redumulate(lambda s,i: t.__next__(s),range(len(self)-1),0)) #trivial implementation
    __iter__=(lambda self,l=None,u=None: map(lambda i: i[0],redumulate(lambda s,i: self.nexter(*s),range((len(self) if u==None else u if l==None else u-l)-1),(0,self.n) if l==None else (lambda s: (s,self.branch(s)))(self[l]))) if self.sym else iter(range(len(self)) if l==None else range(l) if u==None else range(l,u))) #does not compute branch
    #polya=(lambda self,l,i,b: (3<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+(((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1)))>>1)) if l==3 else (2<<(self.n&~1)-2*(i+1) if i>b else (1<<(self.n&~1)-2*(i+1))+((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l==2 else (1<<(self.n&~1)-2*(i+1) if i>b else ((1<<((self.n>>1)-1-i))+(1<<(self.n&~1)-2*(i+1))>>1)) if l else 0)
    polya=(lambda self,l,i,b: l<<(self.n&~1)+(~i<<1) if b else (l<<(self.n&~1)+(~i<<1))+(1<<(self.n>>1)+~i)>>1 if l else 0)
    index=(lambda self,s,sym=True: (lambda s: (lambda b: sum(map(lambda i: self.polya(self.layer(s,i),i,i>b),range(self.n>>1)))<<(self.n&1)|self.n&s>>(self.n>>1)&1)(self.branch(s)))(funcxp(self.symmetry,sym)(s)) if self.sym else s&(1<<self.n)-1)
    #__getitem__=(lambda self,i: reduce(lambda s,i: t.__next__(s),range(i-1),0)) #also trivial (and slow)
    __getitem__=(lambda self,j: self.__iter__(j.start,j.stop) if type(j)==slice else (lambda f: f(j>>1)|(j&1)<<self.n//2 if self.n&1 else f(j))(lambda j: construce(lambda s,j,b,i: (lambda k,m: (s|(k&1)<<i|(k&2)<<(self.n+~i-1),j-m,b|k&1^k>>1))(*next(filter(lambda r: r[0][1]<=j<r[1][1],pairwise(map(lambda r: (r,b+1 if r==4 else self.polya(r,i,b)),(0,1,)+(2,)*b+(3,4)))))[0]),range(self.n//2),(0,j%len(self),0))[0]) if self.sym else j&(1<<self.n)-1)
if __name__=='__main__':
    '''t=twofold(5)
    print('|'.join(map(t.strate,t)))
    print(len(t))
    print('|'.join(map(lambda i: t.strate(t[i]),range(len(t)))))
    print('|'.join(map(lambda i: t.strate(t.reverse(t[i])),range(len(t)))))
    print('|'.join(map(lambda i: t.strate(t.symmetry(t.reverse(t[i]))),range(len(t)))))
    #print('|'.join(map(t.strate,t[:4])))
    print(tuple(map(t.index,t))==tuple(range(len(t))))'''
    from time import time
    wolfram=tap(lambda s: eval('lambda p,q,r: '+s),('0',        '~(p|q|r)',    '~p&~q&r',    '~(p|q)',      '~(p|r)&q',   '~(p|r)',      '~p&(q^r)',   '~(p|q&r)',      '~p&q&r',       '~(p|q^r)',      '~p&r',        'p^(p|~q|r)',    'p&q^q',       'p^(p|q|~r)',    'p^(p|q|r)',   '~p',               
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
                                        'p&(q|r)',  'p^~(q|r)',    'p&q^q&r^r',  'p&r|p^~q',    '(p^q)&r^q',  'p&q|p^~r',    'p&q&r^q^r',  'p^~q|q^r',      'p&q|(p|q)&r',  'p^p&q&r^q^~r',  'p&q|r',       'p^~q|r',        'p&r|q',       'p^~r|q',        'q|r',          '~p|q|r',               
                                        'p',        'p|~(q|r)',    'p|~q&r',     'p|~q',        'p|q&~r',     'p|~r',        'p|q^r',      'p|~q|~r',       'p|q&r',        'p|q^~r',        'p|r',         'p|~q|r',        'p|q',         'p|q|~r',        'p|q|r',        '-1')) #transcribed from https://www.wolframscience.com/nks/notes-3-2--rule-expressions-for-cellular-automata/ and deliberately only brackets reduced by precedence (you wouldn't steal a logic gate configuration)
    #print(all(starmap(lambda i,w: ORsum(map(lambda i: (w(i>>2,i>>1&1,i&1)&1)<<i,range(8)))==i,enumerate(wolfram))))
    rule=150
    boundaries=0 #left and right fixed edges
    cut=True #takes linear space this way, to avoid running over high-period oscillators too many times
    symmetry=(lambda r: ~(r|r>>2&1)&1)(rule>>1^rule>>4) #~((rule>>1^rule>>4)|(rule>>3^rule>>6))&1
    hybrid=True #do not use symmetry-reduced indexing methods (only twofold.__iter__)
    reduction=True #reduce state by symmetry but do not use optimal-space searcheds list
    fast=2#+(rule==150)
    fun=wolfram[rule]
    wr=(lambda s: fun(s>>1|boundaries>>1<<w-1,s,s<<1|boundaries&1)&mask)
    canon=(lambda p: min(map(f.symmetry,p)))
    periods=[]
    allPeriods=set()
    iterations=0
    yujh=(lambda s: '     o\n    o o\n    '+' o'[s&1]+'o o\n'+'\n'.join(map(lambda i: ' '*i+' o'[bool(i)]+' o'+' o'[s>>i&1]+(' '+' o'[s>>i+1&1]+'o'+' o'*(i<w-3))*(i<w-2),range(w)))+'\n'+' '*w+'o' if w>1 else ':-(') #b34kz5e7c8s23-a4ityz5k :-)
    yujhMode=False
    for w in range(1,20):
        isotropic=(symmetry and w>2) #otherwise layer requires negative shift
        mask=(1<<w)-1
        #print('width',w)
        n=1<<16
        f=twofold(w,isotropic)
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
    print(iterations,'iterations')
    print('\n'.join(map(str,periods)))
