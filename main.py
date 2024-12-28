import dag

FILE_JSON = "workflow.json"

# Ejemplo de uso
if __name__ == "__main__":
    my_dag = dag.build_dag(FILE_JSON, plot = True)

    output = dag.execute_dag(my_dag)
    print(output)
