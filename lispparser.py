from interpreter import *

def tryParse(n):
    return tryParseQuote(tryParseFloat(tryParseInt(n)))

def tryParseInt(n):
    try:
        return Literal(int(n))
    except Exception:
        return n

def tryParseFloat(n):
    try:
        return Literal(float(n))
    except Exception:
        return n

def tryParseQuote(n):
    try:
        if(n[0] == "'"):
            return ["quote",tryParse(n[1:])]
        return n
    except Exception:
        return n

def parse_quote(st):
    inesc = False
    qt = ""
    while len(st) > 0:
        if st[0] == '"' and inesc:
            qt += '"';
        elif st[0] == '"':
            return (Literal(qt),st)
        else:
            qt += st[0]
        st = st[1:]
    return (Literal(qt),st) 

def whitespace(st):
    return st == " " or st == "\n" or st == "\r" or st == "\t"

def read_expr(st,expr = None,word = ""):
    if expr == None:
        expr = []
    inword = False
    while len(st) > 0:
        if(st[0] == "("):
            (nexpr, st) = read_expr(st[1:],[],"")
            expr.append(nexpr)
        elif(st[0] == '"'):
            (qt,st) = parse_quote(st[1:])
            expr.append(qt)
        elif(whitespace(st[0]) and inword):
            expr.append(tryParse(word))
            inword=False
            word = ""
        elif(whitespace(st[0])):
            pass
        elif(st[0]== ")"):
            if(inword):
                expr.append(tryParse(word))
            return (expr,st)
        else:
            inword = True
            word += st[0]
        st = st[1:]
    return (expr,st)

def read(st):
    return read_expr(st)[0]

