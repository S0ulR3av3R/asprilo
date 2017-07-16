#script (python)

class Order(object):

    def __init__(self, ID = None):
        self._ID = ID
        self._stationID = None
        self._station   = None
        self._shelves   = []
        self._fulfilled = False
        self._products = []
        self._starttime = 0

    def setID(self, orderID):
        self._ID = orderID

    def addProduct(self, productID, amount):
        self._products.append([productID,amount])

    def setStationID(self, stationID):
        self._stationID = stationID

    def setStation(self, station):
        self.setStationID(station.getID())
        self._station = station

    def addShelf(self, shelf):
        self._shelves.append(shelf)

    def setFulfilled(self, fulfilled):
        self._fulfilled = fulfilled

    def isFulfilled(self):
        return self._fulfilled

    def getID(self):
        return self._ID

    def getProducts(self):
        return self._products

    def getStationID(self):
      return self._stationID

    def getStation(self):
      return self._station

    def getShelves(self):
      return self._shelves

    def getFulfilled(self):
      return self._fulfilled

    def getStartTime(self):
        return self._starttime

    def checkShelf(self, shelf):
        if self._station == None:
         print "None Station!"
        if shelf.getPositionX() == self._station.getPositionX() and shelf.getPositionY() == self._station.getPositionY() and shelf.contains(self._products):
         return True
        else:
         return False
#end.
