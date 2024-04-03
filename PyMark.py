import csv
import numpy as np
import math
import time

#Reads input file
def readInput(fileDir):
    f = open(fileDir)
    marks = {}
    columns = {}
    first = True
    for line in f:
        if (first): 
            columns = line.rstrip().split(',')
            first = False
        else:
            data_line = line.rstrip().split(',')
            gradesInSection = {}
            for question, val in zip(columns[1:], data_line[1:]):
                gradesInSection[question] = val
            marks[data_line[0]] = gradesInSection
    f.close()
    return marks

#Reads and parses marking scheme
def readRules(fileDir):

    f = open(fileDir)

    separators = ['[types]', '[attributes]', '[rules]', '[results]']
    blocks = {}
    tempBlock = []
    continuedLine = []
    for line in f:
        line = line.replace("\t", "")
        line = line.replace(" ", "")
        if line != '\n':
            if line[:-1] in separators:
                if (len(tempBlock) != 0):
                    blocks[tempBlock[0][1:-1]] = tempBlock[1:]
                    tempBlock = []
            if continuedLine:
                if ']' not in line: continuedLine.append(line[:-1])
                else:
                    continuedLine.append(line[:-1])
                    tempBlock.append(continuedLine)
                    continuedLine = []
            else: 
                if '[' in line and ']' not in line:
                    continuedLine = [line[:-1]]
                else:
                    if '\n' in line: tempBlock.append(line[:-1])
                    else: tempBlock.append(line)
    f.close()

    blocks[tempBlock[0][1:-1]] = tempBlock[1:]
    blocks['types'] = getTypes(blocks['types'])
    return blocks['types'], updateAttributes(blocks['attributes']), updateRules(blocks['rules']), updateResults(blocks['results'], blocks['types'])

def getTypes(types):
    adaptedTypes = {}
    for ty in types:
        if not isinstance(ty, list): tySplit = ty[:-1].split(':')
        else: tySplit = ty[0].split(':')
        
        if '\n' in tySplit:
            ##print('newline')
            pass
        else:
            if '/' in tySplit[1]:
                typeValue = tySplit[1].split('[')
                tySplit[1] = typeValue[1]
                if tySplit[1][0].isdigit() and '..' in tySplit[1]:
   
                    adaptedTypes[tySplit[0]] = [typeValue[0]] + [tySplit[1]]
                else:
                    adaptedTypes[tySplit[0]] = [typeValue[0]]  + tySplit[1].split(',')
            else:
                if tySplit[1][1].isdigit() and '..' in tySplit[1]:
               
                    if not isinstance(ty, list): adaptedTypes[tySplit[0]] = tySplit[1][1:]
                    else: adaptedTypes[tySplit[0]] = [tySplit[1][1:]] + ty[1:-1] + [ty[-1][:-1]]
                else:
                    adaptedTypes[tySplit[0]] = tySplit[1][1:].split(',')
  
    return adaptedTypes

def updateRules(rules):         
    updatedRules = {}
    for r in rules:
        splittedR = r.split(':')
        if splittedR[0] in updatedRules: updatedRules[splittedR[0]] = updatedRules[splittedR[0]] + [splittedR[1]]
        else: updatedRules[splittedR[0]] = [splittedR[1]]
    return updatedRules

def updateAttributes(attributes):
    updatedAttrs = {}
    for attr in attributes:
        splittedAttr = attr.split(':')
        updatedAttrs[splittedAttr[0]] = splittedAttr[1]
    return updatedAttrs

def updateResults(results, types):
    return {r[0]: types[r[1]] for r in [result.split(':') for result in results]}

def calculateMark():
    #Check result if grades or percentage
    studentResults = {m: [] for m in studentsMarks.keys()}
  
    for res, typ in results.items():
        if isinstance(typ, list):
            for name in studentResults.keys():
                studentResults[name] = checkPercentage(name, res, typ)
                #print(109, 'delete to fix')
                #break #delete
        else:
            for name in studentResults.keys():
                studentResults[name] = checkGrade(studentsMarks[name], res, typ)
   

    return studentResults

