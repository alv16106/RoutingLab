import algorithms.dvr
import algorithms.flooding
import algorithms.lsr

def getTopology(file):
  relations = []
  f = open(file)
  for line in f:
    relation = line[:-1].split(" ")
    relation[2] = int(relation[2])
    relations.append(relation)
  return relations

def getNeighbours(relations, name):
  neighbours = []
  for r in relations:
    if (r[0] == name):
      neighbours.append({"neighbour": r[1], "distance": r[2]})
    elif (r[1] == name):
      neighbours.append({"neighbour": r[0], "distance": r[2]})
  print(neighbours)
  return neighbours

def getAlgorithm(a):
  switcher = {
    "flooding": algorithms.flooding.flooding,
    "dvr": algorithms.dvr.dvr,
    "lsr": algorithms.lsr.lsr
  }
  return switcher.get(a, algorithms.flooding.flooding)
