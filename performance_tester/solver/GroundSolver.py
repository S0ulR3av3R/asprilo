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


class GroundSolver(AbstractSolver):
    def __init__(self):
        AbstractSolver.__init__(self)
    
    def solve(self, start_time_step):
    
        self._start_time_step = start_time_step
        self._solution = False
        print "Start solving..."
        prg = clingo.Control(["-t", self._num_threads, "--stats=1"])
        prg.load(self._instance)         #load the instance
        prg.load(self._encoding)    #load the solver of the problem
        prg.load("encoding/init_encoding_ground.lp")     #load the init encoding part for grounding

        saveFile = None
        if(self._save_execution):
            if(start_time_step<10):
              filename = "{}/init00{}.lp".format(self._save_execution_dir,start_time_step)
            elif(start_time_step<100):
              filename = "{}/init0{}.lp".format(self._save_execution_dir,start_time_step)
            else:
              filename = "{}/init{}.lp".format(self._save_execution_dir,start_time_step)
            saveFile = open(filename, "w")

        imax = int(self.getNumOfUnfullfilledOrders()) + len(self._shelves) + len(self._robots) + 30

        try:
            step, ret = 0, False
            while (not ret):
                if not self._performance_test: print "ground step: ", step

                if step > imax:
                    if not self._performance_test:
                        inputStr = raw_input("Number of steps is bigger than maximum. If you want to continue solving, enter new maximum: ")
                        try:
                            newMax = int(inputStr)
                            imax = newMax
                        except:
                            return self.getReturn(False, prg.statistics, prg.symbolic_atoms)
                    else:
                        return self.getReturn(False, prg.statistics, prg.symbolic_atoms)

                parts = []
                if step == 0:
                  #initialize
                    for robot in self.getRobots():
                        parts.append(("initRobot",[robot.getID(), robot.getPositionX(), robot.getPositionY()]))
                        if robot.getCarries() != None:
                            parts.append(("initLifted",[robot.getID(), robot.getCarries().getID()]))
                        if(self._save_execution and saveFile != None):
                            string = "init(robot({}), {}, {}).\n".format(robot.getID(),robot.getPositionX(), robot.getPositionY())
                            if robot.getCarries() != None:
                                string += "init(lifted({}, {})).\n".format(robot.getID(), robot.getCarries().getID())
                            saveFile.write(string)
                        print "add Robot: ", robot.getID(), robot.getPositionX(), robot.getPositionY()
                        if robot.getCarries() != None:
                            print "lifted: ", robot.getID(), robot.getCarries().getID()
                    for shelf in self.getShelves():
                        parts.append(("initShelf",[shelf.getID(), shelf.getPositionX(), shelf.getPositionY()]))
                        if(self._save_execution and saveFile != None):
                            string = "init(shelf({}), {}, {}).\n".format(shelf.getID(),shelf.getPositionX(), shelf.getPositionY())
                            saveFile.write(string)
                        print "add Shelf: ", shelf.getID(), shelf.getPositionX(), shelf.getPositionY()
                        for item in shelf.getItems():
                            parts.append(("initProduct", [item[0], item[1], shelf.getID()]))
                            if(self._save_execution and saveFile != None):
                                string = "init(product({}), shelf({})).\n".format(item, shelf.getID())
                                saveFile.write(string)
                            print "   add Product: ", item, shelf.getID()
                    for order in self.getOrders():
                        if order.isFulfilled() == False and order.getStartTime() == 0:
                            for product in order.getProducts():
                                parts.append(("initOrder", [order.getID(), product[0], order.getStationID()]))
                            if(self._save_execution and saveFile != None):
                                string = "request(item({}), pickingStation({})).\n".format(order.getItemID(), order.getStationID())
                                saveFile.write(string)
                            print "add Order: ", order.getID(), order.getProducts(), order.getStationID()
                    if(self._save_execution and saveFile != None):
                        saveFile.close()

                parts.append(("check", [step]))
                if step > 0:
                    #for order in self.getOrders():
                    #    if order.isFulfilled() == False and order.getStartTime() == step:
                    #        for product in order.getProducts():
                    #            parts.append(("initOrder", [order.getID(), product[0], order.getStationID()]))
                    prg.release_external(clingo.Function("query", [step-1]))
                    parts.append(("step", [step]))
                    prg.cleanup()
                else:
                    parts.append(("base", []))

                self._groundTimer.start()
                prg.ground(parts)
                self._groundTimer.stop()
                if not self._performance_test: print "ground time: ", round(self._groundTimer.getLastSecs(),4)

                prg.assign_external(clingo.Function("query", [step]), True)

                if not self._performance_test: print "solve step: ", step
                self._solveTimer.start()
                ret, step = prg.solve(on_model=super(GroundSolver, self).on_model).satisfiable, step+1
                self._solveTimer.stop()
                if not self._performance_test:
                    print "solve time: ", round(self._solveTimer.getLastSecs(),4)
                    print prg.solve(on_model=super(GroundSolver, self).on_model)
                    print
                self._num_steps = step

                
        except RuntimeError as error:
            print error
            return self.getReturn(False, prg.statistics, prg.symbolic_atoms)

        json.dumps(prg.statistics, sort_keys=True, indent=4, separators=(',', ': '))

        return self.getReturn(True, prg.statistics, prg.symbolic_atoms)
#end.
