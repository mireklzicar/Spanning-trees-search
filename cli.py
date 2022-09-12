import argparse
from argparse import RawTextHelpFormatter

# import GraphMatrix and SpanningTrees and make a CLI interface with option to load and run a spanning tree prediction

# Load the libraries
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from spanning_trees_search.GraphMatrix import GraphMatrix
from spanning_trees_search.SpanningTrees import SpanningTrees
import warnings

warnings.filterwarnings("ignore")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Make a parser
parser = argparse.ArgumentParser(description="""Spanning Trees Search 
    A library for spanning tree computation 
    - one of the arguments --graph-adjacency --graph-incidence is required 
    - argument --graph-incidence: not allowed with argument --graph-adjacency 
    
    Example usage:""", formatter_class=RawTextHelpFormatter)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    "--graph-adjacency",
    type=str,
    help="Graph to be loaded in adjacency matrix format in .csv",
)
group.add_argument(
    "--graph-incidence",
    type=str,
    help="Graph to be loaded in incidence matrix format in .csv",
)
parser.add_argument(
    "--output",
    type=str,
    help="Directory where all files will be saved",
    default="/tests/mygraph_run",
)
# parser.add_argument(
#     "--export",
#     type=str,
#     help="Directory where all files will be saved",
#     default="adjacency_csv",
#     choices=["adjacency_csv", "incidence_csv", "none"],
# )
# parser.add_argument(
#     "--visualise",
#     action="store_true",
#     help="Visualisation type",
# )

parser.add_argument(
    "--gif",
    action="store_true",
    help="Gif export",
)

parser.add_argument(
    "--count", 
    action="store_true",
    help="Count the number of spanning trees",
)

parser.add_argument(
    "--trees",
    help="Find spanning trees",
    action="store_true",
    )

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
    
args = parser.parse_args()


def main():
    # Load the graph
    graph = GraphMatrix() # Create an instance of GraphMatrix
    if args.graph_adjacency:
        graph.load(args.graph_adjacency, mode="adjacency") # Load the graph from adjacency matrix
    if args.graph_incidence:
        graph.load(args.graph_incidence, mode="incidence") # Load the graph from incidence matrix
    
    # Count if --count arg is specified
    if args.count:
        spanning_trees = SpanningTrees(graph.graph)
        spanning_trees.spanning_trees_count()
        print("Number of spanning trees: ", spanning_trees.spanning_trees_num)

    # Find spanning trees if --trees arg is specified
    if args.trees:
        spanning_trees = SpanningTrees(graph.graph)
        if args.output:
            spanning_trees.compute_spanning_trees(visualisation=False, progress_bar=False)
            spanning_trees.export_spanning_trees(export='adjacency_csv', save_path=args.output)
            if args.gif:
                spanning_trees.export_gif()
            print("Everyting is saved in ", args.output)

if __name__ == "__main__":
    main()
    
