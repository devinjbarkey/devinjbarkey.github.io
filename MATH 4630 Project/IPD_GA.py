#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Devin Barkey
Math 4/6630 Project
4/21/20
IPD_GA.py
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from statistics import stdev, mean

"Lookup list containing all possible results of two previous games."
lookup = ["CCCC", "CCCD", "CCDC", "CDCC", "DCCC", "CCDD", "CDCD", "DCCD", 
          "CDDC", "DCDC", "DDCC", "CDDD", "DCDD", "DDCD", "DDDC",  "DDDD"]

"Python dictionary in which to look up payoff for player given current moves."
payoffs = {'CC': 3, 'CD': 0, 'DC': 5, 'DD': 1}

##############################################################################
#Classes
##############################################################################

"""
Defines class Generation, which has attributes size and population, the latter 
of which contains Strategy objects.
"""
class Generation:
    
    "Initializes Generation object with empty population list."
    def __init__(self, n):
        self.population = []
        self.size = n
    
    "Adds Strategy object to Generation's population list."
    def add(self, strat):
        self.population.append(strat)
    
    "Returns list of chromosomes in population as strings."
    def get_pop(self):
        return [str(strat) for strat in self.population]
        
        
"""
Defines class Strategy which has attribute chrom, the
20-character long string of C's and D's that defines a given strategy.
"""
class Strategy:
    
    "Initializes Strategy object with input chromosome string."
    def __init__(self, chromosome):
        self.chrom = chromosome
    
    "Returns move defined by chromosome given the results from past two games."    
    def move(self, mem):
        ind = lookup.index(mem)
        return self.chrom[ind]
    
    """
    Returns last four alleles in chromosome defining two hypothetical games 
    used to begin round of IPD.
    """
    def get_init_mem(self):
        return self.chrom[16:20]
    
    "Returns chromosome of Strategy object."
    def __str__(self):
        return self.chrom
    
    """
    Performs mutation on chromosome of Strategy object by flipping an allele 
    with probability pm.
    """
    def mutate(self, pm):
        for i, allele in enumerate(self.chrom):
            if random.random() <= pm:
                if allele == 'C':
                    self.chrom = self.chrom[0:i] + 'D' + self.chrom[i+1:20]
                elif allele == 'D':
                    self.chrom = self.chrom[0:i] + 'C' + self.chrom[i+1:20]

##############################################################################
#Functions
##############################################################################

"Creates initial generation of Strategies from randomly generated chromosomes."    
def gen_0(n):
    generation_0 = Generation(n)
    i = 0
    while i < n:
        rchrom = ""
    
        for j in range(20):
            rchrom += random.choice(["C","D"])
            
        generation_0.add(Strategy(rchrom))
        i += 1
    return generation_0

"""
Creates next generation by first computing fitness scores for each strategy.
Then assigns weight of 2 to strategies which perform one standard deviation
above the mean, 1 to strategies within one standard deviation from the mean, 
and 0 to strategies below one standard devistion from the mean. Uses these
weights to randomly select parents of offspring. Returns next generation and 
mean score of previous generation.
"""
def evolve(cgen, iters, pc, pm):
    nextgen = Generation(cgen.size)
    scores = fitness(cgen, iters)
    mn = mean(scores)
    std = stdev(scores)
    matings = [1 for i in range(cgen.size)]
    for i, score in enumerate(scores):
        if score >= (mn + std):
            matings[i] = 2
        elif score <= (mn - std):
            matings[i] = 0
    j = 0
    while j < cgen.size/2:
        parents = random.choices(cgen.population, weights = matings, k = 2)
        mate(nextgen, parents[0], parents[1], pc, pm)
        j += 1

    return nextgen, mn

"""
Calculates fitness scores for each strategy by computing average payoff totals 
for IPD games against all other strategies in same generation, including itself.
"""
def fitness(cgen, iters):
    scores = []
    
    for player in cgen.population:
        tot_score = 0
        for adversary in cgen.population:
            tot_score += ipd(player, adversary, iters)
        avg_score = tot_score/cgen.size
        scores.append(avg_score)
    
    return scores

"""
Plays IPD for iters iterations, continuously updating the memory for each player 
p_1 and p_2.
"""
def ipd(p_1, p_2, iters):
    score = 0
    mem_1 = p_1.get_init_mem()
    mem_2 = p_2.get_init_mem()
    
    i=0
    while i < iters:
        move = p_1.move(mem_1) + p_2.move(mem_2)
        score += payoffs[move]
        mem_1 = mem_1[2:4] + move
        mem_2 = mem_2[2:4] + move[::-1]
        i += 1
        
    return score

"""
Produces two offspring from parents par_1 and par_2 with probability of 
crossover pc and probability of mutation pm. If no crossover occurs, offspring 
are copies of parents. Offspring then added to next generation.
"""
def mate(nextgen, par_1, par_2, pc, pm):
    if random.random() <= pc:
        off_1, off_2 = crossover(par_1, par_2)
    else:
        off_1, off_2 = par_1, par_2
    off_1.mutate(pm)
    off_2.mutate(pm)
    nextgen.add(off_1)
    nextgen.add(off_2)

"""
Performs crossover of two strategy chromosomes x and y by randomly selecting 
crossover point and constructing offspring by splicing complementary pieces of 
each chromosome together.
"""
def crossover(x, y):
    cp = random.randrange(1,19)
    child_1 = Strategy(str(x)[0:cp] + str(y)[cp:20])
    child_2 = Strategy(str(y)[0:cp] + str(x)[cp:20])
    return child_1, child_2

##############################################################################
#Main
##############################################################################

"""
Main function which prompts user for population size, number of generations, 
and number of runs to be performed.
"""
def main():
    n = int(input('Enter the population size n: '))
    g = int(input('Enter the number of generations: '))
    runs = int(input('Enter the number of runs: '))
    
    iters = 150
    pc = 0.1
    pm = 0.001
    
    #Optional promts to input desired iters, pc, and pm
    #iters = int(input('Enter number of iterations for PD: '))
    #pc = float(input('Enter the crossover probability Pc: '))
    #pm = float(input('Enter the mutation probability Pm: '))

    "Numpy array to store average scores of each generation in every run."
    record = np.zeros([g, runs])

    j = 0
    while j < runs:
        gen = gen_0(n)
   
        i = 1
        while i < g:
            gen, pgen_mean = evolve(gen, iters, pc, pm)
            record[i-1,j] = pgen_mean
            i += 1
        print(gen.get_pop())
        record[i-1,j] = mean(fitness(gen, iters))
        j +=1

    "Plot average score for every generation."
    x = np.arange(0,g)
    y = np.mean(record, axis = 1)
    
    plt.plot(x,y)
    plt.xlabel('Generation')
    plt.ylabel('Mean Score')
    title = 'n = ' + str(n) + ', g = ' + str(g) + ', runs = ' + str(runs)
    plt.title(title)


if __name__ == "__main__":
    main()
