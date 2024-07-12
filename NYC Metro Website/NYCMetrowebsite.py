import streamlit as st
import networkx as nx
import random
from networkx_robustness import networkx_robustness
import pandas as pd
import matplotlib.pyplot as plt
from ast import literal_eval
import altair as alt


# Load your CSV file with node names
# Replace 'your_file.csv' with the actual filename
# import the data
OD_edges = pd.read_csv('OD_edges.csv', converters={'to': literal_eval, 'from': literal_eval}, index_col = None).drop(columns = 'Unnamed: 0')
PN_edges = pd.read_csv('PN_edges.csv', converters={'to': literal_eval, 'from': literal_eval}, index_col = None).drop(columns = 'Unnamed: 0')
node = pd.read_csv('node.csv', converters={'Nearest_Stop': literal_eval, 'location': literal_eval}, index_col = None)

## ORIGIN DESTINATION NETWORK
#adding edges
gOD = nx.from_pandas_edgelist(OD_edges, source='from', target='to', edge_attr='ridership')
#adding the nodes
for index, row in node.iterrows():
    gOD.add_node(row['Nearest_Stop'], location = row['location'], borough = row['borough'], routes = row['routes'])


## PN NETWORK
#adding edges
gPN = nx.from_pandas_edgelist(PN_edges, source='from', target='to', edge_attr='total_ridership')
#adding the nodes
for index, row in node.iterrows():
    gPN.add_node(row['Nearest_Stop'], location = row['location'], borough = row['borough'], routes = row['routes'])
node = node.set_index('Nearest_Stop')


## Get the degrees
dc = sorted(dict(gOD.degree(weight = 'ridership')).items(), key = lambda x: x[1], reverse = True)[:10]
DegreeCentDf = pd.DataFrame({'rank' : [i + 1 for i in range(10)], 'Station and Ridership': [str(i) for i in dc]})

## Get the betweeness centralities
bc = sorted(dict(nx.betweenness_centrality(gPN, weight = 'total_ridership')).items(), key = lambda x: x[1], reverse = True)[:10]
BetweenCentDf = pd.DataFrame({'rank' : [i + 1 for i in range(10)], 'Station': [str(i[0]) for i in bc]})

## Get the closeness centralities
cc = sorted(dict(nx.closeness_centrality(gPN)).items(), key = lambda x: x[1], reverse = True)[:10]
CloseCentDf = pd.DataFrame({'rank' : [i + 1 for i in range(10)], 'Station': [str(i[0]) for i in cc]})

## Create a map with these colored
colors = ['cyan', 'purple', 'coral']
nodes = list(gPN.nodes())
col_assign = ['gray' for i in range(len(nodes))]
partition_num = 0
for i in [dc, bc, cc]:
  for j in i:
    indexOfNode = nodes.index(j[0])
    col_assign[indexOfNode] = colors[partition_num]
  partition_num += 1

# Create a Streamlit app
st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# Title
st.title("NYC Metro Network Dashboard")

# list of degrees
degrees = pd.DataFrame(dict(gOD.degree(weight = 'ridership')).values())

# Display This
col1, col2, col3 = st.columns(3)

with col1:
    ## metro network
    fig, ax = plt.subplots()
    nx.draw(gPN, node_color=col_assign, pos = node['location'].to_dict(), with_labels=False, ax = ax, node_size=10, edge_color='gray', width=.8)
    st.pyplot(fig)

    ## degree df 
    st.write("These stations are the most traveled stations (Blue)")
    st.dataframe(DegreeCentDf, hide_index = True)
with col2:
    ## distribution of ridership
    st.write("Distribution of Ridership")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(degrees, bins='auto', color='skyblue')
    st.pyplot(fig)

    ## betweeness df 
    st.write("These stations are important in connecting other stations (Purple)")
    st.dataframe(BetweenCentDf, hide_index = True)
    
    
with col3:
    ## stats
    st.subheader(f':blue[Mean Ridership Across All Stations] : {degrees.mean()}')
    st.subheader(f':blue[Max Ridership Across All Stations] : {degrees.max()}')
    st.subheader(f':blue[Number of Stations] : {gPN.number_of_nodes()}')
    st.subheader(f':blue[Number of Tracks] : {gPN.number_of_edges()}')

    ## closeness df 
    st.write("These stations can most easily reach other stations (Coral)")
    st.dataframe(CloseCentDf, hide_index = True)

