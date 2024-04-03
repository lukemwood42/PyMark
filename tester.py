import findMaxGrade
import GeneticAlgorithm
import verticesSearch



for i in range(1, 10):
    print('Test' + str(i) + ': -------------------------------------')
    ruleInput = 'test_case' + str(i) + '.csv' 

    #print('bf')
    findMaxGrade.bruteForce(ruleInput)
    #print('rr')
    findMaxGrade.reducedRules(ruleInput)
    #print('ga')
    ga = GeneticAlgorithm.GeneticAlgorithm(ruleInput)
    ga.run()
    #print('va')
    vs = verticesSearch.verticesSearch(ruleInput)
    vs.ProcessData()
    #print('rules', vs.rules)
    for bound in vs.results.values()[0][1:]:
        vs.genFeasibleArea(bound)
        outputValues = ['\n']
        with open('outputVerticesSearch.csv', 'a') as f:
            f.writelines(outputValues)
            

    #print("")