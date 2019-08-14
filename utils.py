import algorithms.dvr
import algorithms.flooding
import algorithms.lsr

def getAlgorithm(a):
  switcher = {
    "flooding": algorithms.flooding.flooding,
    "dvr": algorithms.dvr.dvr,
    "lsr": algorithms.lsr.lsr
  }
  return switcher.get(a, algorithms.flooding.flooding)
