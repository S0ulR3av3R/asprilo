#script (python)

class Shelf(object):
   def __init__(self, ID = None, x = None, y = None):
      self._ID = ID
      self._firstX = x
      self._firstY = y
      self._x  = 0 if x == None else x
      self._y  = 0 if y == None else y
      self._carried = None
      self._items   = []

   def setID(self, shelfID):
      self._ID = shelfID

   def setPosition(self, x, y):
       if self._firstX == None: self._firstX = x
       if self._firstY == None: self._firstY = y
       self._x = x
       self._y = y

   def setCarried(self, robot):
      if robot == self._carried: return
      old = self._carried
      self._carried = robot
      if old           != None: old.setCarries(None)
      if self._carried != None: self._carried.setCarries(self)

   def restart(self):
       self._x = self._firstX
       self._y = self._firstY      

   def addItem(self, item, amount):
      self._items.append([item,amount])

   def contains(self, item):
      for item2 in self._items:
         if item == item2: return True
      return False

   def getID(self):
      return self._ID

   def getPositionX(self):
      return self._x

   def getPositionY(self):
      return self._y

   def getCarried(self):
      return self._carried     

   def getItems(self):
      return self._items

#end.
