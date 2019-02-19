import sympy as sym
from random import randint

list_of_symbols = ['a', 'b', 'c']

symbol_dict = dict()

for symbol in list_of_symbols:
    symbol_dict[symbol] = sym.symbols(symbol)

for k, v, in symbol_dict.items():
    print(k, v*v)
    x = randint(1,10)
    print(x)
    expr = v * x
    print(expr)
    print(expr.subs(v,x))


sym.var(['n1', 'n2', 'n3'])

eqns = [
    sym.Eq(n1 + n2 + n3, 100),
    sym.Eq(0.8*n1 + 0.5*n2 + 0.25*n3, 60),
    sym.Eq(0.16*n1+0.233*n2+0.5*n3, 25)
]

print(sym.solve(eqns))

