"""
This class implements the simple pagerank algorithm
as described in the first part of the project.
"""
class SimplePageRank(object):

    """
    Keeps track of the rdd used as the input data. 
    This should be a list of lines similar to the example input files.
    You do not need to change this method, but feel free to do so to suit your needs. 
    However, the signature MUST stay the same.
    """
    def __init__(self, input_rdd):
        self.input_rdd = input_rdd

    """
    Computes the pagerank algorithm for num_iters number of iterations.
    You do not need to change this method, but feel free to do so to suit your needs. 
    However, the signature MUST stay the same.
    The output should be a rdd of (pagerank score, node label) pairs, 
    sorted by pagerank score in descending order.
    """
    def compute_pagerank(self, num_iters):
        nodes = self.initialize_nodes(self.input_rdd)  # nodes: (0, (1.0, frozenset([1, 2])))....
        num_nodes = nodes.count()
        for i in range(0, num_iters):
            print "**********************************************"
            print num_iters
            nodes = self.update_weights(nodes, num_nodes)  # nodes is list
        return self.format_output(nodes)
    """
    Converts the input_rdd to a rdd suitable for iteration with
    the pagerank update algorithm.
    The rdd nodes should be enough to calculate the next iteration
    of the pagerank update algorithm by itself, without using any
    external structures.
    That means that all the edges must be stored somewhere,
    as well as the current weights of each node.
    You do not need to change this method, but feel free to do so to suit your needs.
    In the default implemention, the rdd is simply a collection of (node label, (current weight, target)) tuples.
    Lines in the input_rdd file will either be blank or begin with "#", which
    should be ignored, or be of the form "source[whitespace]target" where source and target
    are labels for nodes that are integers. 
    For example, the line:
    1    3
    tells us that there is an edge going from node 1 to node 3.
    """
    @staticmethod
    def initialize_nodes(input_rdd):
        # takes in a line and emits edges in the graph corresponding to that line
        # for node in input_rdd.take(100):  # Return array with the first n elements of dataset.
        #     print "{}".format(node)
        # 0 1; 0 2; ...
        def emit_edges(line):
            # ignore blank lines and comments
            if len(line) == 0 or line[0] == "#":
                return []
            # get the source and target labels
            source, target = tuple(map(int, line.split()))  # frozenset([(0, 1, 2, 3)])
            # map the line from str to int, then change it to tuple form: edge = source, target
            # emit the edge
            edge = (source, frozenset([target]))
            # also emit "empty" edges to catch nodes that do not have any
            # other node leading into them, but we still want in our list of nodes
            self_source = (source, frozenset())
            self_target = (target, frozenset())
            return [edge, self_source, self_target]
            # flatmap emit three key-value pair, key: node, value: frozenset(..)
            # jk: emit value form: fronzenzet(list[tuple()])
        # collects all outgoing target nodes for a given source node
        # for two frozen set with same key: add frozen set together
        def reduce_edges(e1, e2):
            return e1 | e2 # frozenset use "|" as "+" operator

        # sets the weight of every node to 0, and formats the output to the 
        # specified format of (source (weight, targets))
        # map again for the required format of output
        def initialize_weights((source, targets)):
            return (source, (1.0, targets))

        nodes = input_rdd\
                .flatMap(emit_edges)\
                .reduceByKey(reduce_edges)\
                .map(initialize_weights)
        # for node in nodes.take(100):  # Return array with the first n elements of dataset.
        #     print "{}".format(node) 
        # (0, (1.0, frozenset([1, 2])))
        return nodes

    """
    Performs one iteration of the pagerank update algorithm on the set of node data.
    Details about the update algorithm are in the spec on the website.
    You are allowed to change the signature if you desire to.
    """
    @staticmethod
    def update_weights(nodes, num_nodes):  # nodes: list of node, (0, (1.0, frozenset([1, 2])))...
        # for node in nodes.take(100):
        #     print "{}".format(node)

        """
        Mapper phase.  -- distribute_weights
        Distributes pagerank scores for a given node to each of its targets,
        as specified by the update algorithm.
        Some important things to consider:
        We can't just emit (target, weight) values to the reduce phase, 
        because then the reduce phase will lose information on the outgoing edges
        for the nodes. We have to emit the (node, targets) pairs too so that 
        the edges can be remembered for the next iteration.
        Think about the best output format for the mapper so the reducer can
        get both types of information.
        You are allowed to change the signature if you desire to.
        """
        def distribute_weights((node, (weight, targets))):
            # pass in: elem of nodes = (0, (1.0, frozenset([1, 2])))...

            # for node in nodes.take(100):
            # print "{}".format(node)        
            # YOUR CODE HERE
            # if isinstance(targets, frozenset):
            #     print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
            # the targets passed in are all frozenset

            node_targets = (node, targets)  # pass node-targets to return value, node-frozenset
            node_weight_self = (node, frozenset([0.05,]))  # stay in same page, 0.05 goes back to self node
            node_weight_random = (node, frozenset([0.1,]))  # random factor for each node
            node_weight_list = [node_targets, node_weight_self, node_weight_random]
            
            targets_unpack = next(iter(targets))
            print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
            print targets_unpack
            if len(targets_unpack) == 0:  # no external links in this page
                average_weight = frozenset([tuple(0.85 / (num_nodes - 1))])
                new_target = range(num_nodes)  # give 0.85 to all other nodes
                new_target.remove(node)
                for target in new_target:
                    node_weight_pair = (target, average_weight)
                    node_weight_list.append(node_weight_pair)
            else:  # when links exist
                average_weight = 0.85 / len(targets)
                for target in targets:
                    node_weight_pair = (target, average_weight)
                    node_weight_list.append(node_weight_pair)
                # new_weight = new_weight + [average_weight] * (len(targets) - 1)
            return node_weight_list

        """
        Reducer phase.
        We are given a node as a key and a list of all the values emitted by the mappers
        corresponding to that key.
        There should be two types of values:
        Pagerank scores, which represent how much score an incoming node is giving to us,
        and edge data, which we need to collect and store for the next iteration.
        The output of this phase should be in the same format as the input to the mapper.
        You are allowed to change the signature if you desire to.
        """
        def collect_weights((node, values)):
            # YOUR CODE HERE
            # input: node, [list of values of this node]
            weight = 0
            for val in values:
                if isinstance(val, frozenset):
                    print "ffffffffffffffffffffffffffffffff"
                    targets = val
                    continue
                weight += val
            return (node, (weight, frozenset([tuple(targets)])))

        # retVal of update_xxx
        return nodes.flatMap(distribute_weights).groupByKey().map(collect_weights)

    """
    Formats the output of the data to the format required by the specs.
    If you changed the format of the update_weights method you will 
    have to change this as well.
    Otherwise, this is fine as is.
    """
    @staticmethod
    def format_output(nodes):
        return nodes\
                .map(lambda (node, (weight, targets)): (weight, node))\
                .sortByKey(ascending = False)\
                .map(lambda (weight, node): (node, weight))