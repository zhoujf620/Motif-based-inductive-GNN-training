# Graph Convolutional Matrix Completion

Paper link: [https://arxiv.org/abs/1706.02263](https://arxiv.org/abs/1706.02263)
Author's code: [https://github.com/riannevdberg/gc-mc](https://github.com/riannevdberg/gc-mc)

The implementation does not handle side-channel features and mini-epoching and thus achieves
slightly worse performance when using node features.

Credit: Jiani Zhang ([@jennyzhang0215](https://github.com/jennyzhang0215))

## Dependencies
* PyTorch 1.2+
* pandas
* torchtext 0.4+ (if using user and item contents as node features)

## Data

Supported datasets: ml-100k, ml-1m, ml-10m

## How to run
### Train with full-graph
ml-100k, no feature
```bash
python3 train.py --data_name=ml-100k --use_one_hot_fea --gcn_agg_accum=stack --train_max_epoch 80 --max_nodes_per_hop 200 --save_dir /log/dir/ --batch_size 50 --train_decay_epoch 50 --num_igmc_bases 4  --train_min_lr 1e-6  --train_val

```
Results: RMSE=0.9088 (0.910 reported)
Speed: 0.0410s/epoch (vanilla implementation: 0.1008s/epoch)

ml-100k, with feature
```bash
python3 train.py --data_name=ml-100k --gcn_agg_accum=stack
```
Results: RMSE=0.9448 (0.905 reported)

ml-1m, no feature
```bash
python3 train.py --data_name=ml-1m --gcn_agg_accum=sum --use_one_hot_fea
```
Results: RMSE=0.8377 (0.832 reported)
Speed: 0.0844s/epoch (vanilla implementation: 1.538s/epoch)

ml-10m, no feature
```bash
python3 train.py --data_name=ml-10m --gcn_agg_accum=stack --gcn_dropout=0.3 \
                                 --train_lr=0.001 --train_min_lr=0.0001 --train_max_iter=15000 \
                                 --use_one_hot_fea --gen_r_num_basis_func=4
```
Results: RMSE=0.7800 (0.777 reported)
Speed: 1.1982/epoch (vanilla implementation: OOM)
Testbed: EC2 p3.2xlarge instance(Amazon Linux 2)

### Train with minibatch on a single GPU
ml-100k, no feature
```bash
python3 train_sampling.py --data_name=ml-100k \
                          --use_one_hot_fea \
                          --gcn_agg_accum=stack \
                          --gpu 0

```
ml-100k, no feature with mix_cpu_gpu run, for mix_cpu_gpu run with no feature, the W_r is stored in CPU by default other than in GPU.
```bash
python3 train_sampling.py --data_name=ml-100k \
                          --use_one_hot_fea \
                          --gcn_agg_accum=stack \
                          --mix_cpu_gpu \
                          --gpu 0 
```
Results: RMSE=0.9380
Speed: 1.059s/epoch (Run with 70 epoches)
Speed: 1.046s/epoch (mix_cpu_gpu)

ml-100k, with feature
```bash
python3 train_sampling.py --data_name=ml-100k \
                          --gcn_agg_accum=stack \
                          --train_max_epoch 90 \
                          --gpu 0
```
Results: RMSE=0.9574

ml-1m, no feature
```bash
python3 train_sampling.py --data_name=ml-1m \
                          --gcn_agg_accum=sum \
                          --use_one_hot_fea \
                          --train_max_epoch 160 \
                          --gpu 0
```
ml-1m, no feature with mix_cpu_gpu run
```bash
python3 train_sampling.py --data_name=ml-1m \
                          --gcn_agg_accum=sum \
                          --use_one_hot_fea \
                          --train_max_epoch 60 \
                          --mix_cpu_gpu \
                          --gpu 0
```
Results: RMSE=0.8632
Speed: 7.852s/epoch (Run with 60 epoches)
Speed: 7.788s/epoch (mix_cpu_gpu)

ml-10m, no feature
```bash
python3 train_sampling.py --data_name=ml-10m \
                          --gcn_agg_accum=stack \
                          --gcn_dropout=0.3 \
                          --train_lr=0.001 \
                          --train_min_lr=0.0001 \
                          --train_max_epoch=60 \
                          --use_one_hot_fea \
                          --gen_r_num_basis_func=4 \
                          --gpu 0
```
ml-10m, no feature with mix_cpu_gpu run
```bash
python3 train_sampling.py --data_name=ml-10m \
                          --gcn_agg_accum=stack \
                          --gcn_dropout=0.3 \
                          --train_lr=0.001 \
                          --train_min_lr=0.0001 \
                          --train_max_epoch=60 \
                          --use_one_hot_fea \
                          --gen_r_num_basis_func=4 \
                          --mix_cpu_gpu \
                          --gpu 0
```
Results: RMSE=0.8050
Speed: 394.304s/epoch (Run with 60 epoches)
Speed: 408.749s/epoch (mix_cpu_gpu)
Testbed: EC2 p3.2xlarge instance

### Train with minibatch on multi-GPU
ml-100k, no feature
```bash
python train_sampling.py --data_name=ml-100k \
                         --gcn_agg_accum=stack \
                         --train_max_epoch 30 \
                         --train_lr 0.02 \
                         --use_one_hot_fea \
                         --gpu 0,1,2,3,4,5,6,7
```
ml-100k, no feature with mix_cpu_gpu run
```bash
python train_sampling.py --data_name=ml-100k \
                         --gcn_agg_accum=stack \
                         --train_max_epoch 30 \
                         --train_lr 0.02 \
                         --use_one_hot_fea \
                         --mix_cpu_gpu \
                         --gpu 0,1,2,3,4,5,6,7
```
Result: RMSE=0.9397
Speed: 1.202s/epoch (Run with only 30 epoches) 
Speed: 1.245/epoch (mix_cpu_gpu)

ml-100k, with feature
```bash
python train_sampling.py --data_name=ml-100k \
                         --gcn_agg_accum=stack \
                         --train_max_epoch 30 \
                         --gpu 0,1,2,3,4,5,6,7
```
Result: RMSE=0.9655
Speed:  1.265/epoch (Run with 30 epoches)

ml-1m, no feature
```bash
python train_sampling.py --data_name=ml-1m \
                         --gcn_agg_accum=sum \
                         --train_max_epoch 40 \
                         --use_one_hot_fea \
                         --gpu 0,1,2,3,4,5,6,7
```
ml-1m, no feature with mix_cpu_gpu run
```bash
python train_sampling.py --data_name=ml-1m \
                         --gcn_agg_accum=sum \
                         --train_max_epoch 40 \
                         --use_one_hot_fea \
                         --mix_cpu_gpu \
                         --gpu 0,1,2,3,4,5,6,7
```
Results: RMSE=0.8621
Speed: 11.612s/epoch (Run with 40 epoches)
Speed: 12.483s/epoch (mix_cpu_gpu)

ml-10m, no feature
```bash
python train_sampling.py --data_name=ml-10m \
                         --gcn_agg_accum=stack \
                         --gcn_dropout=0.3 \
                         --train_lr=0.001 \
                         --train_min_lr=0.0001 \
                         --train_max_epoch=30 \
                         --use_one_hot_fea \
                         --gen_r_num_basis_func=4 \
                         --gpu 0,1,2,3,4,5,6,7
```
ml-10m, no feature with mix_cpu_gpu run
```bash
python train_sampling.py --data_name=ml-10m \
                         --gcn_agg_accum=stack \
                         --gcn_dropout=0.3 \
                         --train_lr=0.001 \
                         --train_min_lr=0.0001 \
                         --train_max_epoch=30 \
                         --use_one_hot_fea \
                         --gen_r_num_basis_func=4 \
                         --mix_cpu_gpu \
                         --gpu 0,1,2,3,4,5,6,7
```
Results: RMSE=0.8084
Speed: 632.868s/epoch (Run with 30 epoches)
Speed: 633.397s/epoch (mix_cpu_gpu)
Testbed: EC2 p3.16xlarge instance

### Train with minibatch on CPU
ml-100k, no feature
```bash
python3 train_sampling.py --data_name=ml-100k \
                          --use_one_hot_fea \
                          --gcn_agg_accum=stack \
                          --gpu -1
```
Speed 1.591s/epoch
Testbed: EC2 r5.xlarge instance
