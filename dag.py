import json
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import matplotlib.pyplot as plt


def plot_dag(dag):
    """
    Grafica el DAG de manera estructurada con pygraphviz.
    """
    # Crear un grafo de pygraphviz
    ag = nx.nx_agraph.to_agraph(dag)

    # Etiquetar nodos con el schemaId
    for node in dag.nodes:
        ag.get_node(node).attr['label'] = dag.nodes[node]['schemaId']

    # Configurar dirección del flujo
    ag.graph_attr.update(rankdir='LR', splines='true', overlap='false')

    # Dibujar el grafo
    plt.figure(figsize=(12, 8))
    ag.draw('/tmp/dag_output.png', prog='dot')  # Usa dot para una disposición estructurada
    img = plt.imread('/tmp/dag_output.png')
    plt.imshow(img)
    plt.axis('off')
    plt.show()


## Funciones de bloques de Safe:
def alarm_manager(param1, params=None):
    print(f'ejecutado alarm_manager {param1}')
    return f"Output of alarm_manager with param1={param1}, params={params} \n"


def notification_on_site(param2, params=None):
    print(f'ejecutado notification_on_site {param2}')
    return f"Output of notification_on_site with param2={param2}, params={params} \n"


def filter_node(param3, params=None):
    print(f'ejecutado filter_node {param3}')
    return f"Output of filter_node with param3={param3}, params={params} \n"

def ai_node(param3, params=None):
    print(f'ejecutado ai_node {param3}')
    return f"Output of ai_node with param3={param3}, params={params} \n"

def count_node(param3, params=None):
    print(f'ejecutado count_node {param3}')
    return f"Output of count_node with param3={param3}, params={params} \n"

def camera_node(param3, params=None):
    print(f'ejecutado camera_node {param3}')
    return f"Output of camera_node with param3={param3}, params={params} \n"


def distance_node(param3,param4, params=None):
    print(f'ejecutado distance_node {param3}')
    return f"Output of exdistance_nodeample_function_3 with param3={param3}, params={params} \n"

def start_cycle_node(params=None):
    print(f'ejecutado start_cycle_node')
    return f"Output of start_cycle_node with no_param, params={params} \n"

def notification_off_site(param3, params=None):
    print('ejecutado notification_off_site {param3}')
    return f"Output of notification_off_site with param3={param3}, params={params} \n"


def build_dag(json_path: str, plot: bool = False):
    with open(json_path, 'r') as f:
        flow = json.load(f)
    # Crear el grafo
    dag = nx.DiGraph()

    # Almacenar las funciones disponibles
    functions = {
        "alarm-manager": alarm_manager,
        "notification-on-site": notification_on_site,
        "filter-node": filter_node,
        "ai-node": ai_node,
        "count-node": count_node,
        "camera-node": camera_node,
        "notification-off-site": notification_off_site,
        "start-cycle-node": start_cycle_node,
        "distance-node": distance_node
    }

    for block in flow:
        node_id = block['id']
        func_name = block['schemaId']  # El nombre de la función está en 'schemaId'
        func = functions.get(func_name)
        
        if not func:
            raise ValueError(f"Función {func_name} no definida en el mapa de funciones")

        # Agregar el nodo al DAG
        dag.add_node(node_id, 
                     func=func,
                     schemaId=func_name,
                     params={inp['inputId']: inp['value'] for inp in block.get('inputs', [])})

        # Agregar conexiones desde los nodos de entrada
        for connection in block.get('connectedTo', {}).get('inputs', []):
            source_node = connection['source']
            dag.add_edge(source_node, node_id)

        # Agregar conexiones hacia los nodos de salida
        for connection in block.get('connectedTo', {}).get('outputs', []):
            target_node = connection['target']
            dag.add_edge(node_id, target_node)

    # Verificar que sea un DAG válido
    if not nx.is_directed_acyclic_graph(dag):
        raise ValueError("El flujo no es un DAG válido")
    if plot:
        plot_dag(dag)
    return dag


def execute_dag(dag):
    """
    ejecuta las operaciones en el flujo definido.
    """
    # Cargar el JSON

    # Resolver el DAG ejecutando las operaciones
    results = {}
    in_degrees = dict(dag.in_degree())

    def process_node(node_id):
        """
        Procesa un nodo ejecutando su función con los inputs correspondientes.
        """
        inputs = [results[predecessor] for predecessor in dag.predecessors(node_id)]
        func = dag.nodes[node_id]['func']
        params = dag.nodes[node_id]['params']

        # Asumimos que la función toma `params` y una lista de `inputs`.
        results[node_id] = func(*inputs, params=params)

    # Crear un ejecutor para manejar la concurrencia
    with ThreadPoolExecutor() as executor:
        # Inicializar la cola con nodos sin predecesores
        ready_nodes = [node for node, degree in in_degrees.items() if degree == 0]
        futures = {}

        while ready_nodes or futures:
            # Lanzar tareas para nodos listos
            for node_id in ready_nodes:
                futures[node_id] = executor.submit(process_node, node_id)

            ready_nodes = []

            # Esperar a que se completen algunas tareas
            for node_id, future in list(futures.items()):
                if future.done():
                    future.result()  # Propagar excepciones si ocurrieron
                    futures.pop(node_id)

                    # Reducir el in-degree de los sucesores y agregar a la lista de listos
                    for successor in dag.successors(node_id):
                        in_degrees[successor] -= 1
                        if in_degrees[successor] == 0:
                            ready_nodes.append(successor)

    return results