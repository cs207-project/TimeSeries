Implementation of vp_tree for CS207 EXTRA CREDIT: vantage point storage using a vptree integrated in.

Is a simple but yet powerfull implementation of
a vp-tree. It implements a simple knn search and
will implement a way to persist the tree.

Reference: Data Structures and Algorithms for Nearest Neighbor Search in General Metric Spaces (1993)
http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.41.4193

From Wiki
A vantage-point tree, or VP tree is a BSP tree which segregates data in a metric space by choosing a position in the space (the "vantage point") and dividing the data points into two partitions: those that are nearer to the vantage point than a threshold, and those that are not. By repeatedly applying this procedure to partition the data into smaller and smaller sets, a tree data structure is created where neighbors in the tree are likely to be neighbors in the space.[1]

One of its declination is called the multi-vantage point tree, or MVP tree: an abstract data structure for indexing objects from large metric spaces for similarity search queries. It uses more than one point to partition each level.