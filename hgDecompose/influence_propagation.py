import random
import numpy as np
from copy import deepcopy
from multiprocessing import Pool


def propagate_for_all_vertices(H, core, num_vertex_per_core = 100, top_k = 100,  p = 0.5, num_iterations = 100, verbose=True):


    
    result = {} # Entry is a core number. value is a list of percentages of the infected population for all vertices with the same core number


    core_to_vertex_map = {}
    distinct_core_numbers = []
    for v in core:
        if(core[v] not in core_to_vertex_map):
            core_to_vertex_map[core[v]] = [v]
            distinct_core_numbers.append(core[v])
        else:
            core_to_vertex_map[core[v]].append(v)

    distinct_core_numbers.sort(reverse=True)

    for core_number in distinct_core_numbers[:top_k]:
        for v in random.choices(core_to_vertex_map[core_number], k=num_vertex_per_core):
            if(core_number not in result):
                result[core_number] = [propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0]]
            else:
                result[core_number].append(propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0])
            
    #TODO: Parallelize this loop
    # core_v_list = [] 
    # core_numbers = []
    # for core_number in distinct_core_numbers[:top_k]:
    #     for v in random.choices(core_to_vertex_map[core_number], k=num_vertex_per_core):
    #         core_v_list.append((H,v,p,num_iterations,verbose))
    #         core_numbers.append(core_number)
    
    
    # with Pool(processes=8) as pool:
    #     pool_results = pool.map(propagate, core_v_list)
    #     # for x in pool.map(propagate, core_v_list):
    #     #     pool_results.append(x[0])
    #     pool.join()

    # for i, core_number in enumerate(core_numbers):
    #     if(core_number not in result):
    #         result[core_number] = pool_results[i][0]
    #     else:
    #         result[core_number].append(pool_results[i][0])
    #     # if(core_number not in result):
    #     #     result[core_number] = [propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0]]
    #     # else:
    #     #     result[core_number].append(propagate(H, starting_vertex=v, p = p, num_iterations = num_iterations, verbose = verbose)[0])


    return result


def run_intervention_exp(H, core, p = 0.5, verbose = False):
    # print(core)
    deleted_ids = [2693,2804,3865,1547,2102,2960,2537,3446,2120,2673]
    max_core_number = -1
    for v in core:
        if(max_core_number < core[v]):
            max_core_number = core[v]
        
    # print(max_core_number)

    nodes_with_max_core = []
    for v in core:
        if(core[v] == max_core_number):
            nodes_with_max_core.append(v)
        
    
    all_nodes = H.nodes()
    result = {}
    # print(all_nodes)
    strongly_induced_eids = H.get_stronglyinduced_edgeIds(nodes_with_max_core)
    if verbose:
        print('# potential edges to delete: ',len(strongly_induced_eids))
    # for eid in ['nill'] +  strongly_induced_eids:
    for eid in ['nill'] + random.choices(strongly_induced_eids, k = 10):
        print(eid)
    # for eid in [3,4]:
        temp_H = deepcopy(H)
        if(eid != "nill"):
            temp_H.del_edge(eid)
        temp_core = {}
        for node in temp_H.nodes():
            temp_core[node] = core[node]
        # print(eid, H.get_edge_byindex(eid), temp_H.nodes(), len(temp_H.nodes()))
        result[eid] = propagate_for_all_vertices(temp_H, temp_core, p = p, verbose=verbose)
    
    # print(result)

    return result



def propagate_for_random_seeds(H, core, seed_size = 1000, p = 0.5, num_iterations = 100, verbose = False):

    # print(core)
    result = {}
    # 
    for v in random.choices(H.nodes(), k = seed_size):
        # print(v)
        _, timestep_of_infection = propagate(H, starting_vertex = v, p = p, num_iterations = num_iterations, verbose = False)
        # print(timestep_of_infection)
        # print()
        for u in timestep_of_infection:
            if(core[u] not in result):
                result[core[u]] = [timestep_of_infection[u]]
            else:
                result[core[u]].append(timestep_of_infection[u])

    # print(result)

    return result



def propagate(H, starting_vertex, p = 0.5, num_iterations = 10, verbose=True):
    """
    """
    
    timestep_of_infection = {}
    len_nodes = H.get_N()
    for v in H.nodes():
        timestep_of_infection[v] = num_iterations + 1
    suscepted = H.nodes()
    suscepted.remove(starting_vertex)
    infected = [starting_vertex]
    timestep_of_infection[starting_vertex] = 0
    recovered = []

    for i in range(num_iterations):
        if(verbose):
            print('\n\n\nIteration:', i)
            # print("infected:", infected)
            # print("recovered:", recovered)
            # print("suscepted:", suscepted)
            print()
        
        if(len(infected) == 0):
            # if(verbose):
            #     print("No more propagation is possible")
            break
        
        
        new_infected = []
        new_recovered = []    
        for v in infected:
            # if(verbose):
            #     print("\nPorpagating for", v)
            for u in H.neighbors(v):
                if(u in suscepted):
                    if(random.random() <= p):
                        # if(verbose):
                        #     print(v, "->", u)
                        new_infected.append(u)
                        timestep_of_infection[u] = i + 1
                        suscepted.remove(u)
                    else:
                        # if(verbose):
                        #     print(v, "->", u, "not propagated")
                        pass
                # else:
                #     if(verbose):
                #         print(u, "is already either infected or recovered")
            new_recovered.append(v)


        infected += new_infected
        recovered += new_recovered
        for v in new_recovered:
            infected.remove(v)
    
    return 1 - float(len(suscepted) / H.get_N()), timestep_of_infection