# Dropdown for selecting the type of attack
attack_type = st.selectbox("Select Type of Attack", ["None", "Random Attack", "Degree Centrality Attack", "Betweenness Centrality Attack", "Closeness Centrality Attack"])

attack_fraction = .99
n = len(gPN)

## FOR EACH ATTACK TYPE, record efficency, apl, and lcc stats and then plot them 
if attack_type == "Random Attack":
    initial, frac_lc_random, apl_random = networkx_robustness.simulate_random_attack(gPN, attack_fraction=attack_fraction)
    frac_removed_random = [i/n for  i in range(len(frac_lc_random))]
   
    gPNrandom = gPN.copy()
    fraction_removed_random = []
    efficiency_random = []
    for i in range(int(n * attack_fraction)):
        gPNrandom.remove_node(random.choice(list(gPNrandom.nodes())))
        eff = nx.global_efficiency(gPNrandom)
        if eff != 1:
            fraction_removed_random.append(i/n)
            efficiency_random.append(eff)   


    chart1 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_random, 'Fraction of Nodes in Largest Component': frac_lc_random})).mark_line().encode(x='Fraction of Nodes Removed', y='Fraction of Nodes in Largest Component').properties(title='Fraction of Nodes in Largest Component')
    chart2 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_random, 'Average Path Length': apl_random})).mark_line().encode(x='Fraction of Nodes Removed', y='Average Path Length').properties(title='Average Path Length')
    chart3 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': fraction_removed_random, 'Network Efficency': efficiency_random})).mark_line().encode(x='Fraction of Nodes Removed', y='Network Efficency').properties(title='Network Efficency')
    

    # # Display the Altair charts in the Streamlit app
    combined_chart = st.altair_chart(alt.hconcat(chart1, chart2, chart3))

if attack_type == "Degree Centrality Attack":
    initial, frac_lc_degree, apl_degree = networkx_robustness.simulate_degree_attack(gPN, attack_fraction=attack_fraction)
    frac_removed_degree = [i/n for  i in range(len(frac_lc_degree))]
   
    gPNdegree = gPN.copy()
    degree = nx.degree(gPNdegree)
    sorted_degree = sorted(dict(degree).items(), key = lambda x: x[1], reverse = True)
    fraction_removed_degree = []
    efficiency_degree = []
    for i in range(int(n * attack_fraction)):
        gPNdegree.remove_node(sorted_degree[i][0])
        eff = nx.global_efficiency(gPNdegree)
        if eff != 1:
            fraction_removed_degree.append(i/n)
            efficiency_degree.append(eff)
    
    
    
    chart1 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_degree, 'Fraction of Nodes in Largest Component': frac_lc_degree})).mark_line().encode(x='Fraction of Nodes Removed', y='Fraction of Nodes in Largest Component').properties(title='Fraction of Nodes in Largest Component')
    chart2 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_degree, 'Average Path Length': apl_degree})).mark_line().encode(x='Fraction of Nodes Removed', y='Average Path Length').properties(title='Average Path Length')
    chart3 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': fraction_removed_degree, 'Network Efficency': efficiency_degree})).mark_line().encode(x='Fraction of Nodes Removed', y='Network Efficency').properties(title='Network Efficency')
    

    # # Display the Altair charts in the Streamlit app
    combined_chart = st.altair_chart(alt.hconcat(chart1, chart2, chart3))

if attack_type == "Betweenness Centrality Attack":
    initial, frac_lc_betweenness, apl_betweenness = networkx_robustness.simulate_betweenness_attack(gPN, attack_fraction=attack_fraction)
    frac_removed_betweenness = [i/n for  i in range(len(frac_lc_betweenness))]
   
    gPNbetweenness = gPN.copy()
    betweenness = nx.betweenness_centrality(gPNbetweenness)
    sorted_betweenness = sorted(dict(betweenness).items(), key = lambda x: x[1], reverse = True)
    fraction_removed_betweenness = []
    efficiency_betweenness = []
    for i in range(int(n * attack_fraction)):
        gPNbetweenness.remove_node(sorted_betweenness[i][0])
        eff = nx.global_efficiency(gPNbetweenness)
        if eff != 1:
            fraction_removed_betweenness.append(i/n)
        efficiency_betweenness.append(eff)
    
    chart1 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_betweenness, 'Fraction of Nodes in Largest Component': frac_lc_betweenness})).mark_line().encode(x='Fraction of Nodes Removed', y='Fraction of Nodes in Largest Component').properties(title='Fraction of Nodes in Largest Component')
    chart2 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_betweenness, 'Average Path Length': apl_betweenness})).mark_line().encode(x='Fraction of Nodes Removed', y='Average Path Length').properties(title='Average Path Length')
    chart3 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': fraction_removed_betweenness, 'Network Efficency': efficiency_betweenness})).mark_line().encode(x='Fraction of Nodes Removed', y='Network Efficency').properties(title='Network Efficency')
    
    # # Display the Altair charts in the Streamlit app
    combined_chart = st.altair_chart(alt.hconcat(chart1, chart2, chart3))

