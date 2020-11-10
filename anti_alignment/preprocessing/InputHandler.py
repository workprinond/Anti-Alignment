
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri.petrinet import PetriNet,Marking
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.petri import utils
from pm4py.objects.petri.importer import importer as pnml_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
import os


class InputHandler:
    """
    Class for Input Handler contains all methods necessary for the user to create an object of filtered traces
    Instance Attributes:
        pathnet: Petrinet path value of the InputHandler object
        pathlog: Log path of the InputHandler object
        logtype: CSV or IEEE type log InputHandler object
    """

    def __init__(self,pathnet,pathlog,logtype):
        """
        Instantiates InputHandler object
        :param pathnet: Path of the petrinet
        :param pathlog: Path of the log
        :param significance: Type of the log (CSV or XES)
        """
        self.pathnet = pathnet
        self.pathlog = pathlog
        self.logtype = logtype

    def ieee_xes_loghandler(self):
        """
        Loads the XES type log from the path
        :return: The log
        """
        event_log = xes_importer.apply(self.pathlog)
        return event_log

    def csv_loghandler(self):
        """
        Loads the CSV type log from the path
        :return: The log
        """
        log_csv = pd.read_csv(self.pathlog, sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('<timestamp_column>')
        event_log = log_converter.apply(log_csv)
        return event_log

    def petrinethandler(self):
        """
        Loads the pnml file from the path
        :return: The petrinet with its initial and final marking
        """
        petrinet, initial_marking, final_marking = pnml_importer.apply(self.pathnet)
        return petrinet, initial_marking, final_marking

    def filtering_traces(self):
        """
        Calculates the filtered traces which fits the model
        :return: The filtered traces in a list
        """
        newLog = []
        if (self.logtype) == 'CSV' or 'csv':
            log = self.csv_loghandler()
        else:
            log = self.ieee_xes_loghandler()
        net = self.petrinethandler()
        replayed_traces = token_replay.apply(log, net[0], net[1], net[2])
        for i in range(0, len(log)):
            if replayed_traces[i].get('trace_is_fit') == False:
                continue
            newLog = newLog + log[i]

        return newLog



# to be discussed and then consider to keep this or not
    def petrinetcreator(self, places,transitions,arcs):
        net = PetriNet("new_petri_net")

        source = PetriNet.Place("source")
        sink = PetriNet.Place("sink")
        for i in range(1,places+1):
            p = PetriNet.Place("p_"+str(i))
            net.places.add(p)
        net.places.add(source)
        net.places.add(sink)

        for i in range(1,transitions+1):
            t = PetriNet.Transition("name_"+ str(i), "label_"+str(i))
            net.transitions.add(t)

        for i in range(1,len(arcs+1)):
            arc = arcs[i].split()
            utils.add_arc_from_to(arc[0], arc[1], net)

        initial_marking = Marking()
        initial_marking[source] = 1
        final_marking = Marking()
        final_marking[sink] = 1

        return net
















