from threading import Thread
from SAT.formula import And,Or
import itertools
def edit_distance(artefact, transitions, silent_transitions, vars, nbTraces, size_of_run,
                                   wait_transition, max_d):
    '''
    Generic function of the edit distance.
    :param artefact (string) : one of the global variables (MULTI_ALIGNMENT, ANTI_ALIGNMENT and EXACT_ALIGNMENT)
    :param transitions (list) : the transitions
    :param silent_transitions (list) : the silent transitions
    :param variables (variablesGenerator) : to creates the variables numbers
    :param nbTraces (int) : number of traces
    :param size_of_run (int) : maximal size of run
    :param wait_transition (transition) : end of words
    :param max_d (int) : heuristic because formula are too large
    :return: formula
    '''
    # gets the right functions
    initialisation_function = DICT_OF_EDIT_INIT[artefact]
    recursion_function = DICT_OF_EDIT_RECURSIONS[artefact]
    # add djiid boolean variables. See paper _Encoding Conformance Checking Artefacts in SAT_ for more details
    vars.add(BOOLEAN_VAR_EDIT_DISTANCE,
             [(0, nbTraces), (0, size_of_run + 1), (0, size_of_run + 1), (0, max_d + 1)])

    # some simple parallelism
    formulas = []
    threads = []
    for i in range(0, NB_MAX_THREADS):
        process = Thread(target=aux_for_threading,
                         args=[formulas, recursion_function, initialisation_function, transitions, silent_transitions,
                               vars, size_of_run, wait_transition,
                               max_d, i, nbTraces])
        process.start()
        threads.append(process)
    for process in threads:
        process.join()

    return formulas

def levenshtein(s, t):
    if len(s) == 0 :
        return len(t)
    if len(t) == 0 :
        return len(s)
    if s[-1] in ["w",None,"tau"]:
        return levenshtein(s[:-1], t)
    if t[-1] in ["w",None,"tau"] :
        return levenshtein(s, t[:1])
    if s[-1] == t[-1] :
        return levenshtein(s[:-1], t[:-1])
    else:
        return min(levenshtein(s[:-1], t)+1,
               levenshtein(s, t[:-1])+1)