import numpy as np
import networkx as nx


class SearchTree:

    def __init__(self,net,i_m, f_m):
        self.net = net
        self.i_m = i_m
        self.f_m = f_m

    def compute_incidence_matrix(self,net):
        """
        We compute the incidence matrix of a Petri Net. It provides us with the firing requirements of a transition and its
        outcome. The matrix has rows equals to the number of places and columns equals to the the number of transition.
        As a result, the columns represent the firing information for each transition.
        :return: Numpy Matrix representing the incidence matrix.
        """
        incidence_matrix=np.zeros((len(self.net.places), len(self.net.transitions)))
        transitions=list(self.net.transitions)
        places=list(self.net.places)
        i=0
        while i<len(transitions):
            transition=transitions[i]
            for ingoing_arc in transition.in_arcs:
                #A transition consumes a token from its input places. Therefore, we have to subtract 1.
                incidence_matrix[places.index(ingoing_arc.source), i] -= ingoing_arc.weight
            for outgoing_arc in transition.out_arcs:
                #A transition produces one token for each of its "destination" places. Therefore, we have to add 1.
                incidence_matrix[places.index(outgoing_arc.target), i] +=outgoing_arc.weight
            i+=1
        return incidence_matrix

    def requirement_firing(self,net):
        """
        Computes how many tokens in which place are needed for a transition to fire.
        :param net: PM4Py Petri Net object
        :return: dictionary, whereby the keys are the transition, the values are a np.array which only marks where tokens are consumed for the respective transtion.
        """
        place_list=list(net.places)
        transition_dict={}
        for transition in net.transitions:
            temp=np.zeros(len(place_list))
            for arc in transition.in_arcs:
                temp[place_list.index(arc.source)]-=arc.weight
            transition_dict[transition]=temp
        return transition_dict

    def transition_firing_information(self,incidence_matrix, net):
        """
        We transform the information that is available in the incidence in a more readable form. This means that we
        contruct a dictionary, whereby a key is the name of a
        :param incidence_matrix: Incidence Matrix of a Petri Net
        :param net: Petri Net
        :return: Dictionary
        """
        firing_dict = {}
        i=0
        transitions=list(net.transitions)
        while i < len(transitions):
            firing_dict[transitions[i]] = incidence_matrix[: , i]
            i+=1
        return firing_dict

    def get_post_firing_marking(self,marking, firing_dict, requirement_dict):
        """
        We compute all possible markings after all fireable transition have been fired.
        :param marking: current marking
        :param firing_dict: Dictionary which provides us with the firing infomation whereby the key is the transition
        :param requirement_dict: Dict, whereby keys are transitions, key np.array that marks from which places amount of tokens is needed to fire
        :return: List of tuples, whereby the first element is the new marking, the second element is the transition that
        was used to reach the new marking.
        """
        firing_result = []
        for transition,requirement in requirement_dict.items():
            if all(np.greater_equal(marking, requirement.copy()*-1)):
                firing_result.append((marking+firing_dict[transition], transition))
        return firing_result
    
    def convert_marking(self, net, marking):
        """
        Since we are working with numpy arrays as representation of marking, we need no transform the initial marking
        to such a representation
        :param marking: Marking which is returned from discovery algorithms of PM4Py
        :return: numpy array that represents the initial marking
        """
        places=list(net.places)
        conv=np.zeros(len(places))
        i=0
        while i<len(places):
            if places[i] in marking:
                conv[i]=marking[places[i]]
            i+=1
        return conv

    def construct_reachability_graph(self,initial_marking, net, n):
        """
        We construct a reachability graph. Important to note is that we only expand nodes/marking, which can be reached in
        at most n not-tau transitions.
        :param initial_marking: inital marking of Petri Net, already coverted into a np.array representation
        :param net: Petri Net Object
        :param n: How many not tau transitions are considered
        :return: Networkx Multi-Directed Graph object
        """
        #compute incidence matrix
        incidence_matrix=self.compute_incidence_matrix(net)
    
        #compute requirment_dict
        requirement_dict=self.requirement_firing(net)

        #compute firing dict
        firing_dict=self.transition_firing_information(incidence_matrix,net)

        #output graph is a MulitDiGraph to represent self-loops and parallel edges
        graph=nx.MultiDiGraph()
        #the inital marking is node 0. We add the marking as data to the node
        j=0
        graph.add_node(j, marking=initial_marking, distance_from_source=0)

        #the reference table reveals the node-number a particular marking has
        reference_table={}
        reference_table[np.array2string(initial_marking)]=j

        #our set of nodes which has to be extended in the reachability graph
        work=set()
        work.add(j)
        j+=1
        while len(work)>0:
            #This set contains nodes that are during the computation of the graph faster reachable
            updated_nodes = set()
            #select a random marking and remove it from the work set
            mark=work.pop()
            #a list of marking that are reachble by firing transition which are currently available
            reachable_markings=self.get_post_firing_marking(graph.nodes[mark]['marking'], firing_dict, requirement_dict)
            for marking in reachable_markings:
                if np.array2string(marking[0]) not in reference_table:
                    #the first element of marking represent the numpy representation of that marking, the second the
                    # transition that was taken
                    #If the marking is not in the graph yet, we add it
                    reference_table[np.array2string(marking[0])]=j
                    graph.add_node(j, marking=marking[0])
                    if marking[1].label == None:
                        #if the transition that fires, we need an edge of weight 0. This is done because we only care about
                        # the projected run/trace at the end
                        graph.add_edge(mark, j, transition=marking[1], weight=0)
                        graph.nodes[j]['distance_from_source'] = graph.nodes[mark]['distance_from_source']
                    else:
                        #If a non-tau transition fires, we need a weight of 1
                        graph.add_edge(mark,j, transition=marking[1], weight=1)
                        graph.nodes[j]['distance_from_source'] = graph.nodes[mark]['distance_from_source']+1
                    if graph.nodes[j]['distance_from_source']<=n:
                        #only if the distance is not exceed, we add the node to our work set to expand it
                        work.add(j)
                    j+=1
                else:
                    #The marking is in the graph. However, we have to add the edge.
                    observerable_marking=reference_table[np.array2string(marking[0])]
                    if marking[1].label == None:
                        graph.add_edge(mark, observerable_marking, transition=marking[1], weight=0)
                    else:
                        graph.add_edge(mark, observerable_marking, transition=marking[1], weight=1)
                    min=np.inf
                    #since there might be multiple arcs beetween states, we want to get the minimum weight to have a minimum distance between these
                    for arc in graph.get_edge_data(mark, observerable_marking):
                        if graph.get_edge_data(mark, observerable_marking)[arc]['weight']<min:
                            min=graph.get_edge_data(mark, observerable_marking)[arc]['weight']
                    distance_from_source_over_m=graph.nodes[mark]['distance_from_source']+min
                    if distance_from_source_over_m<graph.nodes[observerable_marking]['distance_from_source']:
                        graph.nodes[observerable_marking]['distance_from_source']=distance_from_source_over_m
                        updated_nodes.add((observerable_marking, graph.nodes[observerable_marking]['distance_from_source']-distance_from_source_over_m))
            for el in updated_nodes:
                #since we have an directed graph, bfs returns us every successor and even their sucessors. These
                #are the nodes which distance have to be updated due a shorter path
                edges = nx.bfs_edges(graph, el[0])
                for (v,w) in edges:
                    min = np.inf
                    #since there might be multiple arcs beetween states, we want to get the minimum weight to have a minimum distance between these
                    for arc in graph.get_edge_data(v, w):
                        if graph.get_edge_data(v, w)[arc]['weight'] < min:
                            min = graph.get_edge_data(v, w)[arc]['weight']
                    if graph.nodes[v]['distance_from_source']+min<graph.nodes[w]['distance_from_source']:
                        #if there is shorter path than before, we have to chek if the sucessor had previously a distance greater than n
                        if graph.nodes[w]['distance_from_source'] > n and graph.nodes[v]['distance_from_source']+min<n:
                            # If the "new" distance after eding edges/nodes is smaller and the old distance exceed our limit,
                            # we need to consider the node in the work set for expansion
                            work.add(w)
                        #We have to update the distance value due a shorter path
                        graph.nodes[w]['distance_from_source'] =graph.nodes[v]['distance_from_source']+min
        return graph

    def annotate_distance_to_sink(self,graph,final_marking):
        """
        Each node gets annotated with the the distance to the final marking. Distance means the number of non-tau
        transitions to reach the final marking
        :param graph: Reachability graph, networkx MultiDiGraph object
        :return: Networkx MultiDiGraph whereby each node gets an additional attribute 'distance_to_sink'
        """
        for node in graph.nodes:            
            if np.array_equal(graph.nodes[node]['marking'],final_marking):
                sink=node
                break
        for node in graph.nodes:
            #it is possible that the final marking cannot be reached from a node
            try:
                graph.nodes[node]['distance_to_sink'] = nx.shortest_path_length(graph, source=node, target=sink, weight='weight')
            except nx.NetworkXNoPath:
                #if the final marking cannot be reached, we remove the node from the reachbility graph
                graph.remove_node(node)
        return graph

    def apply(self,depth):#,net, i_m, f_m, 
        """
        Apply method. Use from outside to get an reachbility graph.
        The reachability graph consist of the following attributes:
        For nodes:
        marking: np.arrray representation of the marking
        distance_from_source: number of non-tau transitions to get to the marking of the node, starting from the initial
        distance_to_sink: number of non-tau transitions to get to the final marking
        For edges:
        transition: transition object of the given Petri Net that is fired
        weight: If a tau-tranisiton has fired, the weight is 0; else 1. Since we are interested in the projected trace,
        we need to distinguish.
        :param net: PM4Py Petri Net object
        :param i_m: initial marking of the Petri Net object
        :param f_m: final marking of the Petri Net object
        :param depth: Depth of the reachability graph, meaning, maximum of non-tau transitions to the final marking
        :return: 3-tupel, consisting of two nodes and a networkx MultiDigraph object. The first node contains the initial
        marking, the second node contains the final marking
        """
        initial_marking = self.convert_marking(self.net,self.i_m)
        final_marking = self.convert_marking(self.net,self.f_m)
        reachability_graph =self.construct_reachability_graph(initial_marking, self.net, depth)
        reachability_graph = self.annotate_distance_to_sink(reachability_graph, final_marking)
        #Due the construction of the graph, we know that the initial marking is observerable in node 0
        inital_marking_node = 0
        for node in reachability_graph.nodes:
            if np.array_equal(reachability_graph.nodes[node]['marking'], final_marking):
                final_marking_node = node
        return (inital_marking_node, final_marking_node, reachability_graph)