def checkGrade(name, result, resultType):
    grade = resultType[0]
    for rt in resultType[1:]:
        obtained = True
        for rule in rules[rt]:
            if 'and' in rule: rule = rule.split('and')
            else: rule = [rule]
            for andRule in rule:
                if 'or' in andRule: andRule = andRule.split('or')
                else: andRule = [andRule]
                satisfied = False
                for orRule in andRule:
                    if '=' in orRule:
                        orRule = orRule.split('=')
                        if orRule[1].isdigit():
                            if marks[orRule[0]] >= orRule[1]: 
                                satisfied = True
                                break
                        else:
                            if marks[orRule[0]] == orRule[1]:
                                satisfied = True
                                break
                    else:
                        if orRule == grade: satisfied = True
                if not satisfied: obtained = False
        if obtained: grade = rt
    return grade

def checkPercentage(name, result, resultType):
    #print('start', name, result, resultType)
    avs = normalise(studentsMarks[name])
    #print(studentsMarks[name])
    boundaries = [[r.split('=')[0], r.split('=')[1]] for r in resultType[1:]]
    boundariesV = {}
    #print(name)
    global rules
    for ruleI in range(len(resultType[1:])):
        ruleReqs = rules[boundaries[ruleI][0]]
        ruleV = []
        ruleVWeighting = []
        #print('aaaaa', ruleReqs)
        for ruleReq in ruleReqs:
            #print('ruleRebjkbq', ruleReq)
            if '%' in ruleReq and 'or' not in ruleReq and 'and' not in ruleReq: 
                #print(1288888)
                temp = ruleReq.split('%')
                ruleVWeighting.append(int(temp[0]) / 100.0)
                ruleReq = temp[1]
            elif '%' in ruleReq and '(' in ruleReq:
                temp = ruleReq.split('%')
                ruleVWeighting.append(int(temp[0]) / 100.0)
                ruleReq = temp[1][1:-1]
            else: ruleVWeighting.append(1.0)
            #print(132, ruleVWeighting)
            #print(ruleReq)
            #if '{' in ruleReq:
                #print('of') 
                #print(ruleReq)
                #ruleReq = ruleReq.split(',')
                #tempN = ruleReq[0].index('{')+1
                #print(ruleReq)
                #print(tempN)
                
                #r#uleReq = [ruleReq[0][:tempN], ruleReq[0][tempN:]] + ruleReq[1:-1] + [ruleReq[-1][:-1], '}']
                #print(ruleReq)
                #exit()
            ruleReq = seprateBrackets(ruleReq)
            #print('rulesReq', ruleReq)
            ruleV, ruleHasPassed = checkVs(ruleReq, avs, ruleV, boundariesV)
        #print(125,'rule V', ruleV)
        #print(ruleVWeighting)
        #print(ruleHasPassed)
        ruleV = collapseRulesV(ruleV, ruleVWeighting, True)
        #ruleV = compoundRule(ruleV, len(ruleReqs), ruleHasPassed)
        boundariesV[boundaries[ruleI][0]] = ruleV
        #if not ruleHasPassed: break
    #print(name, 'boundaries', boundariesV, ruleHasPassed)
    
    return boundariesV
    
    
    #print('boundaries', boundariesV)
    #print(boundaries)
    if (any([x < 0 for x in boundariesV.values()])):
        i = 0
        tempBound = boundariesV.copy()
        for b in boundaries:
            vB = boundariesV[b[0]]
            #print('b', b, boundaries)
            tempBound.pop(b[0])
            if vB < 0 and not any([x >= 0 for x in tempBound.values()]):
                if b[0] == boundaries[0][0]: return int((((boundariesV[boundaries[0][0]] + 1) * (int(b[1])))))
                else: 
                    f = (boundariesV[b[0]] + boundariesV[boundaries[i-1][0]] + 1) / 2.0
                    #print('d', f)
                    
                    return int(round(((f * ((int(b[1])-1) - int(boundaries[i-1][1]))) + int(boundaries[i-1][1]))))
            i+=1

    else: 
        ip = int(boundariesV[boundaries[-1][0]] * (int(resultType[0].split('..')[1]) + 1 - int(boundaries[-1][1])) + int(boundaries[-1][1]))
        e = (10)**-8 
        if ip < (int(resultType[0].split('..')[1]) - e): return ip
        else: return int(ip-e)

                
