#script (python)
import clingo
from clingo import *

class Robot(object):
   def __init__(self, ID = None, x = None, y = None, E = None):
      self._ID = ID
      self._firstX = x
      self._firstY = y
      self._x  = 0 if x == None else x
      self._y  = 0 if y == None else y
      self._actions = []
      self._carries = None
      self._lastCarried = None
      self._energy = 1 if E == None else E

   def doAction(self, timeStep):
      if timeStep >= len(self._actions):  return 0  #break, if no action is defined
      if self._actions[timeStep] == None: return 0  #break, if no action is defined
      if self._actions[timeStep].name == "move":
         if len(self._actions[timeStep].arguments) != 2: return -1
         try:
            self._x = self._x + self._actions[timeStep].arguments[0].number
            self._y = self._y + self._actions[timeStep].arguments[1].number
         except:
            self._x = self._x
            self._y = self._y
         if self._carries != None: self._carries.setPosition(self._x, self._y)
         print "Do: Robot ", self._ID, " move to x: ", self._x, " y: ", self._y 
         return 1
      elif self._actions[timeStep].name == "lift":
         print "Do: Robot ", self._ID, " lift"
         return 2
      elif self._actions[timeStep].name == "place":
         if self._carries == None:
            return -3
         self.setCarries(None)
         print "Do: Robot ", self._ID, " place"
         return 3
      elif self._actions[timeStep].name == "charge":
         print "Do: Robot ", self._ID, " charged to ", self._energy
         return 4
      return 0

   def setID(self, robotID):
      self._ID = robotID

   def setPosition(self, x, y):
       if self._firstX == None: self._firstX = x
       if self._firstY == None: self._firstY = y
       self._x = x
       self._y = y

   def setAction(self, action, timeStep):
      if timeStep < 0:
         print "Warning: invalid time step in action: do(", self._ID, ",", action,",", timeStep, ")"
         print "time step is less then 0"
         return
      for ii in range((timeStep + 1) - len(self._actions)):
         self._actions.append(None)
      if self._actions[timeStep] == None:
         self._actions[timeStep] = action
      else:
         print "Warning: for robot(" + str(self._ID) + ") multiple actions are defined at time step: " + str(timeStep)


   def setCarries(self, shelf):
      if shelf == self._carries: return
      self._lastCarried = self._carries
      self._carries = shelf
      if self._lastCarried != None: self._lastCarried.setCarried(None)
      if self._carries != None: self._carries.setCarried(self)
      
   def setEnergy(self, energy):
       self._energy=energy

   def restart(self):
       self._x = self._firstX
       self._y = self._firstY 
       self.setCarries(None)

   def getID(self):
      return self._ID

   def getPositionX(self):
      return self._x

   def getPositionY(self):
      return self._y

   def getAction(self, timeStep):
      if timeStep >= len(self._actions): return Function("idle", [])
      action = self._actions[timeStep]
      if action == None: action = Function("idle", [])
      return action

   def getCarries(self):
      return self._carries   
      
   def getEnergy(self):
      return self._energy

   def getLastCarried(self):
      return self._lastCarried

#end.
