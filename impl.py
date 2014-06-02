from interpreter import *
import lispparser
import sys

def if_form(state,xs):
    if(not(1 < len(xs) < 4)):
        raise Exception("Invalid conditional form")
    else:
        cond = eval_lisp(state,xs[0])
        if cond.value != []:
            return xs[1]
        else:
            if len(xs) == 2:
                return Literal([])
            else:
                return xs[2]

def progn(state,xs):
    for expr in xs[:-1]:
        eval_lisp(state,xs)
    return xs[-1]

def plus(state,xs):
    x =  Literal(sum(map(lambda x: x.value,xs)))
    return x

def quote(state,xs):
    if(len(xs) > 1):
        raise Exception("Expected one thing, found "+str(len(xs)))
    if(isinstance(xs[0],Literal)):
        return xs[0]
    return Literal(xs[0])

def equals(state,xs):
    return Literal(True) if xs[0].value == xs[1].value else Literal([])

def eval_expr(state,xs):
    return eval_lisp(state,xs[0])

def define(state,xs):
    state[xs[0]]=eval_lisp(state,xs[1])
    return state[xs[0]]

def mk_lambda(state,xs):
    return Lambda(state,xs[0],xs[1:])

def times(state,xs):
    prod = 1
    for v in xs:
        prod*=v.value
    return Literal(prod)

def divide(state,xs):
    prod = xs[0].value
    for v in xs[1:]:
        prod/=v.value
    return Literal(prod)

def minus(state,xs):
    prod = xs[0].value
    for v in xs[1:]:
        prod-=v.value
    return Literal(prod)

def and_form(state,xs):
    e = Literal(True)
    for v in xs:
        e = eval_lisp(state,v)
        if e == []:
            return []
    return e

def or_form(state,xs):
    if(len(xs) == 0):
        return Literal(True)
    for v in xs:
        e = eval_lisp(state,v)
        if e != []:
            return e
    return []

def list_create(state,xs):
    return Literal(xs)

def cons(state,xs):
    return Literal([xs[0]]+xs[1].value)

def cdr(state,xs):
    return Literal(xs[0].value[1:])

def car(state,xs):
    return xs[0].value[0]

def concat(state,xs):
    return Literal(xs[0].value + xs[1].value)

def substr(state,xs):
    if(len(xs)) == 2:
        return Literal(xs[0].value[xs[1].value:])
    return Literal(xs[0].value[xs[1].value:xs[2].value])

def my_map(state,xs):
    return Literal(list(map(lambda x: xs[0].call(state,[x]),xs[1].value)))

def my_reduce(state,xs):
    value = None
    lst = []
    if len(xs) == 3:
        value = xs[1]
        lst = xs[2].value
    elif len(xs) == 2:
        value = xs[1].value[0]
        lst = xs[1].value[1:]
    for v in lst:
        value = xs[0].call(state,[value,v])
    return value

def my_range(state,xs):
    if len(xs) == 2:
        return Literal(map(Literal,range(xs[0].value,xs[1].value)))
    return Literal(map(Literal,range(xs[0].value)))

def my_quit(state,xs):
    quit()

def my_display(state,xs):
    def pr(x):
        if(isinstance(x.value,str)):
            print(x.value)
        else:
            print(str(x))
    map(pr,xs)
    return xs[-1]

def my_str(state,xs):
    return Literal(str(xs[0]))


globalState = State()

globalState["if"] = SpecialForm(if_form)
globalState["or"] = SpecialForm(or_form)
globalState["and"] = SpecialForm(and_form)
globalState["progn"] = SpecialForm(progn)
globalState["quote"] = SpecialForm(quote)
globalState["lambda"] = SpecialForm(mk_lambda)
globalState["define"] = SpecialForm(define)

globalState["eval"] = SpecialFn(eval_expr)
globalState["list"] = SpecialFn(list_create)
globalState["cons"] = SpecialFn(cons)
globalState["cdr"] = SpecialFn(cdr)
globalState["car"] = SpecialFn(car)
globalState["concat"] = SpecialFn(concat)
globalState["substr"] = SpecialFn(substr)
globalState["map"] = SpecialFn(my_map)
globalState["reduce"] = SpecialFn(my_reduce)
globalState["range"] = SpecialFn(my_range)
globalState["quit"] = SpecialFn(my_quit)
globalState["display"] = SpecialFn(my_display)
globalState["str"] = SpecialFn(my_str)

globalState["+"] = SpecialFn(plus)
globalState["-"] = SpecialFn(minus)
globalState["*"] = SpecialFn(times)
globalState["/"] = SpecialFn(divide)
globalState["="] = SpecialFn(equals)

def read_eval(st):
    res = lispparser.read(st)
    last = []
    for expr in res:
        last.append(eval_lisp(globalState,expr))
    return last

def repl():
    while True:
        try:
            x = read_eval(raw_input(">> ") + " ")
            for y in x:
                print(str(y))
        except Exception as e:
            print(e)

def main(name,args):
    interactive = True
    if "--help" in args:
        print("Usage: %s [filenames...] [--nointeractive]" % name)
        return
    elif "--nointeractive" in args:
        args.remove("--nointeractive")
        interactive = False
    for fname in args:
        read_eval(" ".join(open(fname,"rU").readlines()) + " ")
    if interactive:
        repl()
    return

if __name__ == "__main__": main(sys.argv[0],sys.argv[1:])
