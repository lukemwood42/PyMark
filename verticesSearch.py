import PyMark
import numpy as np
import collections
import itertools

class verticesSearch:

    types = None
    attributes = None
    rules = None
    results = None 

    def __init__(self, ruleInput='rules.csv'):
        self.types, self.attributes, self.rules, self.results = PyMark.readRules(ruleInput)

    def ProcessData(self):
        types = self.types
        rules = self.rules
        attributes = self.attributes
        newruleTypes = {}
        resultTypes = {}
        for ty, val in types.items():
            fractions = None
            if isinstance(val, list): 
                if val[0][0] == '-': 
                    fractions = val[0]
                    if val[1][0].isdigit(): itemLst = val[1]
                    else: itemLst = val[1:]
                elif '=' in val[1]:
                    resultTypes[ty] = val
                    continue
                else: itemLst = val
            else: itemLst = val

            if itemLst[0].isdigit() and ty[0] != 0:
                splitItmLst = itemLst.split('..')
                itemLst = range(int(splitItmLst[1]) - int(itemLst[0]) + 1)
            else: 
                itemLst = range(len(itemLst))
            
            if fractions: 
                itemLst = [fractions] + range((itemLst[-1]+1) * (len(fractions))) 
            newruleTypes[ty] = itemLst
        
        
        
        newRules = {}
        for boundary, ruleList in rules.items():
            newBoundaryRules = []
            for rule in ruleList:
                rule = rule.split('and')
                rule = [r.split('or') for r in rule]
                rule = [[self.convert(v1, attributes, newruleTypes) for v1 in v2] for v2 in rule]
                newBoundaryRules.append('and'.join(['or'.join(r) for r in rule]))
            newRules[boundary] = newBoundaryRules
        
        self.types = newruleTypes
        self.rules = newRules

    def convert(self, val, attributes, attrNewType):
        #print('start of convert')
        #print('attrnew type' , attrNewType)
        #print(val)
        if '%' in val: 
            weight = val.split('%')[0] + '%'
            val = val.split('%')[1]
        else: weight = ""

        if 'of{' in val: 
            idx = val.index('{')
            newVal = val[idx+1:-1]
            #print('newVal', newVal.split(','))
            convertedRule = val[:idx+1]
            for nv in newVal.split(','):
                convertedRule += self.convert(nv, attributes, attrNewType) + ','
            #print(convertedRule)
            convertedRule = convertedRule[:-1] + '}'
            #print('convertedRule', convertedRule)
            return convertedRule

        val = val.split('=')
        attrType = self.types[attributes[val[0]]]

        if attrType[0][0] == '-':
            if val[1][0].isdigit(): 
                idx = int(val[1]) - int(attrType[1].split('..')[0])
                idx *= len(attrType[0])
                return weight + val[0] + '=' + str(idx)
            else: 
                idx = attrType[1:].index(val[1])
                idx *= len(attrType[0])
                return weight + val[0] + '=' + str(idx)
        else:   
            if val[1][0].isdigit(): 
                idx = int(val[1]) - int(attrType.split('..')[0])
                return weight + val[0] + '=' + str(idx)
            else: 
                idx = attrType.index(val[1])
                return weight + val[0] + '=' + str(idx)

    def genFeasibleArea(self, fullBoundary):
        boundary = fullBoundary.split('=')[0]
        #print('rules', self.rules[boundary])
        axes = self.rules[boundary]
        axesConstraints = {}
        if self.results.values()[0][1].split('=')[0] == boundary: 
            return
            for axis in axes:
                if '%' in axis:
                    if not any([l in axis for l in ['or', 'and', 'of{']]): w = int(axis.split('%')[0]) / 100
                    else: w = 1
                else: w = 1
                andMaxfail, andAxisWeights = self.axisConstrait(axis, boundary)
                axesConstraints[axis] = [str(w)] + self.findMaxAxisConstrait(andMaxfail, andAxisWeights)

            #print(axesConstraints)
            #[maximum failing grade, maximum grade(mostly 1)]

            weightings = [float(v[0]) for v in axesConstraints.values()]
            totalWeighting = sum(weightings)
            weightings = [w / totalWeighting for w in weightings]
            verticesWs = []
            for axisCName, axisC in axesConstraints.items():
                listOfV = [v[2] if k != axisCName else v[1] for k, v in axesConstraints.items()]
                verticesWs.append(sum([v * w for v, w in zip(listOfV, weightings)]))

            ws = max(verticesWs)
            m = len(axes)
            sortedWeightIndex = np.array((np.argsort(weightings)))
            weightings = np.array(weightings)[sortedWeightIndex]
            wsMin = sum([-1 * w for w in weightings])
            wsMax = sum([1 * w for w in weightings[1:]])
            if wsMin == wsMax: vr=-0.5

            else: vr = ((ws-wsMin) / (wsMax-wsMin)) - 1

            grade = int(int(fullBoundary.split('=')[1]) * vr + int(fullBoundary.split('=')[1]))
            #print('Max grade without achieving ' + boundary + ' is - ' + str(grade))
            exit()



        else: 
            boundaryBelow = self.results.values()[0][self.results.values()[0].index(fullBoundary) - 1]
            boundaryBelowAxes = self.rules[boundaryBelow.split('=')[0]]

            boundaryBelowAxesVValues = []
            boundaryBelowAxesWeights = []

            #print('bba', boundaryBelowAxes)
            for bba in boundaryBelowAxes:

                bba = bba.split('and')
                bba = [ax.split('or') for ax in bba]
                #print(165, bba)

                if len(bba[0]) == 1 and len(bba[0][0]) == 1 and '%' in bba[0][0]: boundaryBelowAxesWeights.append(int(bba[0][0].split('%')[0])/100.0)
                else: boundaryBelowAxesWeights.append(1)

                andV_Values = []
                andV_Weights = []
                
                for andAxis in bba:
                    #print('andAxis', andAxis)
                    if len(andAxis) == 1 and '%' in andAxis[0]: andV_Weights.append(int(andAxis[0].split('%')[0])/100.0)
                    else: andV_Weights.append(1)
                    orV_Values = []
                    orV_Weights = []
                    for orAxis in andAxis:
                        if '%' in orAxis: 
                            orAxis = orAxis.split('%')
                            orV_Weights.append(int(orAxis[0])/100.0)
                            orAxis = orAxis[1]
                        else: orV_Weights.append(1)

                        if 'of{' in orAxis: 
                            idxOf = orAxis.index('{')
                            n = self.findPredixN(orAxis[:idxOf])
                            orAxis = orAxis[idxOf+1: -1].split(',')
                            orV_Values.append([n] + orAxis)
                            #print(181, [n] + orAxis)
                        else: orV_Values.append(orAxis)
                            
                        #print(orAxisMaxFail, 'orMax')
                        #print(orAxisWeights, 'weight')
                    andV_Values.append([orV_Weights, orV_Values])
                
                boundaryBelowAxesVValues.append([andV_Weights, andV_Values])
            #print(187, boundaryBelowAxesVValues)

            #vp = self.compoundRule(boundaryBelowAxesVValues, len(boundaryBelowAxesVValues), boundaryBelowAxesWeights, True)
            #print('vp', vp, boundaryBelowAxesVValues, boundaryBelowAxes)
            #print(andMaxfail, andAxisWeights)
            #exit()
            #andMaxfail, andAxisWeights = axisConstrait2()
            #vfConstait = self.findMaxAxisConstrait(andMaxfail, andAxisWeights)
            #axesConstraints[axis] = [str(w)] + [vfConstait, vp, 1]

            #print('axes', axes)
            axesConstraints = {}
            for axis in axes:
                if '%' in axis:
                    if not any([l in axis for l in ['or', 'and', 'of{']]): w = int(axis.split('%')[0]) / 100
                    else: w = 1
                else: w = 1
                andMaxfail, andAxisWeights = self.axisConstrait(axis, boundary)
                #print(andMaxfail, andAxisWeights)
                axesConstraints[axis] = [str(w)] + self.findMaxAxisConstrait(andMaxfail, andAxisWeights)

            #print('ac', axesConstraints)
            #[maximum failing grade, maximum grade(mostly 1)]

            weightings = [float(v[0]) for v in axesConstraints.values()]
            totalWeighting = sum(weightings)
            weightings = [w / totalWeighting for w in weightings]
            verticesWs = {}
            for axisCName, axisC in axesConstraints.items():
                listOfV = [v[2] if k != axisCName else v[1] for k, v in axesConstraints.items()]
                #print(listOfV)
                verticesWs[axisCName] = self.compoundRule(listOfV, len(weightings), weightings, False)
                #sum([v * w for v, w in zip(listOfV, weightings)])

            #print('vw', verticesWs)
            axis = [max(verticesWs.iterkeys(), key=(lambda key: verticesWs[key]))]
            #print(axis)
            axisVps = []
            for axis in axes:
                andMaxfail, listOfAttributes = self.axisConstrait2(axis, boundary)


                attributeSetToFail = []
                #print('loa', listOfAttributes)
                for andMax in andMaxfail:
                    andAttributeSetToFail = []
                    for orMax in andMax:
                        #print(202, orMax)
                        andAttributeSetToFail.append(orMax)
                        

         
                    attributeSetToFail.append(andAttributeSetToFail)
                #print('attributeSetToFail', attributeSetToFail)

                attributeSetToFail = self.genAttributeCombos(attributeSetToFail)
                #print('attributeSetToFail2', attributeSetToFail)
                vps = []
                for comboAsf in attributeSetToFail:
                    #print('comboaf', comboAsf)
                    for asf in comboAsf:
                        #print(asf)
                        #asf = [item for sublist in asf for item in sublist]        
                        #print('asf1', asf)

                        tempAsf = []
                        for a in asf:
                            #print(a, 'a')
                            if (isinstance(a, tuple) or isinstance(a, list)): 
                                for tupVal in a:
                                    #print(227, tupVal)
                                    tempAsf.append(tupVal)
                            else: tempAsf.append(a)
                        asf = tempAsf
                        #print(228, asf)
                        asf = [a.split('%')[1] if '%' in a else a for a in asf]
                        asf = [a.split('=') for a in asf]
                        asf = {a[0]: a[1] for a in asf}

                        #print('asf', asf)
                        vps.append([self.passingRule([boundaryBelowAxesWeights, boundaryBelowAxesVValues], asf), asf])
                    axisVps.append(vps)
                

            #print(axisVps)
            maxVp = max(axisVps,key=lambda item:item[0])
            #print('max', maxVp)
            maxVp = max(maxVp,key=lambda item:item[0])
            #print('max2', maxVp)
            #print('Max passing score for boundary ' + boundaryBelow + ' is: ' + str(maxVp[0]))
            #print('Which is acheivable when ' + str(maxVp[1]) + ' criteria isn\'t met.')
            #attrVals = [aName + '=' + str(self.types[ self.attributes[aName] ][self.types[self.attributes[aName]].index(int(maxVp[1][aName]))-1]) if aName in maxVp[1].keys() else aName + '=' + str(self.types[ self.attributes[aName] ][-1]) for aName in self.attributes.keys()] 
           # print(attrVals)
            maxVp[1] = str([n + '=' + str(a) for n, a in maxVp[1].items()]) 
            outputValues = [boundaryBelow + ' max passing score: ' + str(maxVp[0]) + ', with attributes ' + str(maxVp[1])]
            with open('outputVerticesSearch.csv', 'a') as f:
                f.writelines(outputValues)
            
            return
       

              
            
        


    def genAttributeCombos(self, attributeSetToFail):
        #print('gen attr')
        #print(attributeSetToFail)
        combos = []
        for asf in attributeSetToFail:
            #print('259', asf)
            asfRange = []
            for orAsf in asf:
                if int(orAsf[0]) == 1: orAsf = [orAsf[1:]]
                else: orAsf = list(itertools.combinations(orAsf[1:], len(orAsf) - int(orAsf[0])))
                #print(251, orAsf)
                asfRange.append(orAsf)
                #print(orAsf)
            #rint(267, asfRange)
            combos.append(list(itertools.product(*asfRange)))
        #print(268, asfRange)
        #print(270, combos)
        return combos







    def passingRule(self, belowRules, listOfAttributes):
        ruleV = []
        ruleVWeight = belowRules[0]
        belowRules = belowRules[1]
        for br in belowRules:
            #print('br', br)
            andWeight = br[0]
            andV = []
            for andBr in br[1]:
                #print('and', andBr)
                orWeight = andBr[0]
                orVal = []
                for orBr in andBr[1]:
                    #print('or', orBr)
                    if isinstance(orBr, list):
                        idvV = []
                        for ofVal in orBr[1:]:
                            #print(284, ofVal)
                            #print(listOfAttributes)
                            ofVal = ofVal.split('=')
                            if ofVal[0] not in listOfAttributes: idvV.append(1)
                            else: 
                                lenOfAttr = self.types[self.attributes[ofVal[0]]][-1]
                                av = (float(listOfAttributes[ofVal[0]]) - 1)/ lenOfAttr
                                rv = float(ofVal[1]) / lenOfAttr
                                #print('avrv', av, rv)
                                if av >= rv:
                                    #print('avrv', av, rv)
                                    if rv==1: idvV.append(1)
                                    else: idvV.append( (av-rv) / (1 - rv) )
                                else:
                                    #print('avrv', av, rv)
                                    idvV.append( (av / rv) -1)
                        orVal.append(self.compoundRule(idvV, orBr[0], [1] * len(orBr[1:]), True))
                        #print('orVal', orVal)
                    else:
                        orBr = orBr.split('=')

                        if orBr[0] not in listOfAttributes: orVal.append(1)
                        else: 
                            lenOfAttr = self.types[self.attributes[orBr[0]]][-1]
                            av = (float(listOfAttributes[orBr[0]]) - 1)/ lenOfAttr
                            rv = float(orBr[1]) / lenOfAttr
                            if av >= rv:
                                #print('avrv', av, rv)
                                if rv==1: orVal.append(1)
                                else: orVal.append( (av-rv) / (1 - rv) )
                            else:
                                try:
                                    orVal.append( (av / rv) -1)
                                except:
                                    orVal.append(-1)
                #print('orVal', orVal)
                #print(orWeight)
                andV.append(self.compoundRule(orVal, 1, orWeight, True))
            #print('andVal', andV)
            #print(andWeight)
            ruleV.append(self.compoundRule(andV, len(andV), andWeight, True))
        
        #print('ruleV', ruleV)
        #print(ruleVWeight)
        return self.compoundRule(ruleV, len(ruleV), ruleVWeight, True)
            



    def passingRuleVCal(self, orAxis, listOfAttributes):
        orAxis = orAxis.split('=')
        if orAxis[0] not in listOfAttributes: return 1
        else: 
            lenOfAttr = self.types[self.attributes[orAxis[0]]][-1]
            av = (float(listOfAttributes[orAxis[0]]) - 1)/ lenOfAttr
            rv = float(orAxis[1]) / lenOfAttr
            if rv==1: return 1
            return ( (av-rv) / (1 - rv) )
                                

    def compoundRule(self, vValue, n, weights, passing):
        #print('compound rule', vValue, n, weights)
        m = len(vValue)
        s = float(sum(weights))
        weights = [w/s for w in weights]
        ws = sum([w * v for v, w in zip(vValue, weights)])
        sortedWeightIndex = np.array((np.argsort(weights)))
        vValue = np.array(vValue)[sortedWeightIndex]
        weights = np.array(weights)[sortedWeightIndex]
        if passing:
            wsMin = sum([-1 * w for v, w in zip(vValue[n:m], weights[n:m])]) #was n
            wsMax = sum([1 * w for v, w in zip(vValue, weights)])
            #print('passing', wsMin, wsMax)
            if wsMin == wsMax: vr=0.5
            else: vr = (ws-wsMin) / (wsMax-wsMin)
        else:
            wsMin = sum([-1 * w for w in weights])
            wsMax = sum([1 * w for w in weights[m-n+1:]])
            #print(ws, wsMin, wsMax)
            if wsMin == wsMax: vr=-0.5
            else: vr = ((ws-wsMin) / (wsMax-wsMin)) - 1
        return vr

    def axisConstrait(self, axis, boundary):
        #print('start of axis constrait')
        #print(axis)
        axis = axis.split('and')
        axis = [ax.split('or') for ax in axis]
        #print(axis)
        andMaxfail = []
        andAxisWeights = []
        
        for andAxis in axis:
            #print('andAxis', andAxis)
            if len(andAxis) == 1 and '%' in andAxis[0]: andAxisWeights.append(int(andAxis[0].split('%')[0])/100.0)
            else: andAxisWeights.append(1)
            orAxisMaxFail = []
            orAxisWeights = []
            for orAxis in andAxis:
                if '%' in orAxis: 
                    orAxis = orAxis.split('%')
                    orAxisWeights.append(int(orAxis[0])/100.0)
                    orAxis = orAxis[1]
                else: orAxisWeights.append(1)

                if 'of{' in orAxis: 
                    idxOf = orAxis.index('{')
                    n = self.findPredixN(orAxis[:idxOf])
                    orAxis = orAxis[idxOf+1: -1].split(',')
                    orAxis = [(-1.0/int(v.split('=')[1]))for v in orAxis]
                    orAxis.sort()
                    orAxis = [1 if i < n-1 else v for i, v in enumerate(orAxis)]
                    orAxisMaxFail.append(self.compoundRule(orAxis, n, [1]*len(orAxis), False))
                else: 
                    #print(orAxis)
                    orVal = int(orAxis.split('=')[1])
                    if orVal == 0: orAxisMaxFail.append(-1)
                    else: orAxisMaxFail.append(-1.0/orVal)
                    
                #print(orAxisMaxFail, 'orMax')
                #print(orAxisWeights, 'weight')
            andMaxfail.append(self.compoundRule(orAxisMaxFail, 1, orAxisWeights, False))
            return andMaxfail, andAxisWeights


    def axisConstrait2(self, axis, boundary):
        #print('start of axis constrait')
    
        axis = axis.split('and')
        axis = [ax.split('or') for ax in axis]
        #print('full axis', axis)
        andMaxfail = []
        #andAxisWeights = []
        attributesInAxis = []
        
        for andAxis in axis:
            #print('andAxis', andAxis)
            #if len(andAxis) == 1 and '%' in andAxis[0]: andAxisWeights.append(int(andAxis[0].split('%')[0])/100.0)
            #else: andAxisWeights.append(1)
            orAxisMaxFail = []
            #orAxisWeights = []
            attributeSetToFail = []
            for orAxis in andAxis:
                if 'of{' in orAxis: 
                    idxOf = orAxis.index('{')
                    n = self.findPredixN(orAxis[:idxOf])
                    tempOrAxis = orAxis[idxOf+1: -1].split(',')
                    attributesInAxis = [aia.split('=')[0] for aia in attributesInAxis if aia not in attributesInAxis]
                    orAxisMaxFail.append([n] + tempOrAxis)
                    
                else: 
                    orAxisMaxFail.append([1, orAxis])
                    attrIn = orAxis.split('=')[0]
                    if attrIn not in attributesInAxis: attributesInAxis.append(attrIn)

            
            andMaxfail.append(orAxisMaxFail)
        #print(347, andMaxfail, attributesInAxis)    
        return andMaxfail, attributesInAxis


    def findMaxAxisConstrait(self, andMaxfail, andAxisWeights):
        tempMaxAndFail = [v*w for v, w in zip(andMaxfail, andAxisWeights)]
        maxAndIdx = andMaxfail.index(max(andMaxfail))
        andMaxfail = [1] * maxAndIdx + [andMaxfail[maxAndIdx]] + [1] * (len(andMaxfail) - maxAndIdx - 1)
        maxFailV = self.compoundRule(andMaxfail, len(andMaxfail), andAxisWeights, False)
        return [maxFailV, 1]

    def findPredixN(self, prefix):
        if prefix == 'oneof': return 1
        elif prefix == 'allof': return len(reqs) - 2
        elif prefix == 'someof': return 1
        elif prefix == 'mostof': return math.floor( (len(reqs)-2) / 2) + 1
        elif prefix == 'allbutoneof': return len(reqs) - 3
        elif prefix[:7] == 'allbut' and prefix[-2:] == 'of': return int (reqs.count(',')) + 1 - int(prefix[7:-2])
        else: return int(prefix[:-2])


#------------- Uncomment below to run --------------------------
