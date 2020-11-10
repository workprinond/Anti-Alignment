import sys
sys.path.insert(1, 'C:\\Users\\USER\\Documents\\Vorlesungen\\Conformance Checking\\lab-anti-alignment')

import time
from anti_alignment.quality_dimensions.quality_dimension_factory import Quality_dimension_factory
from pm4py.objects.petri.importer import factory  as petri_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
import os
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.evaluation.generalization import factory as generalization_factory
path="3-way match - invoice after GR - service - without SRM"
log_file= os.path.join(path, "BPI_Challenge_2019.xes")
log=xes_importer.import_log(log_file)


for model in ["02.pnml"]:
    net, im, fm = petri_importer.apply(os.path.join(path, model))
    print("Current Model: "+model)
    print("Number of places: "+str(len(list(net.places))))
    print("Number of transitions: " +str(len(list(net.transitions))))
    results=[]
    fac=Quality_dimension_factory(log, net, im, fm)
    
    while len(results)<1:
        start=time.time()
        fac.compute_alignments_of_length()
        (pre, gen)=fac.apply()            
        end=time.time()
        results.append(end-start)
    print()
    print("Results of our approach")
    print("Precision: "+str(pre))
    print("Generalization: "+str(gen))
    print("Mean time: "+str(sum(results)/len(results)))
    print()

#        results = []
#        while len(results)<5:
#            start=time.time()
#            pre = precision_factory.apply(log, net, im, fm)
#            end=time.time()
#            results.append(end-start)
#        print("Results of PM4Py approach")
#        print("Precision: "+str(pre))
#        print("Mean time: "+str(sum(results)/len(results)))
#        print()
#        results = []
#        while len(results) < 5:
#            start = time.time()
#            gen = generalization_factory.apply(log, net, im, fm)
#            end = time.time()
#            results.append(end - start)
#        print("Results of PM4Py approach")
#        print("Generalization: " + str(gen))
#        print("Mean time: " + str(sum(results) / len(results)))
#        print()
#        print()



#eval()
