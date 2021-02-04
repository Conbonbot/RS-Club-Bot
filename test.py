current_queues = [(11, 2), (10, 2)]
adding_queue = (11, -1)
current_queues.append(adding_queue)
D = {}
for (x, y) in current_queues:
  if x not in D.keys():
    D[x] = y
  else:
    D[x] += y
N = [(x, D[x]) for x in D.keys()]
print(N)