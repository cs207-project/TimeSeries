import sys

class PypeSyntaxError(Exception): pass
class PypeTypeError(Exception): pass

def Warn(msg):
  sys.stderr.write('PypeWarning: '+str(msg)+'\n')
