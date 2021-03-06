import numpy as np
import torch as th
import dgl 
import dgl.function as fn

import time
from tqdm import tqdm
import traceback
from functools import wraps
from _thread import start_new_thread
import torch.multiprocessing as mp
mp.set_start_method("spawn", force=True)

# According to https://github.com/pytorch/pytorch/issues/17199, this decorator
# is necessary to make fork() and openmp work together.
def thread_wrapped_func(func):
    """
    Wraps a process entry point to make it work with OpenMP.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        queue = mp.Queue()
        def _queue_result():
            exception, trace, res = None, None, None
            try:
                res = func(*args, **kwargs)
            except Exception as e:
                exception = e
                trace = traceback.format_exc()
            queue.put((res, exception, trace))

        start_new_thread(_queue_result, ())
        result, exception, trace = queue.get()
        if exception is None:
            return result
        else:
            assert isinstance(exception, Exception)
            raise exception.__class__(trace)
    return decorated_function

def MinMaxScaling(x, dim=0):
    dist = x.max(dim=dim, keepdim=True)[0] - x.min(dim=dim, keepdim=True)[0]
    x = (x - x.min(dim=dim, keepdim=True)[0]) / (dist + 1e-7)
    return x

def prune_feature(old_feature, new_feature, threshold):
    idx_to_drop = np.array([])
    for i in range(old_feature.shape[1]):
        for j in range(new_feature.shape[1]):
            corr = np.corrcoef(old_feature[:, i], new_feature[:, j])
            if abs(corr[0, 1]) > threshold:
                idx_to_drop = np.append(idx_to_drop, j)
        idx_to_keep = np.setdiff1d(np.arange(new_feature.shape[1]), idx_to_drop)
        new_feature = new_feature[:, idx_to_keep]
        idx_to_drop = np.array([])
    return new_feature

def get_recursive_feature(graph, basic_feature, n_iter=1):
    with graph.local_scope():

        recursive_feature = [basic_feature]
        for iter_idx in range(n_iter):
            graph.srcdata['h'] = recursive_feature[-1]
            graph.update_all(fn.copy_u('h', 'msg'), fn.mean('msg', 'neigh_mean'))
            graph.update_all(fn.copy_u('h', 'msg'), fn.sum('msg', 'neigh_sum'))

            iter_feature = th.cat([graph.dstdata['neigh_mean'], 
                                   graph.dstdata['neigh_sum']], dim=1)
            iter_feature = prune_feature(recursive_feature[-1], iter_feature, threshold=0.5)
            recursive_feature.append(iter_feature)
        
        return th.cat(recursive_feature[1:], dim=1)

# @thread_wrapped_func
def get_node_ego_feature(graph, node):
    neighs = graph.in_edges([node])[0]    
    nodes = th.cat([node.view(1), neighs])
    num_nodes = nodes.shape[0]

    internal_degree = th.tensor(graph.subgraph(nodes).number_of_edges(), dtype=th.float32)
    overall_degree = th.sum(graph.in_degrees(nodes), dtype=th.float32)
    # there 32 isolated nodes in train graph
    external_degree = overall_degree - internal_degree
    if num_nodes == 1:
        overall_degree = th.tensor(float('inf'))
        external_degree = th.tensor(0.)
        num_nodes = 2
    node_ego_feature = th.cat([internal_degree.view(1), 
                                external_degree.view(1), 
                                (internal_degree/overall_degree).view(1),
                                (external_degree/overall_degree).view(1), 
                                # clustering coefficient
                                (internal_degree/(num_nodes*(num_nodes-1))).view(1)])
    return node_ego_feature

def get_ego_feature(graph, parallel=False):
    ego_feature = []
    if not parallel:
        for node in graph.nodes():
            node_ego_feature = get_node_ego_feature(graph, node)
            ego_feature.append(node_ego_feature)
    else:
        pool = mp.Pool(mp.cpu_count())
        results = pool.starmap_async(get_node_ego_feature, 
                                     [(graph, node) for node in graph.nodes()])
        remaining = results._number_left
        pbar = tqdm(total=remaining)
        while True:
            pbar.update(remaining - results._number_left)
            if results.ready(): break
            remaining = results._number_left
            time.sleep(1)
        results = results.get()
        pool.close()
        pool.join()
        pbar.close()

        ego_feature += [node_ego_feature for node_ego_feature in tqdm(results)]
    return th.stack(ego_feature)

def get_local_feature(graph):
    degree = graph.in_degrees().to(th.float32)
    return degree.unsqueeze(1)

def get_basic_feature(graph, normalize=True, parallel=False):
    local_feature = get_local_feature(graph)
    ego_feature = get_ego_feature(graph, parallel=parallel)
    basic_feature = th.cat([local_feature, ego_feature], dim=1)
    if normalize:
        basic_feature = MinMaxScaling(basic_feature, dim=0)
    return basic_feature

def extract_refex_feature(graph, parallel):
    basic_feature = get_basic_feature(graph, normalize=True, parallel=parallel)
    return basic_feature
    # recursive_feature = get_recursive_feature(graph, basic_feature, n_iter=1)
    # return th.cat([basic_feature, recursive_feature], dim=1)

if __name__ == "__main__":
    from data import MovieLens
    movielens = MovieLens("ml-100k", testing=True)

    train_edges = movielens.train_rating_pairs
    train_graph = movielens.train_graph

    t_start = time.time()
    refex_feature = extract_refex_feature(train_graph, parallel=True).to(th.float)
    print("Epoch time={:.2f}".format(time.time()-t_start))
    pass