def checkVs (ruleReq, avs, ruleV, boundariesV):
    #print('checkVS')
    ruleHasPassed = True
    #print('\n')
    #print('212', ruleReq)
    compoundRuleN = []
    weightingStated = False
    rulesWeighting = []
    for req in ruleReq:
        #print(154, ruleV)
        #print(218, req)

        #Actually fix this

        if isinstance(req, list): 
            #print(155, req)
            ruleV, rhp = checkVs(req, avs, ruleV, boundariesV)
            #print('\n')
            #print(req, avs, ruleV, boundariesV)
            ruleHasPassed = ruleHasPassed and rhp
        else: 
            #print(242, req)
            if req == 'and' or req == 'or': 
                #print('166')
                ruleV = addLast(ruleV, req)
                continue
            if 'and' in req: req = req.split('and')
            else: req = [req]
            andReqVs = []
            hasAndPassed = []
            andWeights = []
            #print(269, req)
      
            for andReq in req:
                if '%' in andReq[0]: 
                    temp = andReq[0].split('%')
                    andWeights.append(int(temp[0]) / 100.0)
                    andReq[0] = temp[1]
                else: andWeights.append(1.0)
                if 'or' in andReq: andReq = andReq.split('or')
                else: andReq = [andReq]
                orsPass = False
                orReqVs = []
                orWeights = []
                for orReq in andReq:
                    #print(17523232, orReq)
                    
                    if 'of{' in orReq:
                        #print(170, compoundRuleN)
                        idxSplit = orReq.index('{')
                        
                        #print('of{', orReq)
                        nOfVal = findCompoundRuleN(orReq)
                        orReq = [orReq[ : idxSplit + 1 ], orReq[idxSplit + 1 :]]
                        #print(orReq)
                        orReqVals = [checkVs([v], avs, [], []) for v in orReq[1][:-1].split(',')]
            
                        nOfPassing = [1 if orVal[1] == True else 0 for orVal in orReqVals ]
                        orReqVals = [orVal[0][0][0] for orVal in orReqVals]
                        #print(nOfPassing, orReqVals)
                        v = compoundRule(orReqVals, nOfVal, nOfVal <= sum(nOfPassing), [1]*(len(orReqVals)))
                        #print('v', v)
    


                    elif '=' in orReq:
                        orReq = orReq.split('=')
                        if '%' in orReq[0]: 
                            temp = orReq[0].split('%')
                            orWeights.append(int(temp[0]) / 100.0)
                            orReq[0] = temp[1]
                        else: orWeights.append(1.0)
                        #print('hi', avs)
                        av = avs[orReq[0]]
                        #print(282, av)
                        rv = normalise({orReq[0] : orReq[1]})[orReq[0]]
                        if orReq[1].isdigit():
                            #print(types)
                            #print('dsjckl', types[attributes[orReq[0]]])
                            if '/' in types[attributes[orReq[0]]][0]: rv = normalise({orReq[0] : ( orReq[1] + types[attributes[orReq[0]]][0].split('/')[1] ) })[orReq[0]]
                            if av >= rv: #Passing rule
                                try:
                                    if rv == 1: v=1
                                    else: v = (av - rv) / (1.0 - rv)
                                    orsPass = True
                                except:
                                    print(ruleReq)
                                    print(andReq)
                                    print(av, rv, 'passing')
                                    exit()
                                #print(v)
                            else: #Failling rule
                                #print(av, rv, 'failing')
                                if rv==0: v = -1
                                else: v = (av/rv) - 1
                                #print(v)
                        else:
                            #print('290', avs[orReq[0]], types, attributes)
                            if '+' in types[attributes[orReq[0]]][0] or '-' in types[attributes[orReq[0]]][0]:
                                nValue = len(types[attributes[orReq[0]]][0])
                                #*(types[attributes[orReq[0]]].index(orReq[1])-1)
                                #print(avs)
                                temp = avs[orReq[0]]
                                #print(temp)
                                temp = temp.replace('+','')
                                temp = temp.replace('-','')
                                
                                upperIdx = types[attributes[orReq[0]]].index(orReq[1])
                                typeForAttr = types[attributes[orReq[0]]]
                                #print('typeForAttr', typeForAttr, temp)
                                if typeForAttr.index(temp) >= typeForAttr.index(orReq[1]):
                                    orsPass = True
                                    #v=0
                                    lowIdx = upperIdx
                                    upperIdx = len(typeForAttr) + 1 #change this so it calculates correctly
                                    #print(lowIdx, upperIdx)
                                    #print('if', (1.0/len(typeForAttr[lowIdx:upperIdx])), typeForAttr[lowIdx:upperIdx].index(temp))

                                    if typeForAttr[lowIdx+1:] == []: v = 1.0
                                    else: v = (1.0/len(typeForAttr[lowIdx+1:])) * (typeForAttr[lowIdx:].index(temp)) #THIS MIGHT NOT WORK

                                    #print(len(typeForAttr[lowIdx:upperIdx])), (typeForAttr[lowIdx:upperIdx+1].index(temp))
                                    #print(328, v)
                                    nValue = 1.0/(len(typeForAttr[lowIdx:upperIdx]) * nValue)
                                    if len(types[attributes[orReq[0]]][0]) == 5:
                                        #print('hi', nValue)
                                        #print(v)
                                        if avs[orReq[0]][-2:] == '--': v += nValue
                                        elif avs[orReq[0]][-1] == '-': v += 2*nValue
                                        elif avs[orReq[0]][-1] != '-' or avs[orReq[0]][-1] != '+': v += 3*nValue
                                        elif avs[orReq[0]][-1] == '+': v += 4*nValue
                                        elif avs[orReq[0]][-2:] == '++': v += 5*nValue
                                        else: print('k', avs[orReq[0]][-2:])
                                    else: 
                                        if avs[orReq[0]][-1] == '-': pass#v += nValue
                                        elif avs[orReq[0]][-1] != '+': v += nValue
                                        elif avs[orReq[0]][-1] == '+': v += 2*nValue
                                else: 
                                    lowIdx = 0
                                    #print(lowIdx, upperIdx)
                                    for bound in boundariesV.keys():
                                        #print(304, bound)
                                        pass
                                    v = (1.0/len(typeForAttr[lowIdx:upperIdx])) * (typeForAttr[lowIdx:upperIdx+1].index(temp)) - 1
                                    #print(len(typeForAttr[lowIdx:upperIdx])), (typeForAttr[lowIdx:upperIdx+1].index(temp))
                                    nValue = 1.0/(len(typeForAttr[lowIdx:upperIdx]) * nValue)
                                    if len(types[attributes[orReq[0]]][0]) == 5:
                                        #print('hi', nValue)
                                        #print(v)
                                        if avs[orReq[0]][-2:] == '--': pass
                                        elif avs[orReq[0]][-1] == '-': v += nValue
                                        elif avs[orReq[0]][-1] != '-' or avs[orReq[0]][-1] != '+': v += 2*nValue
                                        elif avs[orReq[0]][-1] == '+': v += 3*nValue
                                        elif avs[orReq[0]][-2:] == '++': v += 4*nValue
                                        else: print('k', avs[orReq[0]][-2:])
                                    else: 
                                        if avs[orReq[0]][-1] == '-': pass
                                        elif avs[orReq[0]][-1] != '+': v += nValue
                                        elif avs[orReq[0]][-1] == '+': v += 2*nValue
                                #print(nValue)
                                

                                #print('VVVV', v, orReq, avs)
                                
                            elif types[attributes[orReq[0]]].index(avs[orReq[0]]) >= types[attributes[orReq[0]]].index(orReq[1]):
                                temp = avs[orReq[0]]
                                upperIdx = types[attributes[orReq[0]]].index(orReq[1])
                                typeForAttr = types[attributes[orReq[0]]]
                                #print('typeForAttr', typeForAttr, temp)
                                lowIdx = upperIdx
                                upperIdx = len(typeForAttr) + 1 #change this so it calculates correctly
                                
                                if typeForAttr[lowIdx+1:] == []: v = 1.0
                                else: v = (1.0/len(typeForAttr[lowIdx+1:])) * (typeForAttr[lowIdx:].index(temp))
                                orsPass = True
                
                            else: 
                                temp = avs[orReq[0]]
                                
                                upperIdx = types[attributes[orReq[0]]].index(orReq[1])
                                typeForAttr = types[attributes[orReq[0]]]
                                lowIdx = 0
                                v = (1.0/len(typeForAttr[:upperIdx])) * (typeForAttr[lowIdx:upperIdx].index(temp)) - 1

                    else:
                        v = boundariesV[orReq]
                        if v >= 0: orsPass = True
                        #print(230, v)
                    orReqVs.append(v)
                
                #print('or Vs', orReqVs, orWeights)
                if len(orReqVs) > 1:
                    orReqVs = compoundRule(orReqVs, 1, orsPass, orWeights)
                else: orReqVs = orReqVs[0]
                andReqVs.append(orReqVs)
                hasAndPassed.append(orsPass)
            #print('and Vs', andReqVs, andWeights)
            ####print(224, andReqVs)
            if len(andReqVs) > 1: andReqVs = compoundRule(andReqVs, len(andReqVs), all(hasAndPassed), andWeights)
            else: andReqVs = andReqVs[0]
            #print(378, compoundRuleN)
            if compoundRuleN: compoundRuleN.append(andReqVs)
            else:
                #print(381)
                if ruleV: ruleV = addLast(ruleV, [andReqVs])
                else: ruleV.append([andReqVs])
                if not all(hasAndPassed): ruleHasPassed = False
            #print('and Vs2', andReqVs)
        #print(384, compoundRuleN)
        if compoundRuleN: pass
    #print(242, ruleV)
    return ruleV, ruleHasPassed
