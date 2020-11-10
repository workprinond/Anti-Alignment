# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 11:49:28 2020

@author: USER
"""
import os
import unittest

from pm4py.objects.petri.importer import factory  as petri_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking
import sys
import warnings

import warnings
warnings.filterwarnings("ignore")

sys.path.insert(1, 'C:\\Users\\USER\\Documents\\Vorlesungen\\Conformance Checking\\lab-anti-alignment')  # path where the project is when no IDE is used
from anti_alignment.quality_dimensions.quality_dimension_factory import Quality_dimension_factory
import numpy as np

log = xes_importer.import_log(os.path.join("../test/test_one/paper_log.xes"))

net, im, fm = petri_importer.apply("../test/test_one/fig1.pnml")

start=0.1
end=1
intervall=0.1
calc=True
if calc:
#factories=[]*((end-start)/intervall)
    factories={}
    precision={}
    generalisation={}
    k_vals=np.arange(start,end,intervall)
    for k in k_vals:
        fac=Quality_dimension_factory(log,net,im,fm)
        fac.compute_alignments_of_length(15)
        factories[15]=fac
        prec,gene=fac.apply(k,k)
        if prec==None:
            prec= 0
        if gene==None:
            gene= 0
        precision[k]=prec
        generalisation[k]=gene    
    
keys=list(precision.keys())
precs=list(precision.values())
gens=list(generalisation.values())
x=0

import matplotlib.pyplot as plt



fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.set_ylabel('Generalization', fontsize=18)
ax.set_xlabel('Ratio alpha (Trace based(alpha)+Log based (1-alpha))', fontsize=18)
ax.bar(keys,gens,width=0.05)
plt.show()


fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.set_ylabel('Precision', fontsize=18)
ax.set_xlabel('Ratio alpha (Trace based(alpha)+Log based (1-alpha))', fontsize=18)
ax.bar(keys,precs,width=0.05)
plt.show()