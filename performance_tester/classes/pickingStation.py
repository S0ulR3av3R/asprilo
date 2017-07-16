#script (python)

class PickingStation(object):
   def __init__(self):
      self._ID = None
      self._x  = 0
      self._y  = 0

   def setID(self, pickingStationID):
      self._ID = pickingStationID

   def setPosition(self, x, y):
       self._x = x
       self._y = y

   def getID(self):
      return self._ID

   def getPositionX(self):
      return self._x

   def getPositionY(self):
      return self._y   

#end.