if attack_type == "Closeness Centrality Attack":
    initial, frac_lc_closeness, apl_closeness = networkx_robustness.simulate_closeness_attack(gPN, attack_fraction=attack_fraction)
    frac_removed_closeness = [i/n for  i in range(len(frac_lc_betweenness))]

    gPNcloseness = gPN.copy()
    closeness = nx.closeness_centrality(gPNcloseness)
    sorted_closeness = sorted(dict(closeness).items(), key = lambda x: x[1], reverse = True)
    fraction_removed_closeness = []
    efficiency_closeness = []
    for i in range(int(n * attack_fraction)):
        gPNcloseness.remove_node(sorted_closeness[i][0])
        eff = nx.global_efficiency(gPNcloseness)
        if eff != 1:
            fraction_removed_closeness.append(i/n)
            efficiency_closeness.append(eff)

    chart1 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_closeness, 'Fraction of Nodes in Largest Component': frac_lc_closeness})).mark_line().encode(x='Fraction of Nodes Removed', y='Fraction of Nodes in Largest Component').properties(title='Fraction of Nodes in Largest Component')
    chart2 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': frac_removed_closeness, 'Average Path Length': apl_closeness})).mark_line().encode(x='Fraction of Nodes Removed', y='Average Path Length').properties(title='Average Path Length')
    chart3 = alt.Chart(pd.DataFrame({'Fraction of Nodes Removed': fraction_removed_closeness, 'Network Efficency': efficiency_closeness})).mark_line().encode(x='Fraction of Nodes Removed', y='Network Efficency').properties(title='Network Efficency')
    

    # # Display the Altair charts in the Streamlit app
    combined_chart = st.altair_chart(alt.hconcat(chart1, chart2, chart3))


# Dropdown for selecting multiple nodes
selected_nodes = st.multiselect("Select Nodes", gPN.nodes())
# calculate the impact of removing nodes
if st.button('See Impact'):
    if len(selected_nodes) > 0:
        gPN1 = gPN.copy()
        node_removed = ['None']
        Gc = gPN1.subgraph(sorted(nx.connected_components(gPN1), key=len, reverse=True)[0])
        eff = [nx.global_efficiency(gPN1)]
        apl = [nx.average_shortest_path_length(Gc)]
        lcc = [Gc.number_of_nodes()/gPN1.number_of_nodes()]
        for i in selected_nodes:
            node = (i[0] , i[1])
            gPN1.remove_node(node)
            Gc = gPN1.subgraph(sorted(nx.connected_components(gPN1), key=len, reverse=True)[0])
            eff.append(nx.global_efficiency(gPN1))
            try:
                apl.append(nx.average_shortest_path_length(Gc))
            except:
                apl.append(0)
            try:
                lcc.append(Gc.number_of_nodes()/gPN1.number_of_nodes())
            except:
                lcc.append(0)
            node_removed.append(node)
        # value of the metric is the last calculation
        # delta is the pecent change from the og to the last calculation 
        valueE = round(eff[-1], 3)
        deltaE = round(((eff[1] - eff[0]) / eff[0]) * 100, 2)
        valueA = round(apl[-1], 3)
        deltaA = round(((apl[1] - apl[0]) / apl[0]) * 100, 2)
        valueL = round(lcc[-1], 3)
        deltaL = round(((lcc[1] - lcc[0]) / lcc[0]) * 100, 2)

        # write the three metrics 
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Fraction of Nodes in Largest Component", value=valueL, delta=f"{deltaL}%")
        with col2:
            st.metric(label="Average Path Length", value=valueA, delta=f"{deltaA}%")
        with col3:
            st.metric(label="Network Efficency", value=valueE, delta=f"{deltaE}%")

    

    