ruleHasPassed = True


def findCompoundRuleN(reqs):
    #print('findcompoundRuleN', reqs)
    prefix = reqs[0].split('{')[0].split('or')[-1].split('and')[-1].split('%')[-1]
    #print('prefix', prefix)
    if prefix == 'oneof': return 1
    elif prefix == 'allof': return len(reqs) - 2
    elif prefix == 'someof': return 1
    elif prefix == 'mostof': return math.floor( (len(reqs)-2) / 2) + 1
    elif prefix == 'allbutoneof': return len(reqs) - 3
    elif prefix[:7] == 'allbut' and prefix[-2:] == 'of': return int (reqs.count(',')) + 1 - int(prefix[7:-2])
    else: return int(prefix)


def collapseRulesV(rulesV, ruleVWeighting, original):
    #print('collapse rule', rulesV, original)
    if isinstance(rulesV, list):
        ###print('list')
        if len(rulesV) == 1: return collapseRulesV(rulesV[0], ruleVWeighting, True)
        elif 'and' in rulesV: 
            onlyNums = [collapseRulesV(r, ruleVWeighting, False) if isinstance(r, list) else r for r in rulesV[0::2]]
            ###print(onlyNums)
            return compoundRule(onlyNums, len(onlyNums), all([x >= 0 for x in onlyNums]), [1]*len(onlyNums))
        elif 'or' in rulesV:
            onlyNums = [collapseRulesV(r, ruleVWeighting, False) if isinstance(r, list) else r for r in rulesV[1::2]]
            return compoundRule(onlyNums, 1, any([x >= 0 for x in onlyNums]), [1])
        elif original: 
            rulesV = [collapseRulesV(r, ruleVWeighting, False) if isinstance(r, list) else r for r in rulesV]
            #print('collapse rule after original', rulesV)
            return compoundRule(rulesV, len(rulesV), all([x >= 0 for x in rulesV]), [1] * len(rulesV))
        else: 
            rulesV = [collapseRulesV(r, ruleVWeighting, False) if isinstance(r, list) else r for r in rulesV]
            #print(424, rulesV)
            return compoundRule(rulesV, len(rulesV), all([x >= 0 for x in rulesV]), [1]*len(rulesV))
    else: 
        return rulesV

