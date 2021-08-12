import sys

sys.path.append("HyperNetX")
import hypernetx as hnx


class Hypergraph:
    """ 
    Our own hypergraph representation class. 
    We store hyperedge list in compressed format using two things- 1) e_indices (a dict) 2) e_nodes (a list)
    Although edge-centric queries (e.g. edge enumeration) are facilitated in this way, node-centric queries are not convenient.
    To support node-centric queries, we also maintain incidence dictionary inc_dict (key = v_ids, values = incident edge ids)
    """

    def __init__(self, _edgedict=None):
        if _edgedict is None:  # Returns an empty Hypergraph
            return
        self.e_indices = {}  # (position, position+edge_size) of edge e in e_nodes list
        self.e_nodes = []  # flattened edge list
        self.inc_dict = {}  # key: nodeid, value = ids of incident edges (set)
        # degree pre-compute => degree_dict or len_incedge = {}
        self.degree_dict = {}
        self.init_nbrsize = {} # initial nbrhood sizes. can be precomputed.
        self.init_nbr = {}
        self.precomputedlb2 = {}

        self.i = 0
        for e_id, e in _edgedict.items():
            _len = len(e)
            self.e_indices[e_id] = (self.i, self.i + _len)
            for v in e:
                self.e_nodes.append(v)
                if v not in self.inc_dict:
                    self.inc_dict[v] = set()  # create incident edge entry for v
                self.inc_dict[v].add(e_id)  # incident edge update
                self.degree_dict[v] = self.degree_dict.get(v, 0) + 1  # degree update
                nbr_v = self.init_nbr.get(v, set()).union(e)
                nbr_v.remove(v)
                self.init_nbrsize[v] = len(nbr_v)  # neighbourhood length update
                self.init_nbr[v] = nbr_v  # neighbourbood set update
            self.i += _len

        for v in self.inc_dict.keys():
            for u in self.init_nbr[v]:
                self.precomputedlb2[v] = min(self.precomputedlb2.get(v, self.init_nbrsize[v]), self.init_nbrsize[u] - 1)

    def get_init_nbr(self, v):
        return self.init_nbr[v]

    def get_init_nbrlen(self, v):
        return self.init_nbrsize[v]

    def add_edge(self, e_id, e_nodes):
        """ Add an edge to the hypergraph. It does not check repeated edge."""
        _len = len(e_nodes)
        self.e_indices[e_id] = (self.i, self.i + _len)
        for v in e_nodes:
            self.e_nodes.append(v)
            if v not in self.inc_dict:
                self.inc_dict[v] = set()  # create incident edge entry for v
            self.inc_dict[v].add(e_id)  # incident edge update
            self.degree_dict[v] = self.degree_dict.get(v, 0) + 1  # degree update

        self.i += _len

    def get_edge_byindex(self, e_id):
        """ Return edge by edge_id """
        e_start, e_end = self.e_indices[e_id]
        return self.e_nodes[e_start:e_end]

    def edge_iterator(self):
        """ returns: iterator """
        for e_id in self.e_indices.keys():
            yield self.get_edge_byindex(e_id)

    def node_iterator(self):
        """ returns: iterator """
        for v_id in self.inc_dict.keys():
            yield v_id

    def nodes(self):
        """ returns: list of vertices """
        return [v for v in self.node_iterator()]

    def edges(self):
        """ returns: list of edges (each edge is a list of vertex ids) """
        return [e for e in self.edge_iterator()]

    def degree(self, u):
        """ returns: integer """
        # assert (len(self.inc_dict.get(u,[])) == self.degree_dict[u])
        return self.degree_dict.get(u, 0)

    def dim(self, e):
        """ returns: integer """
        return len(e) - 1

    def neighbors(self, v):
        return [u for u in self.neighbors_iterator(v)]

    def get_number_of_nbrs(self, u):
        return len(self.neighbors(u))

    def neighbors_iterator(self, v):
        """ Returns the set of neighbours of v.
            implements a traversal from vertex v to each of its neighbours in contrast to set in neighbors(). 
            It also returns an iterator. So it avoids creating the neighborhood list explicitely.
            Overall complexity: O(d(v) * |e_max|), where e_max = largest hyperedge 
        """
        incident_edges = self.inc_dict.get(v, None)  # {O(1)}
        if incident_edges:
            visited_dict = {}
            for e_id in incident_edges:  # { O(d(v)) }
                for u in self.get_edge_byindex(e_id):  # { O(|e|)}
                    if u != v:
                        if not visited_dict.get(u, False):
                            visited_dict[u] = True
                            yield u
        else:
            return

    def removeV_transform(self, v, verbose=False):
        """ removes input vertex v and transforms this hypergraph into a sub-hypergraph strongly induced by V\{v}
        Here we do not maintain nbr and len_nbr dictionaries.
        """
        incident_eids = set()  # set of edge_ids incident on v
        for e_id in self.inc_dict.get(v, []):
            incident_eids.add(e_id)

        if verbose:
            print("incident edges on ",v," : ", incident_eids)

        # Update incident edges and degree of every nbr of v
        for u in self.neighbors_iterator(v): # traverse over neighbours of v
            if verbose:
                print('traversing nbr: ',u)
            self.inc_dict[u] -= incident_eids # remove v's incident edges from u's incident edges.
            self.degree_dict[u] = len(self.inc_dict.get(u, []))

        if v in self.inc_dict:
            del self.inc_dict[v]

        if v in self.degree_dict:
            del self.degree_dict[v]

    # def removeV_transform(self, v, verbose=False):
    #     """ removes input vertex v and transforms this hypergraph into a sub-hypergraph strongly induced by V\{v} """
    #
    #     # inc_on_v = self.inc_dict.get(v,[]) # List of incident edges(v) { o(1) }
    #     # if len(inc_on_v): # If 0 incident edges, the hypergraph won't need any update.
    #     # for e_id in inc_on_v: # For every edges incident on v { O(d(v)) }
    #     # spos_e, epos_e = self.e_indices[e_id] # { o(1) }
    #     # del self.e_indices[e_id] # Delete that edge (to be precise, we remove its index only) { o(1) }
    #     # # Check if the neighbours of v in e needs to be removed as well.
    #     # for nbrv_in_e in self.e_nodes[spos_e:epos_e]: # For every u in e { O(|e_max|) < O(N) }
    #     #     if nbrv_in_e in self.inc_dict:
    #     #         if len(self.inc_dict[nbrv_in_e]) <= 1: # If u has no edge except e incident on it
    #     #             del self.inc_dict[nbrv_in_e] # Remove u
    #     #         else:
    #     #             self.inc_dict[nbrv_in_e].remove(e_id) # Otherwise, update the incidence entry of u
    #
    #     incident_edges = self.inc_dict.get(v, None)  # {O(1)}
    #     if (verbose):
    #         print(incident_edges)
    #     if incident_edges:
    #         visited_dict = {}
    #         # isolated_vertices = set([v]) # the set of nbrs of v who became isolated after removal of v. They can not be in any edge.
    #         for e_id in incident_edges:  # For every incident edge e { O(d(v)) }
    #             if (verbose):
    #                 print('incident edge: ', e_id)
    #             if e_id in self.e_indices:
    #                 e = self.get_edge_byindex(e_id)
    #                 for u in e:  # For every node u \in e { O(|e|)}
    #                     if u != v:  # If u != v
    #                         if (verbose):
    #                             print('visiting ', u)
    #                         if not visited_dict.get(u, False):  # { O(1) }
    #                             visited_dict[u] = True  # { O(1) }
    #                             # self.nbr[u].remove(v) # v is no more a neighbour of u, because u will be deleted
    #                             # if len(self.inc_dict[u]) <= 1: # If u has no edge except e incident on it {O (d(nbr(v)))}
    #                             # So a neighbour of the vertex we want to delete has degree = 1
    #                             if self.degree_dict[u] <= 1:
    #                                 if (verbose):
    #                                     print('removing incident edge entry of ', u)
    #                                 del self.inc_dict[u]  # Remove u, because its deg became 0. { O(1) }
    #
    #                             else:
    #                                 if (verbose):
    #                                     print('removing ', e_id, ' from ', u, ' \'s incident edges')
    #                                 self.inc_dict[u].remove(
    #                                     e_id)  # Otherwise, update the incidence entry of u { O (1) }
    #
    #                             self.degree_dict[u] -= 1  # degree of u decreases by 1
    #                             if self.degree_dict[u] == 0:
    #                                 if (verbose):
    #                                     print(u, ' : a 0-degree vertex')
    #                                 # isolated_vertices.add(u) # keep track of isolated vertices.
    #                                 # self.nbr[v].remove(u) # keep track of non-isolated vertices.
    #                                 del self.nbr[u]
    #                                 del self.len_nbr_dict[u]
    #                                 del self.degree_dict[u]
    #                 set_e = set(e)
    #                 for u in self.nbr[v]:
    #                     if u in self.nbr:
    #                         self.nbr[u] -= set_e  # Remove e from nbrs of v.
    #                     if u in self.len_nbr_dict:
    #                         self.len_nbr_dict[u] = len(self.nbr.get(u, set()))
    #
    #                 # for u in isolated_vertices:
    #                 #     del self.degree_dict[u]
    #
    #                 if (verbose):
    #                     print('deleting ', e_id)
    #                 del self.e_indices[e_id]
    #
    #         del self.inc_dict[v]
    #         del self.nbr[v]
    #         del self.len_nbr_dict[v]
    #         del self.degree_dict[v]

    # def strong_subgraph(self, vertex_list):
    #     """ returns: Hypergraph object. """
    #     H = Hypergraph()
    #     e_indices = {}  # (position, edge_size) of edge e in e_nodes list
    #     e_nodes = []  # flattened edge list
    #     inc_dict = {}
    #     H.i = 0
    #
    #     # print('inc_dict: ',self.inc_dict.items())
    #     # print('e_indices: ',self.e_indices.items())
    #     # print('e_nodes: ',self.e_nodes)
    #
    #     for v in vertex_list:
    #         for e_id in self.inc_dict.get(v, []):
    #             if e_id not in e_indices:
    #                 e_start, e_end = self.e_indices[e_id]
    #                 flag = True
    #                 e = self.e_nodes[e_start:e_end]
    #                 for u in e:
    #                     if u not in vertex_list:
    #                         flag = False
    #                         break
    #                 if flag:
    #                     e_nodes += e
    #                     _lene = (e_end - e_start)
    #                     e_indices[e_id] = (H.i, H.i + _lene)
    #                     inc_dict[v] = inc_dict.get(v, []) + [e_id]
    #                     H.i += _lene
    #             else:
    #                 inc_dict[v] = inc_dict.get(v, []) + [e_id]
    #
    #     # print('After: ','inc_dict = ',inc_dict.items(),'\n','e_indices = ',e_indices,'\n',' e_nodes = ',e_nodes)
    #     H.e_nodes = e_nodes
    #     H.inc_dict = inc_dict
    #     H.e_indices = e_indices
    #     return H
    #
    # def strong_subgraph2(self, vertex_list):
    #     """
    #     Another implementation of strong_subgraph
    #     returns: Hypergraph object.
    #     """
    #     H = Hypergraph()
    #     e_indices = {}  # (position, edge_size) of edge e in e_nodes list
    #     e_nodes = []  # flattened edge list
    #     inc_dict = {}
    #     H.i = 0
    #
    #     # print('inc_dict: ',self.inc_dict.items())
    #     # print('e_indices: ',self.e_indices.items())
    #     # print('e_nodes: ',self.e_nodes)
    #
    #     # for v in vertex_list:
    #     #     for e_id in self.inc_dict.get(v,[]):
    #     #         if e_id not in e_indices:
    #     #             e_start, e_end = self.e_indices[e_id]
    #     #             flag = True
    #     #             e = self.e_nodes[e_start:e_end]
    #     #             for u in e:
    #     #                 if u not in vertex_list:
    #     #                     flag = False
    #     #                     break
    #     #             if flag:
    #     #                 e_nodes += e
    #     #                 _lene = (e_end - e_start)
    #     #                 e_indices[e_id] = (H.i, H.i+ _lene)
    #     #                 inc_dict[v] = inc_dict.get(v,[])+[e_id]
    #     #                 H.i+= _lene
    #     #         else:
    #     #             inc_dict[v] = inc_dict.get(v,[])+[e_id]
    #
    #     for e_id in self.e_indices:
    #         flag = True
    #         e = self.get_edge_byindex(e_id)
    #         for u in e:
    #             if u not in vertex_list:
    #                 flag = False
    #                 break
    #         if flag:
    #             e_start, e_end = self.e_indices[e_id]
    #             e_nodes += e
    #             _lene = (e_end - e_start)
    #             e_indices[e_id] = (H.i, H.i + _lene)
    #             H.i += _lene
    #
    #     for e_id in e_indices:
    #         e = self.get_edge_byindex(e_id)
    #         for u in e:
    #             inc_dict[u] = inc_dict.get(u, []) + [e_id]
    #
    #     # print('After: ','inc_dict = ',inc_dict.items(),'\n','e_indices = ',e_indices,'\n',' e_nodes = ',e_nodes)
    #     H.e_nodes = e_nodes
    #     H.inc_dict = inc_dict
    #     H.e_indices = e_indices
    #     return H

    def get_hnx_format(self):
        _tempH = {}
        for e_id in self.e_indices.keys():
            _tempH[e_id] = self.get_edge_byindex(e_id)
        return hnx.Hypergraph(_tempH)

    # def weak_subgraph(self, vertex_list):
    #     """ returns: Hypergraph object. """
    #     pass