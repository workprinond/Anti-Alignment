from anti_alignment.preprocessing.utility import Utility
from anti_alignment.algo.search.dfs import DepthFirstSearch
from anti_alignment.objects.anti_alignments import AntiAlignmentFactory
import math

class Generalization:
    def __init__(self,log,occurence_of_variants,alignment_factory):
        self.cleanlog=log
        self.occurence_of_variants=occurence_of_variants
        self.alignment_factory=alignment_factory

    def apply(self,alpha=0.5):
        """
        Simple to call method. Returns the overall generalization score according to the paper.
        :param log: PM4Py event log representation
        :param net: PM4Py Petri Net representation
        :param initial_marking: PM4Py Marking object
        :param final_marking:  PM4Py Marking object
        :param n: maximal length of the longest anti-alignment
        :param alpha: Weighting factor between trac-based and log-based precision score. Weight for trace-based score is alpha, for log-based score 1-alpha
        :return: Generalization score
        :rtype: float
        """
        
        t_b_generalization=self.trace_based_generalization(self.alignment_factory, self.cleanlog, self.occurence_of_variants)
        l_b_generalization=self.log_based_generalization(self.alignment_factory, self.cleanlog)
        return float(alpha*t_b_generalization+(1-alpha)*l_b_generalization)
    
    
    def recovery_distance(self,anti_alignment, log, reachability_graph,im,fm):
        """
        Computes the recovery distance of an anti-alignemnt.
        
        When computing all possible runs in the reachbility graph, we can also safe the number of states that are visited.
        This information can be converted into a dict; key=run (has to be converted to a tuple), value=set of visited states
        Then, if we want to compute the recovery distance for an anti-alignment, we just have to combine the values(sets) 
        for the runs which are covered by the event log. Keep in mind that the log parameter will also contain the log without
        a specific trace for the trace-based computation.
        Afterwards, we have to compute the shortest path from every visited node in the anti-alignment to our new big 
        union of sets. Keep in mind that in this case a tau-transition has to be counted.
        
        
        :param anti_alignment: List of strings
        :param log: List of lists of strings
        :param reachability_graph: Networkx object
        :param initial_marking: PM4Py Marking object
        :param final_marking:  PM4Py Marking object
        :return: recovery distance
        """
        dfs=DepthFirstSearch(reachability_graph,im,fm)
        visited_nodes_of_anti_alignment_in_reachability_graph=anti_alignment.get_nodes()
        sets_of_state_visited_by_traces_of_log=set()
        #collect the log state space
        for trace in log:
            paths=dfs.find_Path_for_Trace(trace)                
            for path in paths:
                for node in path:
                    state=reachability_graph.nodes[node]['marking']    
                    state_tuple=tuple(state.tolist())
                    sets_of_state_visited_by_traces_of_log.add(state_tuple) 
        escaped_states=0
        max_escaped_states=0
        #check if and how long a trace escaped from the log state space
        for node in visited_nodes_of_anti_alignment_in_reachability_graph:
            state=tuple(reachability_graph.nodes[node]['marking'].tolist())
            if(state not in sets_of_state_visited_by_traces_of_log):
                escaped_states+=1
                if(escaped_states>max_escaped_states):
                    max_escaped_states=escaped_states
            else:
                escaped_states=0
        #the formula is 1/len(alignment transitions)-1 times steps to reach back to the state space
        #covered by the log, thats why an additional -1.0 is in the formula since with n nodes we have n-1 transitions
        recovery_distance=(1.0/((len(visited_nodes_of_anti_alignment_in_reachability_graph)-1.0)-1.0))*max_escaped_states
        return recovery_distance
         
    
    
    def trace_based_generalization(self,alignment_factory, log, occurence_of_variants):
        """
        Computes the trace based-generalization score according to the paper.
        :param alignment_factory: Anti-Alignment object
        :param log: List of lists, whereby each list contains strings (trace)
        :param occurence_of_variants: dictionary. Key is a trace converted into a tuple, value is the number of occurence in the log with only perfectly fitting traces
        :param reachability_graph: Networkx MultiDigraph
        :return: trace-based generalization score
        :rtype: float
        """
        alignment_dict = alignment_factory.get_dict_of_anti_alignments()
        reachability_graph = alignment_factory.get_reachability_graph()
        im = alignment_factory.get_initial_marking()
        fm = alignment_factory.get_final_marking()
        temp=0
        for variant in log:
            possible_alignments = []
            for length, alignments in alignment_dict.items():
                if length <= len(variant):
                    for alignment in alignments:
                        possible_alignments.append(alignment)
            log_without_trace = log.copy()
            log_without_trace.remove(variant)
            anti_alignment = alignment_factory.get_maximal_complete_anti_alignment(possible_alignments, log_without_trace,variant,True)
            recovery_distance_value=self.recovery_distance(anti_alignment[1], log_without_trace,reachability_graph,im,fm)
            temp+=occurence_of_variants[tuple(variant)]*(1-min(1, math.sqrt((1-anti_alignment[0])**2+recovery_distance_value**2)))
        return float(1/sum(occurence_of_variants.values())*temp)
    
    def log_based_generalization(self,alignment_factory, log):
        """
        Computes the log based generalizations score according to the paper.
        :param alignment_factory: Anti-Alignment object
        :param log: List of lists of strings, whereby each list represents a trace
        :param reachability_graph: Networkx MultiDigraph object
        :return: log-based generalization score
        :rtype: float
        """
        all_alignments=alignment_factory.get_list_of_anti_alignments()
        anti_alignment=alignment_factory.get_maximal_complete_anti_alignment(all_alignments, log, with_distance=True)
        return float(1-min(1, math.sqrt((1-anti_alignment[0])**2+self.recovery_distance(anti_alignment[1], log,
                                  alignment_factory.get_reachability_graph(),alignment_factory.get_initial_marking(),alignment_factory.get_final_marking())**2)))