#adds v value to last list in rulesV 
def addLast(ruleVLast, andReqVs):
    if isinstance(ruleVLast[-1], list):
        ruleVLast[:-1].append(addLast(ruleVLast[-1], andReqVs))
        return ruleVLast
    else:
        ###print(ruleVLast)
        ruleVLast.append(andReqVs)
        return ruleVLast

def compoundRule(vValue, n, passing, weights):
    #print('compound rule', vValue, n, passing, weights)
    m = len(vValue)
    s = float(sum(weights))
    #print(s,'s', weights)
    weights = [w/s for w in weights]
    #print(weights)
    ws = sum([w * v for v, w in zip(vValue, weights)])
    sortedWeightIndex = np.array((np.argsort(weights)))
    vValue = np.array(vValue)[sortedWeightIndex]
    #print(sortedWeightIndex, weights)
    weights = np.array(weights)[sortedWeightIndex]
    #print(vValue, weights)
    #print(ws)
    if passing:
        wsMin = sum([-1 * w for v, w in zip(vValue[n:m], weights[n:m])]) #was n
        wsMax = sum([1 * w for v, w in zip(vValue, weights)])
        #print('passing', wsMin, wsMax)
        if wsMin == wsMax: vr=0.5
        else: vr = (ws-wsMin) / (wsMax-wsMin)
        #print('vr', vr)
        return vr
    else:
        #print(weights, vValue, n)
        wsMin = sum([-1 * w for w in weights])
        wsMax = sum([1 * w for w in weights[m-n+1:]]) #n-m+1 was old one
        #print('here', wsMin, wsMax, ws)
        if wsMin == wsMax: vr=-0.5
        else: vr = ((ws-wsMin) / (wsMax-wsMin)) - 1
        #print((ws-wsMin), (wsMax-wsMin))
        #print('vr', vr)
        return vr
    return 1
        
