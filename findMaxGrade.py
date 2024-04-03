import PyMark
import numpy as np
import itertools
import csv
import sys
import time

def bruteForce(ruleInput='rules.csv', printOld=False):
    #print('brute')
    
    types, attributes, _, results = PyMark.readRules(ruleInput)

    attributes = {at : types[v] for at, v in attributes.items()}
    for k, v in attributes.items():
        if '..' in v: attributes[k] = range(int(v.split('..')[0]), int(v.split('..')[1])+1)
    
    #print('create combo')
    L = [a for a in attributes.values()]
    combinations = list(itertools.product(*L))
    combinations = [[i] + list(a) for i,a in enumerate(combinations)]
    combinations = [['id'] + attributes.keys()] + combinations
    #print('finsih combo')

    with open('inputFindMax.csv', 'wb') as csvFile:
        writer = csv.writer(csvFile, delimiter=',')
        writer.writerows(combinations)

    #print('before grade')
    grades = PyMark.run('inputFindMax.csv', ruleInput)
    outputValues = []
    gBs = results.values()[0][1:]
    gBs.insert(0,gBs[0])
    for i, b in enumerate([r.split('=')[0] for r in gBs]):
        if (i == len(gBs)-1): 
            continue #The problem doesn't occur when there is no grade above it
            outputValues.append('The grade ' + b + ', maximum passing score is: ' + str(max([scores[b] for scores in grades.values()])))
        elif i == 0:
            continue #There is no passing score when first grade fails
            outputValues.append('The grade below ' + b + ', minimum failing score is: ' + str(min([scores[b] for scores in grades.values()])))
        else: 
            try:
                failingScore = str(min([scores[gBs[i+1].split('=')[0]] for scores in grades.values() if scores[gBs[i].split('=')[0]] >= 0 and scores[gBs[i+1].split('=')[0]] < 0])) 
            except:
                failingScore = '0'
            try:
                passingScoreGrades = {val: float(scores[b]) for val, scores in grades.items() if scores[gBs[i].split('=')[0]] >= 0 and scores[gBs[i+1].split('=')[0]] < 0}
                passingScoreVal = max(passingScoreGrades.iterkeys(), key=(lambda key: passingScoreGrades[key]))
                #
                # print(passingScoreVal)
                passingScore = str(passingScoreGrades[passingScoreVal])

                #print(passingScore)
                passingVals = combinations[int(passingScoreVal)+1]
                #print(passingVals[1:])
                passingVals = str([n + '=' + str(a) for a, n in zip(passingVals[1:], attributes.keys() )]) 
            except Exception as e:
                #print(e)

                #rint(grades)
                passingScore = 'No passing score available'
                passingVals = 'N/A'
            
                #print('N/A')


            outputValues.append(b + ' maximum passing score: ' + passingScore + ', with attributes ' + str(passingVals) + '  \\\\')

        outputValues[-1] += '\n'
    outputValues.append('\n')
    with open('outputBruteForce.csv', 'a') as f:
        f.writelines(outputValues)
    #print('done')
    #exit()

def getRidWeight(r):
    rList = []
    for splitedR in r:
        if splitedR != r[-1]: 
            while(splitedR != "" and splitedR[-1].isdigit()): splitedR = splitedR[:-1]
        if splitedR != "": rList.append(splitedR)

    rListTemp = []
    for rl in rList:
        rl = rl.split('or')
        for temp in rl: 
            if temp!="":rListTemp.append(temp)
    return rListTemp

