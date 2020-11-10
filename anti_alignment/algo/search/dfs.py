import networkx as nx

class DepthFirstSearch:
    def __init__(self,G,i_m,f_m):
        self.G = G
        self.i_m= i_m
        self.f_m =f_m        

    def findPaths(self,n):
        """
        finds all correct paths of length n in the graph
        
        this function returns all paths of length n that begin in the initial
        marking and end in the final marking. The paths then contain the labels that
        are present on the edges visited on the path
        
    	:param graph G: networkx MultiDiGraph G
    	:param marking im: initial petri net marking im
    	:param marking em: end/final petri net marking em
    	:param int n: path length of alignments                 
    	:return: all paths of length n as an array containing the cases
    	that are present on the edges takes by the algorithm
        
        :rtype: arr
    	"""
        paths=self.findPathsRecursive(self.i_m,n)    
        anti_alignments=[]
        #only paths that end in the final marking are returned
        for path in paths:
            
            #final marking is removed from the path since it is only used to check
            #if its a valid path
            if path[-1]==self.f_m:
                del path[-1]       
                alignment=path#AntiAlignment(path)             
                anti_alignments.append(alignment)  
        #seperate edge labels and nodes visited
        alignment_tuples=[]
        for alignment in anti_alignments:
            nodes=[]
            labels=[]
            for node,label,next_node in alignment:
                labels.append(label)
                if(len(nodes)==0):
                    nodes.append(node)
                elif(nodes[-1]!=node):
                    nodes.append(node)
                nodes.append(next_node)
            alignment_tuples.append((labels,nodes))    
           # alignment_tuples.append(tuple([labels,nodes]))
        return alignment_tuples

    def findPathsRecursive(self,u,n):
        """
        finds all paths of length n in the graph

        this method does an edge depth first search through the graph of length an, considering
    all edges staring from the given node u, in the form of (node,edge,next_node) for all edges

        :param graph G: networkx MultiDiGraph G
        :param node u: the current node u
        :param int n: search depth at the current recursion point
        :return: all paths of length n
        """        
        #if we cant reach the final marking anymore we can abort search
        if u==self.f_m:
            #added the final node to check if the last transition takes end in the final marking
            return [[u]]
        if self.G.nodes[u]['distance_to_sink']>n:
            return []
        paths = []
        for neighbor in self.G.neighbors(u):
            rec= n-1
            for k in range(len(self.G.get_edge_data(u,neighbor))):
            #a tau transition is not counted in the path length, a tau transition has weight 0
                path_weight=self.G.get_edge_data(u,neighbor)[k]["weight"]
                if path_weight==0:
                    rec=rec+1
                if rec<0:
                    #added the final node to check if the last transition takes end in the final marking
                    return  []
                for path in self.findPathsRecursive(neighbor,rec):
                    #check if the last transition was a tau trasition
                    #tau transitions are not added to the path
                    if path_weight!=0:
                        #iterate through all edges between two nodes since there can be multiple
                        #trasitions between two nodes      
                    
                        paths.append([(u,self.G.get_edge_data(u,neighbor)[k]["transition"].label,neighbor)]+path)
                    #paths.append((u,[G.get_edge_data(u,neighbor)[k]["transition"].label],neighbor)+path)
                    else:
                        paths.append(path)
        return paths
    
    def find_Path_for_Trace(self,trace):
        return self.find_Path_for_Trace_Recursive(self.i_m,trace)
    
    def find_Path_for_Trace_Recursive(self,u,trace):
        if(u==self.f_m):
            return [[u]]
        paths=[]
        for neighbor in self.G.neighbors(u):
            for k in range(len(self.G.get_edge_data(u,neighbor))):
                path_weight=self.G.get_edge_data(u,neighbor)[k]["weight"]      
                mytrace=trace
                if path_weight!=0:
                        if (len(trace)==0 or self.G.get_edge_data(u,neighbor)[k]["transition"].label!=trace[0]):
                            continue
                        else:
                           mytrace=trace[1:]
                
                for path in self.find_Path_for_Trace_Recursive(neighbor,mytrace):
                        paths.append([u]+path)
                        #iterate through all edges between two nodes since there can be multiple
                        #trasitions between two nodes      
                                   
        return paths