def normalise(notNormalisedItems):
    #print('normalise')
    normlisedValues = {}
  
    for k,v in notNormalisedItems.items():
        #print(v, 'v')
        vType = types[attributes[k]]
        f = 0
        if '/' in vType[0]:
            #print('yes')
            if vType[1][0].isdigit():
                #print('vtype', vType, v)
                changeInValue = 1.0 / len(vType[0])
                f = 1.0 - changeInValue
                if '++' in v: v = int(v.split('++')[0]) + (2*changeInValue)
                elif '--' in v: v = int(v.split('--')[0]) - (2*changeInValue)
                elif '+' in v: v = int(v.split('+')[0]) + changeInValue
                elif '-' in v: v = int(v.split('-')[0]) - changeInValue
                
                n = int(vType[1].split('..')[1]) + 1

                normalisedV = float(v) / (n -1 + f)
                normlisedValues[k] = normalisedV
                #print(normalisedV)
            else: normlisedValues[k] = v
        elif not vType[0].isdigit(): normlisedValues[k] = v
        else:
            v = int(v) - int(vType.split('..')[0])
            n = int(vType.split('..')[1]) - int(vType.split('..')[0]) + 1
            normalisedV = float(v) / (n -1 + f)
            #print(n, normalisedV)
            normlisedValues[k] = normalisedV
    #print('normal', normlisedValues)
    return normlisedValues

def seprateBrackets(bracketRules):
    if '(' not in bracketRules: return [bracketRules]
    stack = []
    temp = []
    word = ''
    for br in bracketRules:
        if br == '(':
            if word != '':
                temp.append(word)
                word=''
            stack.append(temp)
            temp = []
        elif br == ')':
            if word != '':
                temp.append(word)
                word=''
            if stack:
                temp = stack[-1] + [temp]
                del stack[-1]
            splitted = temp
        else:
            word += str(br)
    if word != '': temp.append(word)
    #print(temp)
    return temp


studentsMarks = {}
types = {}
attributes = {}
rules = {}
results = {}

def run(inputFile='input.csv', ruleFile='rules.csv'): #Run the pmark 
    global studentsMarks, types, attributes, rules, results 
    studentsMarks = readInput(inputFile) #Gets the student marks
    types, attributes, rules, results = readRules(ruleFile) #Parses marking scheme
    return calculateMark() #Calculates marks
# ##print(rules, types, results)


