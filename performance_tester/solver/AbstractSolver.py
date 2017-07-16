# script (python)

import clingo
from clingo import *
import os.path
import sys

sys.path.insert(0, './classes')

import robot
from robot import *
import order
from order import *
import shelf
from shelf import *
import pickingStation
from pickingStation import *
import timer
from timer import *


class AbstractSolver(object):
    def __init__(self):

        self._save_execution = False
        self._save_execution_dir = None

        # change to True if you wanna see the solutions each time
        self._show_solution = False

        self._performance_test = False

        self._start_time_step = 0

        self._instance = None
        self._encoding = None

        self._firstInit = None
        self._num_robots = 0  # number of robots
        self._num_shelves = 0  # number of shelves
        self._num_stations = 0  # number of packing stations
        self._num_orders = 0  # number of Orders
        self._num_steps = 1  # number of time steps
        self._grid_size_x = 1  # size of the grid (x-direction)
        self._grid_size_y = 1  # size of the grid (y-direction)

        # self._current_optimization  = 0
        self._solution = False

        self._robots = []  # robots
        self._shelves = []  # shelves
        self._stations = []  # packing stations
        self._orders = []  # orders

        self._time_cpu = 0.
        self._time_solve = 0.
        self._time_sat = 0.
        self._time_unsat = 0.
        self._time_total = 0.

        self._groundTimer = Timer()
        self._solveTimer = Timer()

        self._num_threads = "1"

    def resetTimer(self):
        self._groundTimer.reset()
        self._solveTimer.reset()

    def getNumOfUnfullfilledOrders(self):
        num = 0
        for order in self.getOrders():
            if not order.isFulfilled():
                num += 1
        return num

    def setPerformanceTest(self, perfTest):
        self._performance_test = perfTest

    def setSaveExecutionDirecory(self, saveDir):
        if saveDir != None:
            self._save_execution = True
            if saveDir.endswith('/'):
                saveDir = saveDir[:-1]
            self._save_execution_dir = saveDir

    def setThreads(self, threads):
        self._num_threads = threads

    def setEncoding(self, encoding):
        if not os.path.isfile(encoding):
            print "can't open file: ", encoding
            return
        self._encoding = encoding

    def setInstance(self, instance):
        if not os.path.isfile(instance):
            print "can't open file: ", instance
            return False

        print "Loading init file: ", instance
        self._instance = instance
        show_soluition_before = self._show_solution
        self._show_solution = False

        try:
            prg = clingo.Control(["-t", self._num_threads, "--stats=1"])
            prg.load(instance)

            prg.ground([("base", [])])

            for x in prg.symbolic_atoms:
                if x.symbol.name == "init" and x.symbol.arguments[0].arguments[0].name == "node":
                    try:
                        if x.symbol.arguments[1].arguments[1].arguments[0].number > self.getGridSizeX():
                            self._grid_size_x = x.symbol.arguments[1].arguments[1].arguments[0].number
                        if x.symbol.arguments[1].arguments[1].arguments[1].number > self.getGridSizeY():
                            self._grid_size_y = x.symbol.arguments[1].arguments[1].arguments[1].number
                    except:
                        print #TODO

            # get constants
            #self._grid_size_x = prg.get_const("Grid Size X:").number
            #self._grid_size_y = prg.get_const("Grid Size Y:").number
            #self._max_energy = prg.get_const("max_energy").number
            #self._num_items = prg.get_const("num_items").number
            #self._num_stations = prg.get_const("num_packingStations").number


            prg.solve(self.on_model)
            self._show_solution = show_soluition_before
            return True
        except RuntimeError as error:
            self._show_solution = show_soluition_before
            print error
            return False

    def _get(self, val, default):
        return val if val != None else default


    def on_model(self, m):
        self._solveTimer.stop()
        # print m.atoms(Model.SHOWN)
        #if (self._show_solution):
        #    print "solution found:"
        #    print m.symbols(atoms=True)
        self._num_robots = 0  # reset parameter
        self._num_shelves = 0
        self._num_stations = 0
        self._num_charger = 0
        self._num_steps = 1
        self._robots = []
        self._shelves = []
        self._stations = []
        self._orders = []

        ##        if len(m.optimization()) != 0:
        ##         if m.optimization()[0] > self._current_optimization and self._current_optimization != 0:
        ##            return True   #quit function if the new solution is not better than the old
        ##         self._current_optimization = m.optimization()[0]
        ##         print "optimization: ", m.optimization()[0]

        for x in m.symbols(atoms=True):
            # inits
            try:
                if x.name == "init" and x.arguments[1].arguments[0].name == "at":
                    try:
                        if x.arguments[0].arguments[0].name == "robot":  # init robots
                            robot = self.getRobot2(x.arguments[0].arguments[1].number)
                            robot.setPosition(x.arguments[1].arguments[1].arguments[0].number, x.arguments[1].arguments[1].arguments[1].number)
                        elif x.arguments[0].arguments[0].name == "shelf":  # inits shelves
                            shelf = self.getShelf2(x.arguments[0].arguments[1].number)
                            shelf.setPosition(x.arguments[1].arguments[1].arguments[0].number, x.arguments[1].arguments[1].arguments[1].number)
                        elif x.arguments[0].arguments[0].name == "pickingStation":  # init packing stations
                            station = self.getStation2(x.arguments[0].arguments[1].number)
                            station.setPosition(x.arguments[1].arguments[1].arguments[0].number, x.arguments[1].arguments[1].arguments[1].number)
                    except:
                         print ("invalid init format, exspecting: init(robot([RobotID]), [X], [Y]) or",
                                "init(shelf([ShelfID]), [X], [Y]) or ",
                                "init(pickingStation([PickingStationID]), [X], [Y])")
                         print "May be unexpected error:", sys.exc_info()[0]
                elif x.name == "init" and x.arguments[1].arguments[0].name == "on":  # init items
                    try:
                        if x.arguments[0].arguments[0].name == "product":
                            shelf = self.getShelf2(x.arguments[1].arguments[1].arguments[0].number)
                            shelf.addItem(x.arguments[0].arguments[1].number, x.arguments[1].arguments[1].arguments[1].number)
                    except:
                        print "invalid init format, exspecting: init(item([ItemID]), shelf([ShelfID]))"
                # orders
                elif x.name == "init" and x.arguments[0].arguments[0].name == "order":
                    try:
                        if x.arguments[1].arguments[0].name == "line":
                            order = self.getOrders2(x.arguments[0].arguments[1].number)
                            order.addProduct(x.arguments[1].arguments[1].arguments[0].number, x.arguments[1].arguments[1].arguments[1].number)
                        if x.arguments[1].arguments[0].name == "pickingStation":
                            order = self.getOrders2(x.arguments[0].arguments[1].number)
                            order.setStation(self.getStation2(x.arguments[1].arguments[1].number))
                    except:
                        print "invalid order format, exspecting: order(item([ItemID]), pickingStation([PickingStationID]))"
                # do
                elif x.name == "do" and len(x.arguments) == 3:
                    try:
                        if x.arguments[0].name == "robot":
                            robotid = x.arguments[0].arguments[0].number
                        else:
                            robotid = x.arguments[0].number
                        # if not isinstance(x.arguments[0].number, Function):
                        #    robotid = x.arguments[0].number
                        # elif x.arguments[0].name == "robot":
                        #    robotid = x.arguments[0].arguments[0].number
                        # else:
                        #    raise Exception()
                        robot = self.getRobot2(robotid)
                        time = self._start_time_step + x.arguments[2].number
                        robot.setAction(x.arguments[1], time)
                        if time > self._num_steps: self._num_steps = time
                    except:
                        print "invalid do format, exspecting: do([RobotID], [Action], [TimeStep]) or do(robot([RobotID]), [Action], [TimeStep])"
                        print x.arguments[0].name == "robot"
            except:
                pass
        self._solution = True
        return True

    def solve(self, start_time_step):
        print "Error: you need to implement the solve method!"
        return False

    def getRobot(self, robotID):
        for robot in self._robots:
            if robot.getID() == robotID: return robot
        return None

    def getRobot2(self, robotID):
        for robot in self._robots:
            if robot.getID() == None:
                robot.setID(robotID)
                return robot
            elif robot.getID() == robotID:
                return robot
        self._robots.append(Robot())
        robot = self._robots[len(self._robots) - 1]
        self._num_robots = len(self._robots)
        robot.setID(robotID)
        return robot

    def getRobots(self):
        return self._robots

    def getShelf(self, shelfID):
        for shelf in self._shelves:
            if shelf.getID() == shelfID: return shelf
        return None

    def getShelf2(self, shelfID):
        for shelf in self._shelves:
            if shelf.getID() == None:
                shelf.setID(shelfID)
                return shelf
            elif shelf.getID() == shelfID:
                return shelf
        self._shelves.append(Shelf())
        shelf = self._shelves[len(self._shelves) - 1]
        self._num_shelves = len(self._shelves)
        shelf.setID(shelfID)
        return shelf

    def getShelves(self):
        return self._shelves

    def getStation(self, pickingStationID):
        for station in self._stations:
            if station.getID() == pickingStationID: return station
        return None

    def getStation2(self, pickingStationID):
        for station in self._stations:
            if station.getID() == None:
                station.setID(pickingStationID)
                return station
            elif station.getID() == pickingStationID:
                return station
        self._stations.append(PickingStation())
        station = self._stations[len(self._stations) - 1]
        self._num_stations = len(self._stations)
        station.setID(pickingStationID)
        return station

    def getOrders2(self, orderID):
        for order in self._orders:
            if order.getID() == None:
                order.setID(orderID)
                return order
            elif order.getID() == orderID:
                return order
        self._orders.append(Order())
        order = self._orders[len(self._orders) - 1]
        self._num_orders = len(self._orders)
        order.setID(orderID)
        return order

    def getStations(self):
        return self._stations

    def getOrders(self):
        return self._orders

    def getGridSizeX(self):
        return self._grid_size_x

    def getGridSizeY(self):
        return self._grid_size_y

    def getNumSteps(self):
        return self._num_steps

    def getNumRobots(self):
        return self._num_robots

    def getNumShelves(self):
        return self._num_shelves

    def getNumStations(self):
        return self._num_stations

    def getNumCharger(self):
        return self._num_charger

    def getInitFile(self):
        return self._initFile

    def incomingOrder(self, newOrderProduct, newOrderStation, time_step):
        print "Incoming order: ", newOrderProduct, ", ", newOrderStation
        self._orders.append(Order(newOrderProduct, newOrderStation))
        return self.solve(time_step)

    def _removeOrder(self, item, station):
        for order in self._orders:
            if order.getItemID() == item and order.getStationID() == station:
                self._orders.remove(order)
                return True
        return False



    def getReturn (self, SAT, statistics, symbolic_atoms):
        if self._performance_test:
            return SAT, self._solveTimer.getAccuTime() + self._groundTimer.getAccuTime(), self._groundTimer.getAccuTime(), self._solveTimer.getAccuTime(), statistics['problem']['generator']['constraints'], statistics['problem']['generator']['vars'], statistics['solving']['solvers']['conflicts'], statistics['solving']['solvers']['choices'], statistics['solving']['solvers']['restarts']
        else:
            for x in symbolic_atoms:
                print x.symbol
            return SAT, self._solveTimer.getAccuTime() + self._groundTimer.getAccuTime(), self._groundTimer.getAccuTime(), self._solveTimer.getAccuTime(), statistics['problem']['generator']['constraints'], statistics['problem']['generator']['vars'], statistics['solving']['solvers']['conflicts'], statistics['solving']['solvers']['choices'], statistics['solving']['solvers']['restarts']



# end.
