import numpy as np
import pylab
import itertools
import PyMark
import csv
import time

class GeneticAlgorithm:

    D = 10 # Dimension of the search space
            # number of attributes 
    N = 25 # Size of the population of solutions
    T = 20 # Number of generations.
    p_c = 0.25 # Crossover probability
    p_m = 0.4 # Mutation probbability
    Z = 1 # For evaluation, it is a good idea to run the algorithms several times,
            # to find out whether it consistently gives good results.  

    types = None
    attributes = None
    rules = None
    results = None 

    ruleInput = None

    def __init__(self, ruleInput='rules.csv'):
        self.ruleInput = ruleInput
        self.types, self.attributes, self.rules, self.results = PyMark.readRules(ruleInput)
        self.D = len(self.attributes)
        #self.types = {k : v if not isinstance(v, list) or '..' not in v else range(int(v.split('..')[0]), int(v.split('..')[1])) for k, v in self.types.items()}
        newTypes = {}
        for t, v in self.types.items():
            if '..' in v: 
                vSplit = v.split('..')
                newTypes[t] = range(int(v.split('..')[0]), int(v.split('..')[1])+1)
            else: newTypes[t] = v
        self.types = newTypes


    def setParam(self, N, T, p_c, p_m, Z):
        self.N = N
        self.T = T
        self.p_c = p_c
        self.p_m = p_m
        self.Z = Z

    def roulette_wheel_selection(self, sorted_pop, fitness_list):
        intermediate_pop = []
        select_from = np.arange(self.N) 
        #fitness_list = [rf * -1 if rf < 0 else rf for rf in fitness_list]
        total_fit = float(np.sum(fitness_list))
        if total_fit == 0: 
            total_fit=1
            relative_fitness = fitness_list +1.0/self.N
        else:
            relative_fitness = (fitness_list / total_fit)
            relative_fitness = relative_fitness / np.sum(relative_fitness)
        mating_population = np.random.choice(select_from,self.N, p=relative_fitness)
        for member in mating_population:
            intermediate_pop.append(list(sorted_pop[member]))

        intermediate_pop = [[i] + ip[1:] for i, ip in enumerate(intermediate_pop)]
        return intermediate_pop

    def crossover(self, parent1, parent2):
        if self.D <= 1: return parent1, parent2
        c_point = np.random.randint(1, self.D) # Crossover point
        child1 = parent2
        child2 = parent1
        for chromosome in range(1, c_point):
            child1[chromosome] = parent1[chromosome]
            child2[chromosome] = parent2[chromosome]
        for chromosome in range(self.D+1 - c_point):
            child1[-chromosome] = parent2[-chromosome]
            child2[-chromosome] = parent1[-chromosome] 
        return child1, child2

        
    def mutate(self, population):
        for member in range(len(population)):
            for attr, chromosome in zip(self.attributes.values(), range(1, self.D+2)):
                if np.random.rand()<self.p_m:
                    if not isinstance(population[member][chromosome], int) and population[member][chromosome].isdigit(): population[member][chromosome] = int(population[member][chromosome])

                    if population[member][chromosome] == self.types[attr][-1]: population[member][chromosome] = self.types[attr][-2]
                    elif population[member][chromosome] == self.types[attr][0]: population[member][chromosome] = self.types[attr][1]
                    else:
                        if np.random.rand() < 0.5: population[member][chromosome] = self.types[attr][self.types[attr].index(population[member][chromosome]) + 1]
                        else: population[member][chromosome] = self.types[attr][self.types[attr].index(population[member][chromosome]) - 1]
        return population

    
    def new_generation(self, intermediate_pop):
        new_pop = intermediate_pop
        parent_list = np.arange(self.N)
        pairings = np.random.choice(parent_list, (2,int(self.N/2)), replace =False)
        for x in range(np.int(self.N/2)):
            parent1 = pairings[0][x]
            parent2 = pairings[1][x]
            new_pop[pairings[0][x]], new_pop[pairings[1][x]] = self.crossover(intermediate_pop[parent1], intermediate_pop[parent2])
        self.mutate(new_pop)
        new_pop = [[i] + ip[1:] for i, ip in enumerate(new_pop)]
        return new_pop

    def fitness_func(self, goal, population, boundary, nextBoundary):
        #print(population)
        with open('inputFindMax.csv', 'wb') as csvFile:
            writer = csv.writer(csvFile, delimiter=',')
            attrName = [['id'] + self.attributes.keys()]
            writer.writerows(attrName + population)
        
        #exit()
        boundary = boundary.split('=')[0]
        nextBoundary = nextBoundary.split('=')[0]

        grades = PyMark.run('inputFindMax.csv', self.ruleInput)
        #print(grades)
        #print(boundary)
        fitnessGrade = {idKey : grade[boundary] if grade[boundary] >= 0 and grade[nextBoundary] < 0 else 0 for idKey, grade in grades.items()}
        #exit()
        fitness_list = np.array([fitnessGrade[str(i)] for i in range(0, self.N)])
        avg_fitness = np.sum(fitness_list)/self.N
        max_fitness = max(fitness_list)

        fitness_indices = (fitness_list).argsort()
        
        fitness_list = fitness_list[fitness_indices]
        sorted_pop = np.array(population)[fitness_indices]

        #print(sorted_pop)
        #time.sleep(30)
        return sorted_pop, fitness_list, avg_fitness, max_fitness


    def run(self):

        np.random.seed(0)
        outputValues = []
        for i, r in enumerate(self.results.values()[0][1:-1]):
            r = r.split('=')
            boundaryGoal = r[1]
            
            for n in range(1,self.Z+1):
                
                init_ids = range(0, self.N)
                init_attrValues = [[ident] for ident in init_ids]
                for attrName, attrType in self.attributes.items():
                    typeRange = self.types[attrType]
                    if isinstance(typeRange[0], int): 
                        genRan = np.random.randint(typeRange[0],typeRange[-1]+1, size = (self.N,1))
                        init_attrValues = [aV + list(attr) for aV, attr in zip(init_attrValues, genRan)]
                    else:
                        ranIdx = np.random.randint(0,len(typeRange), size = (self.N,1))
                        init_attrValues = [aV + [typeRange[attr]] for aV, attr in zip(init_attrValues, ranIdx)]

                init_pop = init_attrValues

                idx = 0
                goal = boundaryGoal

                generation_avg_fitness = []
                generation_min_fitness = []

                cur_gen = init_pop
                #for ip in cur_gen:
                    #print(str([n + '=' + str(a) for a, n in zip(ip[1:], self.attributes.keys() )]))
                #exit()
                bestGrade = 0
                bestGradeMarks = []
                for t in range(self.T):
                    #print("generation " + str(t))
                    #print(cur_gen)
                    sorted_pop, fitness_list, avg_fitness, min_fitness = self.fitness_func(goal, cur_gen, self.results.values()[0][i+1], self.results.values()[0][i+2])
                    generation_avg_fitness.append(avg_fitness)
                    generation_min_fitness.append(min_fitness)
                    if (bestGrade < fitness_list[-1] or bestGradeMarks == []):
                        bestGrade = fitness_list[-1]
                        bestGradeMarks = sorted_pop[-1]

                    intermediate_pop = self.roulette_wheel_selection(sorted_pop, fitness_list)

                    new_gen = self.new_generation(intermediate_pop)
                    cur_gen = new_gen
                
                #print(bestGrade)
                #print(self.attributes.keys())
                #print(bestGradeMarks[1:])
                passingVals = str([n + '=' + str(a) for a, n in zip(bestGradeMarks[1:], self.attributes.keys() )]) 
                outputValues.append(r[0] + ' maximum passing score: ' + str(bestGrade) + ', with attributes ' + str(passingVals) + '\n')

        outputValues.append('\n')
        with open('outputGeneticAlgorithm.csv', 'a') as f:
            f.writelines(outputValues)


#------------- Uncomment below to run --------------------------
