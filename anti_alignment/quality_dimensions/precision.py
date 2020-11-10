from anti_alignment.objects.anti_alignments import AntiAlignmentFactory
from anti_alignment.preprocessing.utility import Utility

import sys

class Precision:
    def __init__(self,log,alignment_factory):
        self.cleanlog=log
        self.alignment_factory=alignment_factory

    def apply(self,alpha=0.5):
        """
        To call method to obtain the precision score given those parameters
        :param n: length of the longest
        :param alpha: Weight of trace based score. 1-alpha is weight of log-based score
        :return: Precision Score
        """
        #compute all anti-alignemts with length equal or less than n
        
        t_b_precision=self.trace_based_precision(self.alignment_factory, self.cleanlog)
        l_b_precision=self.log_based_precision(self.alignment_factory, self.cleanlog)
        return alpha*t_b_precision+(1-alpha)*l_b_precision

    def trace_based_precision(self, alignment_factory, log):
        """
        Computes the trace-based precision.
        :param alignment_dict: Dictionary, where the keys are the length of a alignment, and the value is a list of
        alignments
        :param log: Log that is already converted into a list of trace variants
        :return: trace.based precision score
        """
        alignment_dict=alignment_factory.get_dict_of_anti_alignments()
        sum_of_distance = 0
        for trace in log:
            possible_alignments=[]
            for length,alignments in alignment_dict.items():
                if length <= len(trace):
                    for alignment in alignments:
                        possible_alignments.append(alignment)
            log_without_trace = log.copy()
            log_without_trace.remove(trace)
            anti_alignment=alignment_factory.get_maximal_complete_anti_alignment(possible_alignments, log_without_trace, trace)            
            sum_of_distance+=alignment_factory.compute_distance(trace,anti_alignment)
        return 1-(1/len(log))*sum_of_distance

    def log_based_precision(self, alignment_factory, log):
        """
        Compute the log based precision. Note that we do not have to consider a maximum length in this case. The computation
        of the dictionary already considers a bounded length n.
        :param alignment_dict: dictionary, where the keys are the length of a alignment, and the value is a list of
        alignments
        :param log: Log that is already converted into a list of trace variants
        :return: log based precision score
        """
        all_alignments=alignment_factory.get_list_of_anti_alignments()
        return 1-alignment_factory.get_maximal_complete_anti_alignment(all_alignments, log, with_distance=True)[0]