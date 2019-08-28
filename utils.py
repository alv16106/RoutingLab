import algorithms.dvr
import algorithms.flooding
import algorithms.lsr
import json

def getTopology(file):
  relations = []
  f = open(file)
  for line in f:
    relation = line[:-1].split(" ")
    relation[2] = int(relation[2])
    relations.append(relation)
  return relations

def getNeighbours(relations, name):
  neighbours = {}
  for r in relations:
    if (r[0] == name):
      neighbours[r[1]] = r[2]
    elif (r[1] == name):
      neighbours[r[0]] = r[2]
  return neighbours

def getAlgorithm(a):
  switcher = {
    "flooding": algorithms.flooding.flooding,
    "dvr": algorithms.dvr.dvr,
    "lsr": algorithms.lsr.lsr
  }
  return switcher.get(a, algorithms.flooding.flooding)

def generateLSP(node, neighbour_info, serial):
  return json.dumps({
    'node': node,
    'neighbourhood': neighbour_info,
    'serial': serial,
  })
