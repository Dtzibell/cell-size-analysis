
```
DFS-shortest-dist(G,s,t):
shortest_dists = list;
for v in s.edges:
    shortest_dist = 0
    if v == t:
        return shortest_dist
    else:
        shortest_dist += DFS-shortest-dist(G, v, t)
        
        
```
