# a = {
#     '111': [],
#     '222': []
# }
# a[list(a.keys())[0]].append('ttt')

# print(a)

a = [i for i in range(23)]

a[20:21] = ['']
print(a)