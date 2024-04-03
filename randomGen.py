import random
import findMaxGrade
import GeneticAlgorithm
import verticesSearch
import time

def genRule(rrI, lenRR, expands):
    global attribute_ids_temp
    lenAIT = len(attribute_ids_temp)
    if lenAIT == 0: return
    if random.uniform(0, 1) < 0.25 and expands >= 3:
        #print('and')
        return genRule(rrI, lenRR, expands-2) + ' and ' + genRule(rrI, lenRR, expands-2)
    elif random.uniform(0, 1) < 0.25 and expands >= 3:
        #print('or')
        return genRule(rrI, lenRR, expands-2) + ' or ' + genRule(rrI, lenRR, expands-2)
    elif random.uniform(0, 1) < 0.2 and lenAIT >= 3:
        #print('nof')
        n = random.randint(1, lenAIT-2)
        nOf = str(n) + ' of {'
        for i in range(1, random.randint(n, len(attribute_ids_temp)-2) +1):
            while(True):
                #print(17, len(attribute_ids_temp))
                if len(attribute_ids) == 1: attr = 'a1'
                else: attr = 'a' + str(random.randint(1, len(attribute_ids)))
                if attr in attribute_ids_temp:
                    attrValue = attribute_ids_temp[attr]
                    try:
                        attrValue = attrValue[random.randint(int(len(attrValue) * (float(rrI-1)/lenRR))+1, int( (len(attrValue)) * (float(rrI)/lenRR)))]
                    except:
                        attrValue = attrValue[1]
                    nOf += attr + '=' + str(attrValue) +','
                    attribute_ids_temp.pop(attr)
                    break
        return nOf[:-1] + '}'
    else:
        #print('normal')
        #print(22, len(attribute_ids))
        skip = False
        while(True):
            #print(len(attribute_ids_temp))
            weight = ""
            if random.uniform(0, 1) < 0.25:
                weight = str(random.randint(1, 5) * 100) + '% '
            if len(attribute_ids) == 1: 
                attr = 'a1'
                skip = True
            else: attr = 'a' + str(random.randint(1, len(attribute_ids)))
            if attr in attribute_ids_temp or skip:
                attrValue = attribute_ids_temp[attr]
                #print(rrI, lenRR)
                try:
                    attrValue = attrValue[random.randint(int(len(attrValue) * (float(rrI)/lenRR)), int((len(attrValue)-1) * (float(rrI+1)/lenRR)))]
                except:
                    attrValue = attrValue[1]
                attribute_ids_temp.pop(attr)
                return weight + attr + '=' + str(attrValue)


timesToRun = {'bf' : [], 'rr' : [], 'ga' : [], 'vs' : []}

n = 10    
for i in range(2):
    #print('loop')
    type_ids = {}
    attribute_ids = {}
    grade_ids = {}
    with open('randomGenMS.csv', 'wb') as f:

        f.write('[types]\n')
        for typeI in range(1, random.randint(2, 4)):
            #print(60)
            typ = 'type' + str(typeI) + ': '
            if random.uniform(0, 1) < 0.5:
                typ += '[0..' + str(random.randint(1, 20)) + ']\n'
            else:
                #if random.uniform(0, 1) < 0.2: 
                    #if random.uniform(0, 1) < 0.5: typ += '--/++ '
                    #else: typ += '-/+ '
                typ += '[x1'
                for j in range(2, random.randint(3, 6)):
                    typ += ',x' + str(j)
                typ += ']\n'
            type_ids['type' + str(typeI)] = typ.split(': ')[1]
            f.write(typ)
           
        typeResult = 'type_result: [0..100'
        resultsRange = list(random.sample(range(1, 100), random.randint(2, 5)))
        resultsRange.sort()
        for rrI, rr in enumerate(resultsRange):
            typeResult += '\n'
            rrI+=1
            typeResult += 'r' + str(rrI) + '=' + str(rr)
        typeResult += ']\n'
        f.write(typeResult)

        f.write('[attributes]\n')
        for attributesI in range(1, random.randint(len(type_ids)+2, 6)):
            #print(86)
            aI = random.randint(1, len(type_ids))
            attribute = 'a' + str(attributesI) + ': type' + str(aI) + '\n'
            tempType = type_ids['type' + str(aI)].split('[')[1]
            if tempType[0].isdigit():
                typeSplit = tempType[:-2].split('..')
                attribute_ids['a' + str(attributesI)] = range(int(typeSplit[0]), int(typeSplit[1])+1)
            else: attribute_ids['a' + str(attributesI)] = tempType[:-2].split(',')
            f.write(attribute)

        f.write('[rules]\n')
        for rrI, rr in enumerate(resultsRange):
            #print(97)
            rrI += 1
            rules = ''
            attribute_ids_temp = attribute_ids.copy()
            for n in range(1, random.randint(2, 4)):
                #print(104)
                rules += 'r' + str(rrI) + ': ' + genRule(rrI, len(resultsRange)+1, len(attribute_ids_temp)) + '\n'
                if len(attribute_ids_temp) == 0: 
                    #print('break')
                    break

            #print('add rule')
            f.write(rules)
        #print('end write')    
        f.write('[results]\n')
        f.write('final_mark : type_result\n')
        f.close()
        

    #print('bf: ----------------------')
    tt = time.time()
    findMaxGrade.bruteForce(ruleInput='randomGenMS.csv')
    timesToRun['bf'].append(time.time() - tt)
    #print('rr: ----------------------')
    tt = time.time()
    findMaxGrade.reducedRules(ruleInput='randomGenMS.csv')
    timesToRun['rr'].append(time.time() - tt)
    #print('ga: ----------------------')
    tt = time.time()
    ga = GeneticAlgorithm.GeneticAlgorithm(ruleInput='randomGenMS.csv')
    ga.run()
    timesToRun['ga'].append(time.time() - tt)
    #print('vs: ----------------------')
    tt = time.time()
    vS = verticesSearch.verticesSearch(ruleInput='randomGenMS.csv')
    vS.ProcessData()
    for bound in vS.results.values()[0][1:]:
        vS.genFeasibleArea(bound)  
    timesToRun['vs'].append(time.time() - tt)

    #print('loop')

timesToRun = {k : sum(v) / float(len(v)) for k, v in timesToRun.items()}
print(timesToRun)

