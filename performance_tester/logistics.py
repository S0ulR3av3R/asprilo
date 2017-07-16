#script (python)


import os
import sys, getopt
import multiprocessing
import re
sys.path.insert(0, './visualizer')
sys.path.insert(0, './classes')
import clingo
from clingo import *

import robot
from robot import *
import shelf
from shelf import *
import GroundSolver
from GroundSolver import *
import ExternalsSolver
from ExternalsSolver import *
import visualizer
from visualizer import *

def get(val, default):
    return val if val != None else default


def on_model(m):
    print m.atoms()
    
def print_help():
    print 'logistics.py arguments:'
    print '\t-h, --help\tHelp'
    print '\t-e, --encoding <encoding_file>\tEncoding file (default: encoding_test.lp)'
    print '\t-i, --instance <instance_file>\tInstance file'
    print '\t-p, --performance <Test directory>\tdirectory with instances for performance tests (recursive)'
    print '\t-s, --solver <solver>\tsolver: {external | ground} (default: ground)'
    print '\t--save <directory> save incremental execution in <directory>'
    print '\t-l, -load <directory>\tload incrementally execution for <directory>'
    print '\t-t <threads>\tnumber of threads (default: 1)'


def setSolver(solverType, instance):
    if solverType == "ground":
        solver = GroundSolver()
    elif solverType == "external":
        solver = ExternalsSolver()
            
    solver.setEncoding(encoding)
    solver.setInstance(instance)
    return solver        
    
def getInstances(instance_dir):
    instances =[]
    for dir, subdirs, files in os.walk(instance_dir):
        for name in files:
            if name.endswith(".lp"):
                print os.path.join(dir,name)
                instances.append(os.path.join(dir,name))
    return instances


def main():
    instance = None
    mode = "normal" #normal vs load  vs testall
    save_dir = None
    test_dir = None
    instance_dir = None
    solverType = "ground"
    threads = str(multiprocessing.cpu_count())

    try:
        opts, args = getopt.getopt(sys.argv[1:],"he:m:i:p:s:t:",["help","encoding=","instance=","performance","solver="])
    except getopt.GetoptError:
        print_help()
        sys.exit(-1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help()
            sys.exit()
        elif opt in ("-e", "--encoding"):
            encoding = arg
        elif opt in ("-i", "--instance"):
            instance = arg
        elif opt in ("-p", "--performance"):
            instance_dir = arg
            mode = "testall"
        elif opt in ("-s","--solver"):
            if arg in ("external","ground"):
                solverType = arg
            else:
                print "Error: unknown solver: ", arg
                sys.exit(-1)
        elif opt in ("-t"):
            threads=arg
 
    
    
    if(mode == "normal"):
        solver = setSolver(solverType, instance)
        solver.setThreads(threads)

        solver.solve(0)


        #visualizer = Visualizer()
        #visualizer.setSolver(solver)
        #visualizer.visualize()
        

          
          
          
    elif(mode == "testall"):
        tt = 0  #sum of total times
        gt = 0  #sum of gorund times
        st = 0  #sum of solve times
        ch = 0  #sum of choice rules
        cc = 0  #sum of constraint rules
        cf = 0  #sum of conflicts
        re = 0  #sum of restarts
        va = 0  #sum of variables
        roundTo = 3

        oFile = open("stats", "w")
        oFile.write("Test \t\t\t\t\t\t\t\t\ttotal_time \tground_time \tsolve_time \tsteps\t\tSAT\t\t\tSolverType\tconstraints\tvariables\tconflicts\tchoices\trestarts\n")


        alltests =  getInstances(instance_dir)


        for test in alltests:
            solver = setSolver(solverType, test)
            solver.setPerformanceTest(True)
            solver.setThreads(threads)

            result, total_time, ground_time, solve_time, constr, vars, confl, choices, restarts = solver.solve(0)

            #if not result:
            #    continue
            tt += total_time
            gt += ground_time
            st += solve_time
            ch += choices
            cc += constr
            cf += confl
            re += restarts
            va += vars
            string = "{}\t\t\t{:.3f}\t\t{:.3f}\t\t{:.3f}\t\t{}\t\t\t{}\t\t{}\t\t{}\t\t\t{}\t\t\t{}\t\t\t{}\t\t\t{}\n".format(os.path.basename(test), total_time, ground_time, solve_time, solver._num_steps, result, solverType, int(constr), int(vars), int(confl), int(choices), int(restarts))
            oFile.write(string)
            print unichr(157)

        oFile.write("TOTAL \t\t\t\t\t\t\t\t\t\t"+str(round(tt,3))+"\t\t"+str(round(gt,3))+"\t\t"+str(round(st,3))+"\t\t\t\t\t\t\t\t\t\t\t"+str(int(cc))+"\t\t\t"+str(int(va))+"\t\t\t"+str(int(cf))+"\t\t\t"+str(int(ch))+"\t\t\t"+str(int(re))+"\n")
        oFile.write("number of Threads: " + threads)
        oFile.close()
        os.system("cat stats")

      
            
encoding = "encoding/encoding_toot.lp"
main()

#end.
