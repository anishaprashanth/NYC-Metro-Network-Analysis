# NYC Metro Network Analysia

This project focuses on analyzing the New York City (NYC) Metro using network analysis techniques. The code is organized into four main parts:

1. **Data Cleaning:** Involves preprocessing and cleaning the NYC Metro data to make it suitable for network analysis.

2. **Network Creation:** Builds a comprehensive network representation of the NYC Metro system, capturing the connections between stations and estimated riderships.

3. **Network Analysis:** Conducts an in-depth analysis of the NYC Metro network, with a focus on understanding its overall structure and properties.

4. **Tool/Dashboard Development:** Develops a user-friendly tool or dashboard that allows users to interactively explore network statistics and simulate attacks on the network to test its robustness.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Create_edgescsv.py](#Create_edgescsv.py)
- [DataCleaning.ipybn](#DataCleaning.ipybn)
- [NetworkFlowInFlowOut.py](#NetworkFlowInFlowOut.py)
- [NetworkAnalysis.ipybn](#NetworkAnalysis.ipybn)
- [robustness_tool.py](#NYCmetrowebsite.py)
- [Acknowledgments](#acknowledgments)

### Prerequisites

- Python 3.7 or higher is required to run this project. 
- A gurobi academic liscence is required for the NetworkFlowInFlowOut.py file 

### Installation 

These libraries are used in the code and may need to be installed as they do not come with Python. 

`pip install pandas`
`pip install numpy`
`pip install gurobipy`
`pip install networkx-robustness`
`pip install seaborn`
`pip install haversine`
`pip install streamlit `
`pip install networkx`
`pip install matplotlib` 

Here is a full list of libraries / imports used in this project: 
```python
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from ast import literal_eval
import streamlit as st
import networkx as nx
import random
from networkx_robustness import networkx_robustness
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from haversine import haversine, Unit
```

### Create_edgescsv.py

Uses MTA_Subway_Stations_20231102.csv file to find the edges in the physical network. This file has information about stations and the routes they follow. Additionally, if a row is below another row, and they follow the same route / line, then they are connected in real life. Using pandas and the shift function, we got a new data frame with connected stations and their informations into one row. Thereofre, every row represents an edge. 

### DataCleaning.ipybn

Uses the files Edges_new.csv, MTA_Subway_Monthly_Ridership__Feb2022_to_Jan2023.csv, flowInFlowOutSolution.csv

We have two data sets. One has station IDs and their riderships and the other has a list of subway complexes and their routes (which ones are connected). After some inital cleaning, we got the routes into Edges_new.csv.
Next step was to join the two data sets by matching the station IDS to subway complexes. We did this by using their latitude and longitude values given in both data sets. 

Next, we need to implement the riderships. Using the optimization script (NetworkFlowInFlowOut.py) we got flowInFlowOutSolution.csv which had the flows between all possible origin destination combinations. This is enough to create the origin destination network.

 Next, to create the Physical Network, we found the distances between stations to use an attribute for their edges. To find the ridership on these edges, we found the shortest paths on the network. For all edges, we sum the ridership of every shortest path between an origin and destination that passes through that edge on the physical network and that becomes the weigth of the edge in the physical network. We export OD_edges.csv, PN_edges.csv, node.csv to use for network analysis. 


### NetworkFlowInFlowOut.py

Uses the file ridershipFullInfo.csv

This is an optimization script. We have nodes and a flow in for every node. We create an optimization model where the flow into a node equals the flow out of a node (this gives the origin destination graph). We minmize the variance of the flows to make sure it is realistic, otherwise a valid solution would give very concentrated riderships and have other edges with very small riderships. 

### NetworkAnalysis.ipybn

Uses the files OD_edges.csv, PN_edges.csv, and node.csv

This is where the network analysis happens. First we construct the origin destination and physical networks using the OD_edges.csv, PN_edges.csv, and node.csv files. First we do some analysis on metrics such as degree centrality, betweneess centrality, and closeness centrality. We create vizualizations of the msot important stations using these metrics. 

Next we do clustering analysis by using the girvan newman algorithm and calculate the modularity of this. 

We also do robustness analysis by simualting various types of attacks and record various metrics. 

### NYCmetrowebsite.py

Uses the files OD_edges.csv, PN_edges.csv, and node.csv

This is a script used to build a streamlit app that is a dashboard. It uses a lot of the same code from the NetworkAnalysis.ipybn but puts it into a interactive dashboard. Users can view the network, tables of top ten nodes by various metrics, and some other network stats. Additionally, they can choose the type of attack they want to simulate and the app outputs the graph for that. Lastly, they can choose which nodes they want to remove from the graph manually and see the impact of that. 

### Acknowledgments
Tejas Santanam. (2023). tsantanam/networkx-robustness: v0.0.7 (v0.0.7). Zenodo. https://doi.org/10.5281/zenodo.7855211
