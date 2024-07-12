import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from ast import literal_eval

# load data
df = pd.read_csv("ridershipFullInfo.csv", converters={'Connections': literal_eval, 'Nearest_Stop': literal_eval})
nodes = df['Nearest_Stop'].to_list()
flow_in_values = df['ridership'].to_list()
df.set_index('Nearest_Stop', inplace=True)


# Create a new model
model = gp.Model("FlowInFlowOut_NYC_Metro")

# Decision variables
flows = {}
for i in nodes:
    for j in nodes:
        if i != j:
            flows[i, j] = model.addVar(vtype=GRB.CONTINUOUS, name=f"flow_{i}_{j}")

# Flow conservation constraints
for node in nodes:
    model.addConstr(gp.quicksum(flows[i, node] for i in nodes if i != node) - gp.quicksum(flows[node, j] for j in nodes if j != node) == 0, f"flow_conservation_{node}")

# Flow in constraints
for node in range(len(nodes)):
    model.addConstr(gp.quicksum(flows[i, nodes[node]] for i in nodes if i != nodes[node]) == flow_in_values[node], f"flow_in_{node}")

# Flow out constraints
for node in range(len(nodes)):
     model.addConstr(gp.quicksum(flows[nodes[node], j] for j in nodes if j != nodes[node]) == flow_in_values[node], f"flow_out_{node}")

# there has to be some flow between every possible match
for i in nodes:
    for j in nodes:
        if i != j:
            model.addConstr(flows[i, j] == flows[j, i])
            model.addConstr(flows[i, j] >= 1)

variance_objective = gp.quicksum((flows[i, j] - flows[j, i])*(flows[i, j] - flows[j, i]) for i in nodes for j in nodes if i != j)
model.setObjective(variance_objective, GRB.MINIMIZE)

# Solve the model
model.optimize()

# Print the solution
if model.status == GRB.OPTIMAL:
    print("Optimal Flow:")
    data = []
    for i in nodes:
        for j in nodes:
            if i != j:
                print(f"Flow from {i} to {j}: {flows[i, j].x}")
                data.append([i, j, flows[i,j].x])
        
    data = pd.DataFrame(data, columns = ['from', 'to', 'ridership'])
    data.to_csv('flowInFlowOutSolution.csv', index = False)

    