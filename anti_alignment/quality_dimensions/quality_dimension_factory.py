# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 23:12:30 2020

@author: USER
"""
from anti_alignment.objects.anti_alignments import AntiAlignmentFactory
from anti_alignment.preprocessing.utility import Utility
from anti_alignment.quality_dimensions.precision import Precision
from anti_alignment.quality_dimensions.generalization import Generalization

class Quality_dimension_factory:
    def __init__(self,log,model,i_m,f_m):
        self.log = log
        self.occurence=None
        self.model = model
        self.i_m = i_m
        self.f_m =f_m
        self.flower=False
        self.alignment_factory=None
    def compute_alignments_of_length(self,n=None):
       
        Utility.check_inputs(self.log,self.model,self.i_m,self.f_m)
        self.flower=False        
        if Utility.check_if_flower_model(self.model, self.log):
            self.flower=True
            
            
        cleanlog,occurence_of_variants=Utility.clean_log_from_non_fitting_traces(self.log,self.model,self.i_m,self.f_m,True)
        min_trace_len = min(len(trace) for trace in cleanlog)
        #if n = None then n=2*length of longest traces
        if n== None:    
            n=2*max(len(trace) for trace in cleanlog)
        elif n<min_trace_len:
            self.flower=False  
            return
        self.occurence=occurence_of_variants
        self.log=cleanlog
        net=Utility.clean_tau_loops(self.model,self.i_m, self.f_m)
        if(not self.flower):
            
            alignment_factory=AntiAlignmentFactory(cleanlog,net,self.i_m,self.f_m,"dfs","levenshtein")
            alignment_factory.compute_anti_alignments(cleanlog, n)
            self.alignment_factory=alignment_factory
    def apply(self, alpha_precision=0.5,alpha_generalization=0.5):
            """
            To call method to obtain the precision score given those parameters
            :param n: length of the longest
            :param alpha: Weight of trace based score. 1-alpha is weight of log-based score
            :return: Precision Score
            """
            if (self.alignment_factory==None):
                return None,None
            #will be checked in the main when it is finished
            alphas=[]
            precision_calc=False
            generalisation_calc=False
            if(isinstance(alpha_precision,float) or isinstance(alpha_precision,int)):
                precision_calc=True
                alphas.append(alpha_precision)
            if(isinstance(alpha_generalization,float) or isinstance(alpha_generalization,int)):
                generalisation_calc=True
                alphas.append(alpha_generalization)
            if(len(alphas)==0):
                return None,None
            
            
            
            
            Utility.check_alpha_boundaries(alphas)
            
            precision=None
            generalisation=None
            
            if(self.flower):
                precision=0
                generalisation=1
            else:        
                if(precision_calc):
                    precision_module=Precision(self.log,self.alignment_factory)
                    precision=precision_module.apply(alpha_precision)
                if(generalisation_calc):
                    generalization_module=Generalization(self.log,self.occurence,self.alignment_factory)
                    generalisation=generalization_module.apply(alpha_generalization)
            #compute all anti-alignemts with length equal or less than n
            
            if(precision_calc and generalisation_calc):
                return (precision,generalisation)
            elif(precision_calc):
                return precision
            elif(generalisation_calc):
                return generalisation
            else:
                return None,None