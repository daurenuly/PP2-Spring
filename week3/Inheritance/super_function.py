def superfunction(f, n, x):
    
    result = x
    for _ in range(n):
        result = f(result)
    return result


def square(x):
    return x * x

print(superfunction(square, 3, 2))  