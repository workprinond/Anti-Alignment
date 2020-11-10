from anti_alignment.algo.search.dfs import DepthFirstSearch
from anti_alignment.algo.graph_construction.search_tree import SearchTree
from anti_alignment.distance_metrics.levenshtein import Levenshtein_Distance
from anti_alignment.preprocessing.utility import Utility
import math
import copy


class AntiAlignment:
     def __init__(self,labels,nodes):
         self.labels=labels
         self.nodes=nodes
     def get_labels(self):
         return self.labels
     def get_nodes(self):
         return self.nodes
    #legth of an anti_alignment is the legth of the labels/trasitions
    #since there can be more nodes than labels due to tau transitions
     def __len__(self):
        return len(self.labels)
class AntiAlignmentFactory:
    """
	Create a factory to compute, store and manage Anti-alignments
	"""

    def __init__(self, log,model,i_m,f_m,search_algorithm, distance_function):
        """
        create the factory while selecting a search algorithm and a distance function

        :param search_algorithm: identifier to select an implemented search_algorithm
        :param distance_function: identifier to select an implemented distance function
        """
        self.log = log
        self.model = model
        self.i_m = i_m
        self.f_m = f_m
        if search_algorithm == "dfs":
            self.search_algorithm = DepthFirstSearch
        if distance_function == "levenshtein":
            self.distance_function=Levenshtein_Distance()            
        #this alignment list is a list of tuples with the first element
        #being the list of tuples and the second being the list of nodes
        self.alignment_list = []
        self.reachability_graph=None
    def get_reachability_graph(self):
        return self.reachability_graph
    def get_initial_marking(self):
        return self.i_m
    def get_final_marking(self):
        return self.f_m
        #save as set
    def compute_anti_alignments(self,log,longest_search):
        """
        Compute anti alignments

        Compute all possible anti alignments between a log and a model, whereby the length does not exceed n

        :param event_log: PM4Py event log representation
        :param n: maximal of the anti_alignment to consider
        """
        min_trace_len = min(len(trace) for trace in log)
        search_tree_factory=SearchTree(self.model,self.i_m,self.f_m) 
        i_m,f_m,G=search_tree_factory.apply(longest_search)
        self.i_m = i_m
        self.f_m = f_m
        self.reachability_graph=G
        alignments = []
        search=self.search_algorithm(G,self.i_m,self.f_m)
        # iterate through all lenghts
        alignments_of_length = search.findPaths(longest_search)
        alignments.append(alignments_of_length)
        # flatten the list of lists of path into a list of paths        
        flat = Utility.flatten_list(alignments)
        # remove duplicates
        alignment_list=[]
        #alignment_set=set(flat)
        for alignment in flat:
            alignment_as_list=list(alignment[0])
            if(len(alignment_as_list)>=min_trace_len):
                alignment_list.append(AntiAlignment(alignment_as_list,alignment[1]))
        self.alignment_list=alignment_list
            
    def get_list_of_anti_alignments(self):    
        """
        return a list of anti alignemtns
        
		:return: list of alignments
        :rtype: arr
		"""
        return self.alignment_list
    def get_dict_of_anti_alignments(self):
        """
        Returns a dictionary of anti alignments
        
		:return: Dict of alignments. Key is the length of the alignments, value is a list of alignments which have this
        length
        
        :rtype: dict
		"""
        alignments=self.get_list_of_anti_alignments()
        alignment_dict={}
        for index, value in enumerate(alignments):
            if len(alignments[index]) in alignment_dict:
                alignment_dict[len(alignments[index])].append(value)
            else:
                alignment_dict[len(alignments[index])]=[value]
        return alignment_dict

    def compute_distance(self,trace,anti_alignment):
        """
        Method to compute the distance between a trace and an anti-alignment.
        
        Computes the distance between the given parameters
        
        :param anti_alignment: an anit-alignment as a list of event names
        :param trace: List of event names
        :return: the distance between the anti-alignment and the trace bases on the distance function
		selected at factory contruction
        :rtype: int
        """
        return self.distance_function.get_distance(trace, anti_alignment.get_labels())/max(len(anti_alignment.get_labels()), len(trace))

    def compute_min_distance(self, anti_alignment, log):
            """
            computes the minimum distance of the anti alignment from the log

            computes the minimum distance of the anti alignment from the log

            :param anti_alignment: List of strings
            :param log: prepared event log, meaning: list of list of strings; only variants
            :return: minimum distance from the anti-alignment towards any trace in the log
            """
            if len(log)==0:
                #As defined in the paper. If a log is a empty, the distance value is 1.
                return 1
            minimum = float('inf')
            for trace in log:                
                distance = self.compute_distance(trace, anti_alignment)
                if distance < minimum:
                    minimum = distance
            return minimum


    def get_maximal_complete_anti_alignment(self,alignments, log, trace=None, with_distance=False):
        """
        Method to receive the maximal, complete Anti-alignment.
        
        Method to receive the maximal, complete Anti-alignment.
        It is possible that there are multiple anti-alignments with the same distance. However,
        one of these can be the same as the removed trace for the trace-based precision score. By checking these
        requirements we ensure that we try to pick another maximal-complete anti-alignment
        
        :param alignments: list of alignments, whereby each alignment is a list of strings, representing the transition
        labels without tau
        
        :param log: PM4Py representation of an event log
        :param trace: List of event names. Needed for trace-based computation
        :param with_distance: Boolean value. If true, return tuple, whereby second element is anti-alignment, fist is distance. Needed for gerneralization score.
        :return: the maximum complete anti-alignment
        :rtype: arr
        """
        maximal_anti_alignment = (0, None)
        for alignment in alignments:
            distance = self.compute_min_distance(alignment, log)
            if maximal_anti_alignment[0] == distance and alignment.get_labels()!=trace:
                #It is possible that there are multiple anti-alignments with the same distance. However,
                # one of these can be the same as the removed trace for the trace-based precision score. By checking these
                #requirements we ensure that we try to pick another maximal-complete anti-alignment
                maximal_anti_alignment = (distance, alignment)
            if maximal_anti_alignment[0] < distance:
                maximal_anti_alignment = (distance, alignment)
        if  not with_distance:
            return maximal_anti_alignment[1]
        else:
            return maximal_anti_alignment