# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 22:31:58 2020

@author: USER
"""


from pm4py.objects.petri.importer import factory  as petri_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking
import os

from pm4py.objects.petri.petrinet import PetriNet
import copy
Place=PetriNet().Place
Arc=PetriNet().Arc
class PetriNetCheck:
    @staticmethod  
    def filter_tau(net,i_m, f_m):
        #net=copy.deepcopy(my_net)
        places=list(net.places)
#        i=0
#        im_found=False
#        fm_found=False
#        while i<len(places):
#           if im_found==False and places[i] in i_m:
#               i_m=places[i]
#               im_found=True
#           if fm_found==False and places[i] in f_m:
#               f_m=places[i]
#               fm_found=True
#           if fm_found and im_found:
#               break
#           i+=1  
        go_on=True
        while go_on:
            visited=set()
            for place in places:
                if place in visited:
                    continue
                go_on=PetriNetCheck.find_cycle(net,place,[],visited)
                if go_on:
                    break
#        from pm4py.visualization.petrinet import factory as pn_vis_factory
#        gviz = pn_vis_factory.apply(net, i_m, f_m)
#        pn_vis_factory.view(gviz)    
        return net
#        net, im, fm = petri_importer.apply("../test/test_one/tau_loop.pnml")
#        filter_tau(net,im,fm)

    @staticmethod          
    def find_cycle(net,place,tau_places,visited):    
        visited.add(place)
        circle=[]
        found=False
        for current_place_name in tau_places:
            if place.name in current_place_name:
                found=True  
            if found:
                circle.append(current_place_name)
                  
        #merge circle
        if len(circle)!=0:
            outs_redirect=[]
            in_redirect=[]
            names_to_join=[]        
            for my_place_name in circle:
                search=list(net.places)
                my_place=None
                for key in search:
                    if key.name ==my_place_name:
                        my_place=key
                        break
                
                outs_redirect.append(my_place.out_arcs)
                in_redirect.append(my_place.in_arcs)
                names_to_join.append(my_place.name)             
                net.places.remove(my_place)
                
            new_place=Place('_'.join(names_to_join))
            net.places.add(new_place)
            
           
                   
            for out_arcs in outs_redirect:
                for out_arc in out_arcs:   
                    out_arc._Arc__source=new_place#                
                    out_arc.target._Transition__in_arcs=PetriNetCheck.remove_dupilcate_arcs(net,out_arc.target.in_arcs)
            for in_arcs in in_redirect:
               for in_arc in in_arcs:               
                   in_arc._Arc__target=new_place                
                   in_arc.source._Transition__out_arcs=PetriNetCheck.remove_dupilcate_arcs(net,in_arc.source.out_arcs)
            new_place._Place__in_arcs=PetriNetCheck.remove_dupilcate_arcs(net,set.union(*in_redirect))
            new_place._Place__out_arcs=PetriNetCheck.remove_dupilcate_arcs(net,set.union(*outs_redirect))
    
    #       
            set_new_outs=set() 
            set_new_ins=set()
            arcs_to_check=set.union(new_place.out_arcs,new_place.in_arcs)
            transitions_to_remove=set()
            while(len(arcs_to_check)>0):
                
                arc=arcs_to_check.pop()
                forward=True
                transition=arc.target  
                if transition==new_place:
                    forward=False
                    transition=arc.source
                hits_new_node=False            
                if forward:
                    for target_arc in transition.out_arcs:                    
                        if(target_arc.target.name in new_place.name and transition.label==None):
            
                            hits_new_node=True                    
                            break
                else:
                    for target_arc in transition.in_arcs:                    
                        if(target_arc.source.name in new_place.name and transition.label==None):                        
                            hits_new_node=True                    
                            break
                if hits_new_node:   
                    transitions_to_remove.add(transition)
                    
                    
                else:
                    if forward:
                        set_new_outs.add(arc)
                    else:
                        set_new_ins.add(arc)
            new_place._Place__out_arcs=set_new_outs
            new_place._Place__in_arcs=set_new_ins            
            
            for transition in transitions_to_remove:       
                PetriNetCheck.remove_forward_dependencies(net,transition)
                PetriNetCheck.remove_backward_dependencies(net,transition)
                net.transitions.discard(transition)
            return True
    
                    
        outs=place.out_arcs
        tau_places.append(place.name)
        for arc in outs:
            transition=arc.target
            if transition.label==None:            
                for out in transition.out_arcs:        
                    found_cycle=PetriNetCheck.find_cycle(net,out.target,copy.deepcopy(tau_places),visited)
                    if found_cycle:
                        return True
        return False   
    @staticmethod        
    def remove_forward_dependencies(net,node):
        while(len(node.out_arcs)>0):
            arc=node.out_arcs.pop()
            arc.target.in_arcs.discard(arc)
            net.arcs.discard(arc)
    @staticmethod        
    def remove_backward_dependencies(net,node):
        while(len(node.in_arcs)>0):                    
            arc=node.in_arcs.pop()
            arc.source.out_arcs.discard(arc)
            net.arcs.discard(arc)
    @staticmethod        
    def remove_dupilcate_arcs(net,arcs):
        clean_arcs=set()
        while(len(arcs)>0):
            arc=arcs.pop()            
            unique_arc=True
            for check_arc in clean_arcs:
                if arc.source==check_arc.source and arc.target == check_arc.target:
                    unique_arc=False
                    net.arcs.discard(arc)
                    break
            if unique_arc:
                clean_arcs.add(arc)
        return clean_arcs
        
        




        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        