def reducedRules(ruleInput='rules.csv'):
    types, attributes, rules, results = PyMark.readRules(ruleInput)

    attributes = {at : types[v] for at, v in attributes.items()}
    for k, v in attributes.items():
        if '..' in v: attributes[k] = range(int(v.split('..')[0]), int(v.split('..')[1])+1)

    passMarksReq = {}
    maxValues = {k : t[-1] for k, t in attributes.items()}
    outputValues = []
    for b in results.values()[0][2:]:
        #print(b)
        splitB = b.split('=')
        reqs = rules[splitB[0]]
        simpleReqs = []
        #print('reqs', reqs)
        for r2 in [r.split('and') for r in reqs]:
            temp = []
            #print(51, r2)
            #for r3 in [r3.split('or') for r3 in r2]:
                #temp.append([r4.split('%')[1] if '%' in r4 else r4 for r4 in r3])
            temp.append([getRidWeight(r3.split('%')) if '%' in r3 else r3 for r3 in r2])
            #print(55, temp)
            simpleReqs.append(temp)
        #rint('simpleReqs', simpleReqs)
        simpleReqs = [item for sublist in simpleReqs for item in sublist]
        #simpleReqs = [item for sublist in simpleReqs for item in sublist]
        #print('simpleReqs', simpleReqs)
        newSimpleReqs = []
        for sr in simpleReqs:
            temp = []
            for s in sr:
                if isinstance(s, list) : temp = temp + s
                else: temp += [s]
            newSimpleReqs.append(temp)
        simpleReqs = newSimpleReqs
        #rint('simpleReqs', simpleReqs)
        #exit()
        #Find highest occurance of each type
        temp = {}
        #print('simpleReqs', simpleReqs)
        simpleReqs = [[sr.translate(None, "()\{\}") for sr in srList] for srList in simpleReqs]
        simpleReqs = [[sr[sr.index('of')+2:] if 'of' in sr else sr for sr in srList] for srList in simpleReqs]
        #print('simpleReqs', simpleReqs)
        simpleReqs = [[sr if ',' not in sr else sr.split(',') for sr in srList] for srList in simpleReqs]
        #print(simpleReqs)
        tmpSR = []
        for sr in simpleReqs:
            tempSRList = []
            for srList in sr:
                if isinstance(srList, list): 
                    for s in srList: tempSRList.append(s)
                else: tempSRList.append(srList)
            tmpSR.append(tempSRList)
        simpleReqs = tmpSR

        for simReq in simpleReqs:
            for srList in simReq:
                tempSR = {}
                for sr in srList.split('or'):
                    splitSr = sr.split('=')
                    name = splitSr[0]
                    if name not in tempSR.keys(): tempSR[name] = splitSr[1]
                    else:
                        if splitSr[1].isdigit():
                            if attributes[name].index(int(splitSr[1])) < attributes[name].index(int(tempSR[name])): tempSR[name] = splitSr[1]
                        elif attributes[name].index(splitSr[1]) < attributes[name].index(tempSR[name]): tempSR[name] = splitSr[1]
                temp[srList] = tempSR
        simpleReqs = temp
        passMarksReq[splitB[0]] = simpleReqs
 
        #print('simpleReqs', simpleReqs)
        ranges = {}
        attributesSeen = []
        #print(attributes)
        for name, v in simpleReqs.items():
            if isinstance(v, dict):
                rangesForDict = {}
                for name2, v2 in v.items():
                    attributesSeen.append(name2)
                    if v2.isdigit(): i = attributes[name2].index(int(v2))-1
                    else: i = attributes[name2].index(v2)-1
                    if i < 0: i = 0
                    #print(i)
                    rangesForDict[name2] = [attributes[name2][i], attributes[name2][-1]]
                ranges[name] = rangesForDict
            else:
                attributesSeen.append(name)
                if v.isdigit(): i = attributes[name].index(int(v))-1
                else: i = attributes[name].index(v)-1
                if i < 0: i = 0
                #rint(i)
                ranges[name] = [attributes[name][i], attributes[name][-1]]
        
        #Fills in missing values 

        for k, v in attributes.items():
            if k not in attributesSeen: ranges[k] = v[-1]

        temp = {}
        for r in ranges:
            if isinstance(ranges[r], dict):
                r = ranges[r]
                for k, v in r.items(): 
                    if k in temp: temp[k].append(v)
                    else: temp[k] = [v]
            else: 
                temp[r] = [[ranges[r], ranges[r]]]

        ranges = temp
        #Generate combinations 
        for r, v in ranges.items():
            if len(v) > 1:
                v = [ attributes[r].index(val[0]) for val in v ]
                minV = attributes[r][min(v)]
                ranges[r] = [[minV, attributes[r][-1]]]
 
        L = [a[0] for a in ranges.values()]
        combinations = list(itertools.product(*L))
        
        combinations = list(set(combinations))
        combinations = [[i] + list(a) for i,a in enumerate(combinations)]
        combinations = [['id'] + attributes.keys()] + combinations

        with open('inputFindMax.csv', 'wb') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(combinations)

        grades = PyMark.run('inputFindMax.csv', ruleInput)
        #print(grades)

        gradeBelow = results.values()[0][ results.values()[0].index(b)-1].split('=')[0]

        try:
            passingScoreGrades = {val: float(scores[gradeBelow]) for val, scores in grades.items() if scores[gradeBelow] >= 0 and scores[splitB[0]] < 0}
            passingScoreVal = max(passingScoreGrades.iterkeys(), key=(lambda key: passingScoreGrades[key]))
            passingScore = str(passingScoreGrades[passingScoreVal])

            #print(passingScore)
            passingVals = combinations[int(passingScoreVal)+1]
            #print(passingVals[1:])
            passingVals = str([n + '=' + str(a) for a, n in zip(passingVals[1:], attributes.keys() )]) 
      

        except Exception as e:
            #print(e)
            passingScore = 'No passing score available'
            passingVals = 'N/A'
            #print(passingScore)

        outputValues.append(results.values()[0][results.values()[0].index(b)- 1].split('=')[0] + ' maximum passing score:  ' + passingScore + ' with attributes ' + str(passingVals) + '\n')
    outputValues.append('\n')
    with open('outputReducedRules.csv', 'a') as f:
        f.writelines(outputValues)

