#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
from pyscipopt import Model, quicksum

Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items= []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))
        
    value, taken = scip_solver(items, capacity)
    
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data
    
def greedy_simple(items, capacity):
    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    
        value = 0
        weight = 0
        taken = [0]*len(items)

        for item in items:
            if weight + item.weight <= capacity:
                taken[item.index] = 1
                value += item.value
                weight += item.weight
                
        return value, taken

def greedy_max_number_of_items(items, capacity):
    #жадный алгоритм, который берет вначале легкие предметы, чтобы поместилось как можно больше предметов
    
        items_ordered = sorted(items, key = lambda x: x.weight) #сортировка по возрастанию веса
        return greedy_simple(items_ordered, capacity)
        
def greedy_most_valuable_items(items, capacity):
    #жадный алгоритм, который берет вначале самые дорогие по стоимости предметы
    
        items_ordered = sorted(items, key = lambda x: x.value, reverse = True) #сортировка по убыванию стоимости
        return greedy_simple(items_ordered, capacity)
        
def greedy_most_value_density_items(items, capacity):
    #жадный алгоритм, который учитывает стоимость и соотношение стоимость - вес
    
        items_ordered = sorted(items, key=lambda x: x.value, reverse=True)
        items_ordered = sorted(items_ordered, key=lambda x: x.value/x.weight, reverse=True)
        return greedy_simple(items_ordered, capacity)
        
def greedy_unique_weight_oredered(items, capacity):
    #жадный алгоритм, который сортирует предметы по весу, но берет только один предмет одного веса
    
    items_ordered = sorted(items, key=lambda x: x.weight)
    current_weight = 0

    value = 0
    weight = 0
    taken = [0]*len(items)

    for item in items:
        if weight + item.weight <= capacity and item.weight != current_weight:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
            current_weight = item.weight
    
    return value, taken
    
def dynamic_programming_simple(items, capacity):
    #динамическое программирование, которое считывает вход в порядке по умолчанию
    
    capacity_range = range(0, capacity+1)
    items_range = range(0, len(items)+1)

    # Составляем таблицу
    # [[v0k0, v0k1, v0k2...], [v1k0, v1k1, v1k2...], ...]
    result_matrix = [[0 for x in capacity_range] for y in items_range]

    # Заполняем колонку для первого предмета
    for j in range(1, len(capacity_range)):
        current_item = items[0]
        if current_item.weight <= j:
            result_matrix[1][j] = current_item.value

    for i in range(2, len(items_range)):
        for j in range(1, len(capacity_range)):
            current_item = items[i-1]
            prev_item_value = result_matrix[i-1][j]
            if current_item.weight <= j:
                # Эта переменная возвращает стоимость из предыдущей колонки из строки с текущей вместимостью (j) минус вес текущего предмета
                item_previous_column_val = \
                    result_matrix[i-1][j-current_item.weight]
                result_matrix[i][j] = max(result_matrix[i-1][j],\
                    current_item.value + item_previous_column_val)
            else:
                result_matrix[i][j] = prev_item_value

    # Восстановление выбранных предметов
    i = len(items)
    j = capacity
    value = 0
    weight = 0
    taken = [0]*i

    while i > 0 and j > 0:
        current_value = result_matrix[i][j]
        prev_value = result_matrix[i-1][j]
        if prev_value != current_value:
            taken[i-1] = 1
            value += items[i-1].value
            j -= items[i-1].weight
        i -= 1

    return value, taken

def depth_first_relaxed_capacity_simple(items, capacity, relaxed_estimate=None):
    # Depth-first алгоритм с релаксацией вместимости
    
        if not relaxed_estimate:
            relaxed_estimate = get_relaxed_capacity_value(items)
        num_items = len(items)
        taken = [0]*num_items

        max_val, taken = process_depth_first(items, capacity, relaxed_estimate, 0, 0, num_items, 0, taken, True)
        max_val, taken = process_depth_first(items, capacity, relaxed_estimate, 0, 0, num_items, max_val, taken, False)

        return max_val, taken
    
