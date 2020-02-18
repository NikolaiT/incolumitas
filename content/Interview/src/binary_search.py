def binary_search(lst, value):
    count = len(lst)
    first = 0

    while count:
        it = first
        step = count // 2
        it += step
        if value > lst[it]:
            it += 1
            first = it
            count -= step + 1
        else:
            count = step

    return first
        

print(binary_search([1,2,3,5,6,7,10], 4))

"""
[1,2,3,4,23,55,88,99,101] 90
m = 9
k = 4
a[4] = 23
90 > 23 => [4,9]

r = 0,5
k = (5-0)/2 = 2.5 

"""
