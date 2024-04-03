
PyMark.py contains the research version of PMark. To run PyMark on its own, uncomment line 598: print(run()). This will use input.csv as the input file for the set of students as default. The marking scheme used by it will be rules.csv as default. Printing the score values for each grade boundary for each student. Comment line 199: return boundariesV to return the marks instead of scores. Can be run by "python PyMark.py"

findMaxGrade.py contains the brute force search algorithm and reduced rules algorithm. Both use rules.csv as input marking schemes as default. Uncomment line 246: bruteForce() to run brute force algorithm. Output is written to outputBruteForce.csv. Uncomment line 247: reducedRules() to run reduced rules algorithm. Output is written to outputReducedRules.csv. Can be run by "python findMaxGrade.py"

geneticAlgorithm.py contains the genetic algorithm. Using rules.csv as input marking scheme as default. Lines 12 - 16 can be changed to vary genetic algorithm parameters. Uncomment line 197 and line 198 to run. Output is written to outputGeneticAlgorithm.csv. Can be run by "python geneticAlgorithm.py"

verticeSearch.py contains the vertices search. Using rules.csv as input marking scheme as default. Uncomment line 516 - 520 to run algorithm. Output is written to outputVerticesSearch.csv. Can be run by "python verticeSearch.py"

When running tester.py and randomGen.py if the line that were commented aren't commented then the first result produced will be for the marking scheme inrule.csv

tester.py runs all the test cases on the algorithms. Test cases can be found in test_case1.csv - test_case9.csv. Can be run by "python tester.py" 

randomGen.py contains the random marking scheme generator. Writes random generated marking scheme to randomGenMS.csv. which is used as marking scheme inputs on algorithms. Prints the average time to run each algorithm. Can be run by "python randomGen.py"

I ran out of time to tidy up code so it's a bit messy but works. 
