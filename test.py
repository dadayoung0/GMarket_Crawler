a = {
    '111': [],
    '222': []
}
a[list(a.keys())[0]].append('ttt')

print(a)