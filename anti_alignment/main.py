# TBA, under construction
def main():
    print("<---WELCOME to ANTI ALIGNMENT WORLD--->")
    print("-----------------")
    print("-----------------")
    print("Start entering your log information")
    type = input("CSV or XES ?")
    if type== 'CSV' or 'csv' or 'XES' or 'xes':
        logtype = input()
    else:
        print("Current format not supported")
    pathlog = input("Your log path:")
    print("Start entering your model information")
    pathnet = input("Your petrinet path:")

    #places = input("No of places in petrinet model")
    #transitions = input("No of transitions in petrinet model")
    #arcs = input("No of arcs ")

    filtered_logobject = InputHandler(pathnet,pathlog,logtype)
    input_log = filtered_logobject.filtering_traces()
    print(input_log)
    #continue working with input log


if __name__ == "__main__":
    main()



# def apply(log,model,distance_function,net, initial_marking, final_marking,quality_dimensions):
#     distance_factory=None
#     if distance_function=="levenshtein":
#         distance_factory=LevenshteinAlignments()
#     elif distance_function=="TBA":
#         print("unimplemented path")
#         return
#     else:
#         print("unknown parameter value")
#         return

    # anti_alignments=distance_factory.get_anti_alignment_dfs_brute_force(log,net, initial_marking, final_marking)