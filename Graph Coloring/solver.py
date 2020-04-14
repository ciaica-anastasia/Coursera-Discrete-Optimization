#!/usr/bin/python
# -*- coding: utf-8 -*-

from constraint import *

def solve_it(inputData):
    # parse the input
    lines = inputData.split('\n')

    firstLine = lines[0].split()
    nodeCount = int(firstLine[0])
    edgeCount = int(firstLine[1])

    edges = []
    for i in range(1, edgeCount + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))
    
    i = 0
    sols = None
    
    while sols is None:
        maxColors = i + 1
        model = Problem()
        model.addVariables(range(nodeCount), range(0, maxColors)) #порядковые номера узлов + область допустимых значений
    
        for i in range(len(edges)): #по всем ребрам
            thisedge = edges[i]
            first = thisedge[0] #первый узел
            second = thisedge[1] #второй узел
            model.addConstraint(AllDifferentConstraint(), [first,second]) #две различные переменные должны иметь различные значения
        
        sols = model.getSolution()

    solution = []
    for i in range(nodeCount): #по всем узлам
        solution.append(sols[i] - 1) #приписываем в список solution покраску узла
    
    # prepare the solution in the specified output format
    output_data = str(max(solution) + 1) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileLocation = sys.argv[1].strip()
        inputDataFile = open(fileLocation, 'r')
        inputData = ''.join(inputDataFile.readlines())
        inputDataFile.close()
        print solve_it(inputData)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'
