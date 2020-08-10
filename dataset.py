import random
from collections import namedtuple

import numpy as np
import torch as th
import dgl

from utils import subgraph_extraction_labeling

class MovieLensDataset(th.utils.data.Dataset):
    def __init__(self, links, g_labels, graph, 
                hop=1, sample_ratio=1.0, max_nodes_per_hop=200):
        self.links = links
        self.g_labels = g_labels
        self.graph = graph 

        self.hop = hop
        self.sample_ratio = sample_ratio
        self.max_nodes_per_hop = max_nodes_per_hop

    def __len__(self):
        return len(self.links[0])

    def __getitem__(self, idx):
        u, v = self.links[0][idx], self.links[1][idx]
        g_label = self.g_labels[idx]

        subgraph = subgraph_extraction_labeling(
            (u, v), self.graph, 
            hop=self.hop, sample_ratio=self.sample_ratio, max_nodes_per_hop=self.max_nodes_per_hop)

        return subgraph, g_label

def collate_movielens(data):
    g_list, label_list = map(list, zip(*data))
    g = dgl.batch(g_list)
    g_label = th.stack(label_list)
    return g, g_label

if __name__ == "__main__":
    import time
    from data import MovieLens
    movielens = MovieLens("ml-100k", testing=False)

    train_dataset = MovieLensDataset(
        movielens.train_rating_pairs, movielens.train_rating_values, movielens.train_graph, 
        hop=1, sample_ratio=1.0, max_nodes_per_hop=200)

    train_loader = th.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True, 
                            num_workers=8, collate_fn=collate_movielens)
    # batch = next(iter(train_loader))

    iter_dur = []
    t_epoch = time.time()
    for iter_idx, batch in enumerate(train_loader, start=1):
        t_iter = time.time()
        inputs = batch[0] # .to(th.device('cuda:0'))

        iter_dur.append(time.time() - t_iter)
        if iter_idx % 100 == 0:
            print("Iter={}, time={:.4f}".format(
                iter_idx, np.average(iter_dur)))
            iter_dur = []
    print("Epoch time={:.2f}".format(time.time()-t_epoch))
