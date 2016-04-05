from sympy import Symbol, solve, symbols

a, b, c, d, e = (4, 3, 12, 33, 345)
a, b, c, d, e = symbols('a b c d e')
x = Symbol('x')
eq = a*x**4 + b* x**3 + c*x**2 + d*x + e

sol = solve(eq, x)

for s in sol:
    print('Exacte oplossing:', s)
#     c = complex(s)
#     print('Numberieke benadering:', c)
#     print('Ingevuld in de vergelijking:', 4*c**4 + 3*c**3 + 12*c**2 + 33*c + 345)
#     print()