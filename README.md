## workflow-json-interpreter

This repo aims to build a logic workflow from a json file. It interprets the json file and builds a directed acyclic graph (DAG) in python that represents the workflow. Then, it executes the workflow.

## Usage:




### Example DAG Visualization

Below is an example visualization of a workflow DAG:

![Example DAG](assets/plot_dag.jpg)

The graph shows the nodes (workflow steps) connected by directed edges indicating the execution flow. Each node is labeled with its schema ID representing the operation to be performed.

Key features shown in the visualization:
- Nodes represent individual processing steps
- Directed edges show dependencies and execution order
- Left-to-right layout for clear flow visualization
- Node labels indicate the operation type (schema ID)


