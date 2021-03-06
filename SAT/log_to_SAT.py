

from pm4py.objects.log.util.log import project_traces

BOOLEAN_VAR_TRACES_ACTIONS = "lambda_jia"
BOOLEAN_VAR_TRACES_MARKING= "m_jip"
WAIT_LABEL_TRACE="w"

NB_MAX_THREADS=50

from da4py.main.utils.formulas import And, Or

def log_to_SAT(traces_xes, transitions, variablesGenerator, size_of_run, wait_transition, label_l=BOOLEAN_VAR_TRACES_ACTIONS,max_nbTraces=None):
    '''
    This method returns the formulas of the Log.
    :param traces_xes:
    :param transitions (list)
    :param variablesGenerator (variablesGenerator) : to add the new boolean variables
    :param size_of_run (int) : to complete smaller words with "wait" transitions
    :param wait_transition (transition) : the "wait" transition
    :param label_l (string) : name of the boolean variables of the log
    :return:
    '''
    traces_multiples = project_traces(traces_xes)
    #traces=list(np.unique(traces_multiples))
    traces=traces_multiples
    traces = traces[:max_nbTraces] if max_nbTraces!=None else traces
    variablesGenerator.add(label_l,[(0,len(traces)),(1,size_of_run+1),(0,len(transitions))])
    lambda_jia=variablesGenerator.getFunction(label_l)
    positives=[]
    negatives=[]
    for j in range (0,len(traces)):
        for i in range (1,size_of_run+1):
            if len(traces[j])<(i):
                positives.append(lambda_jia([j,i,transitions.index(wait_transition)]))
                for a in transitions :
                    if a != wait_transition:
                        negatives.append(lambda_jia([j,i,transitions.index(a)]))
            else :
                for a in transitions:
                    if str(a)==traces[j][i-1]:
                        letterFound=True
                        positives.append(lambda_jia([j,i,transitions.index(a)]))
                    else :
                        negatives.append(lambda_jia([j,i,transitions.index(a)]))
    return And(positives,negatives,[]),traces
