import pm4py
import sys
from pm4py.algo.conformance.alignments import factory as alignments
from pm4py.algo.conformance.alignments.versions import state_equation_a_star as star
from anti_alignment.preprocessing.petri_net_analyzer import PetriNetCheck

#from pm4py.statistics.variants.log.get import get_variants
#def prepare_event_log(log):
#    """
#    We convert the usual Pm4Py object of an event log. The result is a list of variants of traces and these are
#    represented as strings.  We are only interested in the name of the events. We have to split on the ',' symbol,
#    because we receive only one long string
#    :param log: PM4Py object of an event log
#    :return: List of list, whereby each list represents a variant of a trace
#    """
#    variants = list(get_variants(log).keys())
#    splited_variants=[]
#    for trace in variants:
#        splited_variants.append(trace.split(","))
#    return splited_variants
class Utility:
    @staticmethod
    def get_activities(log):
        """
        Returns a set of event names of a given event log.
        :param log: PM4Py event log representation
        :return: set of event names that appears in event log
        """
        activities=set()
        for trace in log:
            for event in trace:
                #In most event logs, concept:name contains the name of the executed activity
                activities.add(event['concept:name'])
        return activities
    @staticmethod
    def get_perfect_fitting_trace_variants_and_number_of_occurence(replay_result, activities,count_occurence=False):
        """
        Returns a tuple. First element is a list of traces whereby each trace is perfectly fitting. Only one variant for each trace. Second element is a dict. key is tuple (trace representation), value is number of occurence.
        If no occurence counting is done, only the list of traces is returned
        :param replay_result: Replay result obtained from the Token-based replay
        :param activities: Set of activities that occur in an event log
        :return: List of perfect fitting traces
        """
        filtered_log=[]
        occurence={}
        for result in replay_result:
            trace=[]
            for alignment in result['alignment']:
                if alignment[1] in activities:
                    trace.append(alignment[1])
            if trace not in filtered_log:
                filtered_log.append(trace)
                occurence[tuple(trace)] = 1
            else:
                occurence[tuple(trace)] += 1
        if count_occurence:
            return (filtered_log, occurence)
        else:
            return filtered_log

    @staticmethod
    def clean_log_from_non_fitting_traces(log,model,i_m,f_m, occurence=False):
        activities=Utility.get_activities(log)
        #filter event log. The perfect fitting traces are kept. However, for unfitting traces, we keep the alligned event log
        replay_result=alignments.apply(log, model, i_m, f_m)        
        return Utility.get_perfect_fitting_trace_variants_and_number_of_occurence(replay_result, activities,occurence)
    
    @staticmethod
    def check_inputs(log,model,i_m,f_m):
        #check if log is PM4Py log object
        if not isinstance(log, pm4py.objects.log.log.EventLog):
            sys.exit('Log is not a PM4Py event log representation.')
        #check if net is PM4Py Petri Net object
        if not isinstance(model, pm4py.objects.petri.petrinet.PetriNet):
            sys.exit('Model is not a PM4Py Petri Net representation.')
        if not isinstance(i_m, pm4py.objects.petri.petrinet.Marking):
            sys.exit('Initial Marking is not a PM4Py Marking representation.')
        if not isinstance(f_m, pm4py.objects.petri.petrinet.Marking):
            sys.exit('Final Marking is not a PM4Py Marking representation.')
        # check if alpha<=1 or less than 0
        
    @staticmethod
    def check_alpha_boundaries(alphas):
        if type(alphas) is not list: 
            alphas=[alphas]
        for alpha in alphas:
            if alpha > 1 or alpha < 0:
                sys.exit('Alpha is either greater than one or smaller than 0.')
    @staticmethod
    def check_if_flower_model(model, log):
        """
        Quick check to detect obvious flower model. All transitions that are named by an actual event share the same place.
        :param model: PM4Py Petri Net representation
        :param log: PM4Py Event log object
        :return: True if flower model; false otherwise
        """
        activities = Utility.get_activities(log)
        source_places=set()
        target_places=set()
        for transition in model.transitions:
            if transition.name or transition.label in activities:
                for arc in transition.in_arcs:
                    source_places.add(arc.source)
                for arc in transition.out_arcs:
                    target_places.add(arc.target)
        if source_places==target_places:
            return True
        else:
            return False
    @staticmethod
    def clean_tau_loops(net,im,fm):
        return PetriNetCheck.filter_tau(net,im,fm)
    
    
    @staticmethod
    def flatten_list(lst):
        """
        flattens an array

        thie thee.g. converts a list of lists
        into a single one by appending all items into one big list
        :param lst: a nested list
        :return: a flat list
        :rtype: arr
        """
        flat_list = []
        for sublist in lst:
            for item in sublist:
                flat_list.append(item)
        return flat_list
