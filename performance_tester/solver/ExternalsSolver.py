#script (python)

import clingo
from clingo import *
import os.path
import sys
sys.path.insert(0, './solver')
sys.path.insert(0, './classes')

import robot
from robot import *
import order
from order import *
import shelf
from shelf import *
import pickingStation
from pickingStation import *
import AbstractSolver
from AbstractSolver import *


import json


class ExternalsSolver(AbstractSolver):
    def __init__(self):
        AbstractSolver.__init__(self)
        self._prg = clingo.Control(["-t", self._num_threads, "--stats=1"])
        self._groundStep = -1


    
    def solve(self, start_time_step):

        self._start_time_step = start_time_step
        self._solution = False
        print "Start solving..."
        print "Start time step: ", start_time_step
        if (start_time_step == 0):
            self._prg.load(self._instance)         #load the map
            self._prg.load(self._encoding)    #load the solver of the problem
            #self._prg.load("encoding/init_encoding_externals.lp")     #load the init encoding part for externals

        saveFile = None
        if(self._save_execution):
            if(start_time_step<10):
              filename = "{}/init00{}.lp".format(self._save_execution_dir,start_time_step)
            elif(start_time_step<100):
              filename = "{}/init0{}.lp".format(self._save_execution_dir,start_time_step)
            else:
              filename = "{}/init{}.lp".format(self._save_execution_dir,start_time_step)
            saveFile = open(filename, "w")

        imax = int(self.getNumOfUnfullfilledOrders()) + len(self._shelves) + len(self._robots) + 10
        try:
            step, ret = 0, False
            while (not ret):

                if step > imax:
                    if not self._performance_test:
                        inputStr = raw_input(
                            "Number of steps is bigger than maximum. If you want to continue solving, enter new maximum: ")
                        try:
                            newMax = int(inputStr)
                            imax = newMax
                        except:
                            return self.getReturn(False, self._prg.statistics, self._prg.symbolic_atoms)
                    else:
                        return self.getReturn(False, self._prg.statistics, self._prg.symbolic_atoms)

                parts = []


                if self._groundStep < step:
                    parts.append(("check", [step]))
                    if step > 0:
                        parts.append(("step", [step]))
                        #self._prg.cleanup_domains()
                    else:
                        parts.append(("base", []))
                    self._groundStep = step
                    if not self._performance_test: print "ground step: ", self._groundStep
                    self._groundTimer.start()
                    self._prg.ground(parts)
                    self._groundTimer.stop()
                    if not self._performance_test: print "ground time: ", round(self._groundTimer.getLastSecs(), 4)

                
                if step > 0:
                    self._prg.assign_external(clingo.Function("query", [step-1]),False)
                self._prg.assign_external(clingo.Function("query", [step]), True)

                if step == 0:
                  #initialize
                    if (start_time_step > 0):
                        for robot in self.getRobots():
                            for x in xrange(1,self._grid_size_x+1):
                                for y in xrange(1,self._grid_size_y+1):
                                    self._prg.assign_external(clingo.Function("init",[clingo.Function("robot",[robot.getID()]), x, y]),False)
                                    #print "falsify robot:", robot.getID(), x, y
                            for shelf in self.getShelves():
                                self._prg.assign_external((clingo.Function("init",[clingo.Function("lifted",[robot.getID(),shelf.getID()])])),False)
                                #print "falsify lifted:", robot.getID(), shelf.getID()
                                
                        for shelf in self.getShelves():
                            for x in xrange(1,self._grid_size_x+1):
                                for y in xrange(1,self._grid_size_y+1):
                                    self._prg.assign_external(clingo.Function("init",[clingo.Function("shelf",[shelf.getID()]), x, y]),False)
                                    #print "falsify shelf:", shelf.getID(), x, y
                            for i in xrange(1,self._num_products+1):
                                self._prg.assign_external(clingo.Function("ison",[clingo.Function("product",[i]), clingo.Function("shelf",[shelf.getID()])]),False)
                                #print "falsify item:", i, shelf.getID()
                        for s in xrange(1,self._num_stations+1):
                            for i in xrange(1,self._num_items+1):
                                self._prg.assign_external(clingo.Function("order",[clingo.Function("product",[i]), clingo.Function("pickingStation",[s])]),False)
                                #print "falsify request:", i, s
                                


                    #assign new externals
                    for robot in self.getRobots():
                        self._prg.assign_external(clingo.Function("init",[clingo.Function("robot",[robot.getID()]), robot.getPositionX(), robot.getPositionY()]),True)
                        if (robot.getCarries() != None):
                            self._prg.assign_external(clingo.Function("init",[clingo.Function("lifted",[robot.getID(),robot.getCarries().getID()])]),True)
                        if(self._save_execution and saveFile != None):
                            string = "init(robot({}), {}, {}).\n".format(robot.getID(),robot.getPositionX(), robot.getPositionY())
                            if (robot.getCarries() != None):
                                string += "init(lifted({}, {})).\n".format(robot.getID(), robot.getCarries().getID())
                            saveFile.write(string)
                        print "add Robot: ", robot.getID(), robot.getPositionX(), robot.getPositionY(), robot.getEnergy()
                        if (robot.getCarries() != None):
                            print "lifted: ", robot.getID(), robot.getCarries().getID()
                    for shelf in self.getShelves():
                        self._prg.assign_external(clingo.Function("init",[clingo.Function("shelf",[shelf.getID()]), shelf.getPositionX(), shelf.getPositionY()]),True)
                        if(self._save_execution and saveFile != None):
                            string = "init(shelf({}), {}, {}).\n".format(shelf.getID(),shelf.getPositionX(), shelf.getPositionY())
                            saveFile.write(string)
                        print "add Shelf: ", shelf.getID(), shelf.getPositionX(), shelf.getPositionY()
                        for item in shelf.getItems():
                            self._prg.assign_external(clingo.Function("init",[clingo.Function("product",[item[0]]), clingo.Function("shelf",[shelf.getID()])]),True)
                            if(self._save_execution and saveFile != None):
                                string = "init(product({}), shelf({})).\n".format(item, shelf.getID())
                                saveFile.write(string)
                            print "   add Product: ", item, shelf.getID()
                    for order in self.getOrders():
                        if not order.isFulfilled():
                            for product in order.getProducts():
                                self._prg.assign_external(clingo.Function("order",[order.getID(), clingo.Function("product", [product[0]]), clingo.Function("pickingStation",[order.getStationID()])]),True)
                            if(self._save_execution and saveFile != None):
                                string = "request(item({}), pickingStation({})).\n".format(order.getItemID(), order.getStationID())
                                saveFile.write(string)
                            print "add Order: ", order.getID(), order.getProducts(), order.getStationID()
                        
                    if(self._save_execution and saveFile != None):
                        saveFile.close()


                if not self._performance_test: print "solve step: ", step
                self._solveTimer.start()
                ret, step = self._prg.solve(on_model=super(ExternalsSolver, self).on_model).satisfiable, step+1
                self._solveTimer.stop()
                if not self._performance_test:
                    print "solve time: ", round(self._solveTimer.getLastSecs(),4)
                    print self._prg.solve(on_model=super(ExternalsSolver, self).on_model)
                    print
                self._num_steps = step

                
        except RuntimeError as error:
            print error
            return self.getReturn(False, self._prg.statistics, self._prg.symbolic_atoms)


        json.dumps(self._prg.statistics, sort_keys=True, indent=4, separators=(',', ': '))

        return self.getReturn(True, self._prg.statistics, self._prg.symbolic_atoms)
#end.
