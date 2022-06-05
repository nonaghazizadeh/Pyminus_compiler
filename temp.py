#  ===  Recursive Sample 2  ===
count = 0
result = [0, 0, 0, 0]


def f(a, result):
    global count
    count = count + 1
    print(f'a: {a}')
    print(f'result: {result}')

    if 0 < result[a - 1]:
        return result[a - 1]
    else:
        if a == 1:
            result[a - 1] = 1
            return 1
        else:
            if a == 2:
                result[a - 1] = 1
                return 1
            else:
                result[a - 1] = f(a - 2, result) + f(a - 1, result)
                return result[a - 1]


if __name__ == '__main__':
    i = 0
    print(f(4, result))
    print(count)