def depth_first_relaxed_value_per_kg_simple(items, capacity):
    # Depth-first алгоритм с релаксацией соотношения стоимость - вес
    
        items_ordered = sorted(items, key=lambda x: x.value, reverse=True)
        items_ordered = sorted(items_ordered, key=lambda x: x.value/x.weight, reverse=True)
        relaxed_estimate = get_relaxed_value_per_kg_value(items_ordered, capacity)

        max_val, taken = depth_first_relaxed_capacity_simple(items_ordered, capacity, relaxed_estimate)
        return max_val, taken

def depth_first_ordered_by_weight(items, capacity):
    # Depth-first алгоритм с сортировкой по убыванию веса
    
        items_ordered = sorted(items, key=lambda x: x.weight, reverse=True)
        relaxed_estimate = get_relaxed_value_per_kg_value(items_ordered, capacity)

        max_val, taken = depth_first_relaxed_capacity_simple(items_ordered, capacity, relaxed_estimate)
        return max_val, taken
    
def get_relaxed_capacity_value(items):
    # релаксация вместимости (то есть убираем ограничение на вместимость рюкзака и получаем наибольшую возможную общую стоимость)
    
    value = 0
    for item in items:
        value += item.value

    return value
    
def get_relaxed_value_per_kg_value(items, capacity):
    # релаксация соотношения стоимость - вес (теперь можем брать часть предмета)
    
    value = 0
    weight = 0
    i = 0
    while weight <= capacity and i < len(items):
        item = items[0]
        weight += item.weight
        if weight <= capacity:
            value += item.value
        else:
            diff = capacity - weight - item.weight
            proportion = item.weight/diff
            value += item.value/proportion
        i += 1
        
    return value
    
def process_depth_first(items, capacity, estimate, i, value, num_items, current_max_value, taken, select):
    max_val = current_max_value
    if i < num_items:
        current_item = items[i]
        if select == True: #положили i-ый предмет
            value += current_item.value
            capacity -= current_item.weight
        else:
            estimate -= current_item.value
        
        if capacity < 0: #ушли в минус, добавив предмет, вес которого уже превышает вместимость
            return current_max_value, taken
        if estimate <= current_max_value: #прекращаем вычисления, если уже на каком-то шаге наша наибольшая возможная общая стоимость меньше текущей максимальной стоимости
            return current_max_value, taken
        if value == estimate:
            taken = [0]*num_items
            taken[i] = int(select)
            return value, taken

        # вызываем эту же функцию для следующих предметов
        max_val, taken = process_depth_first(items, capacity, estimate, i+1, value, num_items, max_val, taken, True)
        max_val, taken = process_depth_first(items, capacity, estimate, i+1, value, num_items, max_val, taken, False)
    
        if max_val > current_max_value:
            taken[i] = int(select)
    return max_val, taken
    
def scip_solver(items, capacity):
    
    # создаем модель
    s = Model("Knapsack")
    s.hideOutput() # скрываем вывод
    
    # ставим цель максимизировать стоимость
    s.setMaximize()
    
    weights = [i.weight for i in items]
    costs = [i.value for i in items]
    
    assert len(weights) == len(costs) # проверка на истинность
    
    knapsackSize = capacity
    
    knapsackVars = []
    varNames = []
    varBaseName = "Item"
    for i in range(len(weights)):
        varNames.append(varBaseName + "_" + str(i)) #Item_1
        knapsackVars.append(s.addVar(varNames[i], vtype = 'INTEGER', obj = costs[i], ub = 1.0)) #upperbound
    
    # добавляем ограничение
    s.addCons(quicksum(w*v for (w, v) in zip(weights, knapsackVars)) <= knapsackSize)

    # решаем задачу
    s.optimize()
    
    # возвращаем решение
    value = 0
    taken = [0]*len(items)
    for i in range(len(weights)):
        current_value = round(s.getVal(knapsackVars[i]))
        if current_value > 0:
            value += costs[i]
            taken[i] = 1
        else:
            taken[i] = 0
            
    return value, taken


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

