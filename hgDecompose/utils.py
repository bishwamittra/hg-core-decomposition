import sys

sys.path.append("HyperNetX")
import hypernetx as hnx


def strong_subgraph(H, vertex_set):
    """
    Returns the strong sub-hypergraph of H induced by vertex_set
    Parameters
    ----------
    H: Hypernetx Hypergraph
    vertex_set: List/set of vertex label

    Returns
    -------
    Hypernetx Hypergraph object
        The strong sub-hypergraph induced by vertex_set
    """
    assert isinstance(H, hnx.Hypergraph)
    if not isinstance(vertex_set, set):
        X = set(vertex_set)
    else:
        X = vertex_set
    _tempdict = {}  # dictionary for induced edges
    for e_id, e_i in H.incidence_dict.items():
        set_e = set(e_i)
        if set_e.issubset(X):  # If an edge of the original hypergraph is a subset of the vertex set, add it
            _tempdict[e_id] = e_i
    return hnx.Hypergraph(_tempdict)


def get_number_of_nbrs(H, u):
    """
        Returns the number of neighbours of u in hypergraph H
        Parameters
        ----------
        H: Hypernetx Hypergraph
        u: a vertex label

        Returns
        -------
        Integer
            The number of neighbours of u in H
    """
    nbrs = H.neighbors(u)
    if nbrs is None:  # u is not in H
        return 0
    return len(nbrs)


def get_degree(H, u):
    degree = 0
    try:
        degree = H.degree(u)
    except Exception as e:
        # print(e)
        pass
    
    return degree

def get_nbrs(H, u):
    """
        Returns the neighbours of u in hypergraph H
        Parameters
        ----------
        H: Hypernetx Hypergraph
        u: a vertex label

        Returns
        -------
        List
            The neighbours of u in H. [] if u is not in H.
    """
    nbrs = H.neighbors(u)
    if nbrs is None:  # u is not in H
        return []
    return nbrs


def get_hg(dataset):
    H = None
    if(dataset == "default"):
        dic = {
            0: ('FN', 'TH'),
            1: ('TH', 'JV'),
            2: ('BM', 'FN', 'JA'),
            3: ('JV', 'JU', 'CH', 'BM'),
            4: ('JU', 'CH', 'BR', 'CN', 'CC', 'JV', 'BM'),
            5: ('TH', 'GP'),
            6: ('GP', 'MP'),
            7: ('MA', 'GP')
        }

        H = hnx.Hypergraph(dic)

    elif(dataset in ['enron', "syn", "bin_1", "bin_2", "bin_4", "bin_5", "congress", "contact"]):

        # file location
        dataset_to_filename = {
            # real
            "enron" : "data/datasets/real/Enron.hyp",
            "congress" : "data/datasets/real/congress-bills.hyp",
            "contact" : "data/datasets/real/contact-primary-school.hyp",
            
            # synthetic
            "syn" : "data/datasets/synthetic/syn.hyp",
            "bin_1" : "data/datasets/synthetic/binomial_5_100_4_0.200000_sample_1_iter_1.txt",
            "bin_2" : "data/datasets/synthetic/binomial_5_500_4_0.200000_sample_2_iter_1.txt",
            "bin_4" : "data/datasets/synthetic/binomial_5_100_3_0.200000_sample_4_iter_1.txt",
            "bin_5" : "data/datasets/synthetic/binomial_5_500_3_0.200000_sample_5_iter_1.txt",

        }

        
        # split by
        dataset_to_split = {
            "enron" : " ",
            "congress" : ",",
            "contact" : ",",
     
            "syn" : ",",
            "bin_1" : ",",
            "bin_2" : ",",
            "bin_4" : ",",
            "bin_5" : ",",

        }

        
        dic = {}
        # read from file
        with open(dataset_to_filename[dataset]) as f:
            lines = f.readlines()

            for idx, line in enumerate(lines):
                edge = tuple(line[:-1].split(dataset_to_split[dataset]))
                dic[idx] = edge

        H = hnx.Hypergraph(dic)

    else:
        raise RuntimeError(dataset + " is not defined or implemented yet")


    return H

