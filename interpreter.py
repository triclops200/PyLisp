import sys

class Literal:
    def __init__(self,value):
        self.value = value
    def __str__(self):
        if isinstance(self.value,list):
            if len(self.value) > 0:
                st = "("
                for x in self.value:
                    st += str(x) + " "
                    st = st[:-1]
                    st += ")"
                    return st
            else:
                return "nil"
        if isinstance(self.value,str):
            return '"' + self.value.replace('"','\\"') + '"'
        return str(self.value)
    
class State:
    def __init__(self,oldstate=None):
        if(oldstate != None):
            self.oldstate = [oldstate]
        else:
            self.oldstate = []
        self.state = {}

    def mergestate(self,otherstate):
       self.oldstate = [otherstate] + self.oldstate

    def bindargs(self,params,args):
        if(len(args) != len(params)):
            print(str(params)+str(args))
            raise Exception("BAD NUMBER OF ARGS")
        for i in range(len(args)):
            self[params[i]] = args[i]
            
    def contains(self,key):
        try:
            if key in self.state:
                return True
            else:
                for oldstate in self.oldstate:
                    if oldstate.contains(key):
                        return True
                return False
        except:
            return False

    def __setitem__(self,key,value):
        self.state[key] = value
    def __getitem__(self,key):
        try:
            if key in self.state:
                return self.state[key]
            elif len(self.oldstate) == 0:
                return None
            else:
                for oldstate in self.oldstate:
                    if oldstate.contains(key):
                        return oldstate[key]
                return None
        except:
            return None
    def __str__(self):
        return str(self.state) + str(list(map(str,self.oldstate)))

class Macro:
    def __init__(self,fn):
        self.fn = fn
    def call(self,state,body):
        self.fn(state,body)

class Lambda(Literal):
    def __init__(self,state,params,body):
        self.params = params
        self.body = body
        self.value = self
        self.state=state

    def call(self,state,args):
        nstate = State(state)
        nstate.mergestate(self.state)
        nstate.bindargs(self.params,args)
        i = 0
        bodies = self.body
        last = None
        while(i < len(bodies)):
            wbody = bodies[i]
            newstate = State(nstate)
            while True:
                if (isinstance(wbody,Literal)):
                    retval = wbody
                    break
                wbody = list(map(lambda x: newstate[x] if newstate.contains(x) else x,wbody))
                if (isinstance(wbody[0],SpecialForm)):
                    wbody = wbody[0].call(newstate,wbody[1:])
                elif (isinstance(wbody[0],SpecialFn)):
                    retval = eval_lisp(newstate,wbody)
                    break
                elif (isinstance(wbody[0],Lambda)):
                    nargs = []
                    for expr in wbody[1:]:
                        nargs.append(eval_lisp(newstate,expr))
                    if(len(wbody[0].body) == 1):
                        newstate.bindargs(wbody[0].params,nargs)
                        wbody = wbody[0].body[0]
                    elif(i == len(bodies)-1):
                        nstate.bindargs(wbody[0].params,nargs)
                        bodies = wbody[0].body
                        i = 0
                        break
                    else:
                        wbody[0].call(newstate,nargs)
            i+=1
            last = retval
        return last
    def __str__(self):
        return "Lambda("+str(id(self))+")"
            
    def actual_call(self,state,wbody,last=False):
        newstate = State(state)
        while True:
            if (isinstance(wbody,Literal)):
                retval = wbody
                break
            elif (isinstance(newstate[wbody[0]],SpecialForm)):
                wbody = state[wbody[0]].call(newstate,wbody[1:])
            elif (isinstance(newstate[wbody[0]],SpecialFn)):
                return eval_lisp(newstate,wbody)
            elif (isinstance(newstate[wbody[0]],Lambda)):
                nargs = []
                for expr in wbody[1:]:
                    nargs.append(eval_lisp(newstate,expr))
                newstate.bindargs(newstate[wbody[0]].params,nargs)
                wbody = newstate[wbody[0]].body[0]
                    
class SpecialForm(Macro):
    def __init__(self,fn):
        self.fn = fn
    def call(self,state,xs):
        return self.fn(state,xs)

class SpecialFn(Lambda):
    def __init__(self,fn):
        self.fn = fn
    def call(self,state,xs):
        return self.fn(state,xs)
        
def eval_lisp(state,form):
    if(isinstance(form,Literal)):
        return form
    if(isinstance(state[form],Literal)):
        return state[form]
    form[0] = state[form[0]] if state.contains(form[0]) else form[0]
    while(isinstance(form[0],Macro)):
        form = form[0].call(state,form[1:])
        if(isinstance(form,Literal) and not isinstance(form.value,list)):
            return form
        form = form.value
    form = list(map(lambda x: state[x] if state.contains(x) else x,form))
    if(isinstance(form[0],Lambda)):
        newform = []
        for expr in form[1:]:
            newform.append(eval_lisp(state,expr))
        return form[0].call(state,newform)
    if(isinstance(form[0],list)):
        return eval_lisp(state,[eval_lisp(state,form[0])]+form[1:])
    raise Exception("First form must be callable")
