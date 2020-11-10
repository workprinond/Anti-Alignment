from da4py.main.utils.formulas import Or, And
def petri_net_to_SAT(net, m0, mf, variablesGenerator, size_of_run, reach_final, label_m="m_ip", label_t="tau_it",
                     silent_transition=None,transitions=None):
    '''
    This function returns the SAT formulas of a petrinet given label of variables, size_of_run
    :param net: petri net of the librairie pm4py
    :param m0: initial marking
    :param mf: final marking
    :param variablesgenerator: @see darksider4py.variablesGenerator
    :param label_m (string) : name of marking boolean variables per instant i and place p
    :param label_t (string) : name of place boolean variables per instant i and transition t
    :param size_of_run (int) : max instant i
    :param reach_final (bool) : True for reaching final marking
    :param sigma (list of char) : transition name
    :return: a boolean formulas
    '''

    # we need a ordered list to get int per place/transition (for the variablesgenerator)
    if transitions is None :
        transitions = [t for t in net.transitions]
    silent_transitions=[t for t in net.transitions if t.label==silent_transition]
    places = [p for p in net.places]

    # we create the number of variables needed for the markings
    variablesGenerator.add(label_m, [(0, size_of_run + 1), (0, len(places))])

    # we create the number of variables needed for the transitions
    variablesGenerator.add(label_t, [(1, size_of_run + 1), (0, len(transitions))])

    return (is_run(size_of_run, places, transitions, m0, mf, variablesGenerator.getFunction(label_m),
                   variablesGenerator.getFunction(label_t), reach_final), places, transitions, silent_transitions)