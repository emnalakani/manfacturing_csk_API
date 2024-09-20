

import os
import uuid
import requests


def add_classes_to_triple_store(expression: str) -> str:

    # Check for isOutputOf relationship, adapting example to a typical Datalog use case
    if "isOutputOf" in expression:
        product_name = expression.split("(")[1].split(")")[0]
        process_name = expression.split("(")[3].split(")")[0]

        insertSparqlQuery =  f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
            PREFIX core: <https://spec.industrialontologies.org/ontology/core/Core/>
            PREFIX bfo: <http://purl.obolibrary.org/obo/>

            # Define classes if they don't already exist
            INSERT {{
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                chaikmat:{product_name} rdf:type owl:Class .
                chaikmat:{process_name} rdf:type owl:Class .                
                chaikmat:{product_name} rdfs:subClassOf core:MaterialProduct .
                chaikmat:{process_name} rdfs:subClassOf core:ManufactringProcess .
              }}
            }} WHERE {{
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                OPTIONAL {{
                  chaikmat:{product_name} rdf:type owl:Class .
                }}
                OPTIONAL {{
                  chaikmat:{process_name} rdf:type owl:Class .
                }}
                FILTER NOT EXISTS {{ 
                  chaikmat:{product_name} rdf:type owl:Class 
                }}
                FILTER NOT EXISTS {{ 
                  chaikmat:{process_name} rdf:type owl:Class 
                }}OPTIONAL {{
                  chaikmat:{product_name} rdf:type owl:Class .
                  FILTER NOT EXISTS {{ chaikmat:{product_name} rdfs:subClassOf core:MaterialProduct }}
                }}
                OPTIONAL {{
                  chaikmat:{process_name} rdf:type owl:Class .
                  FILTER NOT EXISTS {{ chaikmat:{process_name} rdfs:subClassOf core:ManufactringProcess }}
                }}
              }}
            }}
        """
        print("inserting classes")
        result =  execute_insert_sparql_query(insertSparqlQuery)
        if result:
            product_instance = f"{product_name}_{str(uuid.uuid4())}"
            process_instance = f"{process_name}_{str(uuid.uuid4())}"

            # Insert instances
            insertInstancesQuery = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
    PREFIX core: <https://spec.industrialontologies.org/ontology/core/Core/>

    INSERT {{
      GRAPH <http://mcsk.enit.fr/chaikmat> {{
        # Assert instances
        chaikmat:{product_instance} rdf:type chaikmat:{product_name} .
        chaikmat:{process_instance} rdf:type chaikmat:{process_name} .
        
        # Assert the isOutputOf relationship
        chaikmat:{product_instance} core:isOutputOf chaikmat:{process_instance} .
      }}
    }} WHERE {{
      GRAPH <http://mcsk.enit.fr/chaikmat> {{
        # Ensure instances are not already asserted
        FILTER NOT EXISTS {{
          chaikmat:{product_instance} rdf:type chaikmat:{product_name} .
        }}
        FILTER NOT EXISTS {{
          chaikmat:{process_instance} rdf:type chaikmat:{process_name} .
        }}
      }}
    }}
"""
            print("inserting instances")
            result = execute_insert_sparql_query(insertInstancesQuery)
            return result
        else:
            return False
    # Example of translating "precedes" relationship
    elif "precedes" in expression:
        preceding_process = expression.split("(")[1].split(")")[0]
        succeeding_process = expression.split("(")[3].split(")")[0]

        insertSparqlQuery = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
            PREFIX bfo: <http://purl.obolibrary.org/obo/>
            PREFIX core: <https://spec.industrialontologies.org/ontology/core/Core/>

            INSERT {{
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                # Define classes
                chaikmat:{preceding_process} rdf:type owl:Class ;
                                             rdfs:subClassOf core:ManufactringProcess .
                chaikmat:{succeeding_process} rdf:type owl:Class ;
                                              rdfs:subClassOf core:ManufactringProcess .

              }}
            }} WHERE {{
              # Ensure classes are defined once
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                OPTIONAL {{
                  chaikmat:{preceding_process} rdf:type owl:Class .
                  FILTER NOT EXISTS {{ chaikmat:{preceding_process} rdfs:subClassOf core:ManufactringProcess }}
                }}
                OPTIONAL {{
                  chaikmat:{succeeding_process} rdf:type owl:Class .
                  FILTER NOT EXISTS {{ chaikmat:{succeeding_process} rdfs:subClassOf core:ManufactringProcess }}
                }}
              }}
            }}
            """
        
        print("inserting classes")
        result = execute_insert_sparql_query(insertSparqlQuery)

        if result:
            preceding_instance = f"{preceding_process}_{str(uuid.uuid4())}"
            succeeding_instance = f"{succeeding_process}_{str(uuid.uuid4())}"

            # Query to insert instances and precedes relationship
            insertInstancesQuery = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
                PREFIX bfo: <http://purl.obolibrary.org/obo/>

                INSERT {{
                  GRAPH <http://mcsk.enit.fr/chaikmat> {{
                    # Assert instances
                    chaikmat:{succeeding_instance} rdf:type chaikmat:{succeeding_process} .
                    chaikmat:{preceding_instance} rdf:type chaikmat:{preceding_process} .

                    # Assert the precedes relationship
                    chaikmat:{preceding_instance} bfo:BFO_0000063 chaikmat:{succeeding_instance} .
                  }}
                }} WHERE {{
                  GRAPH <http://mcsk.enit.fr/chaikmat> {{
                    # Ensure instances are not already asserted
                    FILTER NOT EXISTS {{
                      chaikmat:{succeeding_instance} rdf:type chaikmat:{succeeding_process} .
                    }}
                    FILTER NOT EXISTS {{
                      chaikmat:{preceding_instance} rdf:type chaikmat:{preceding_process} .
                    }}
                  }}
                }}
            """

            # Execute insert instances query
            print("Inserting instances and precedes relationship")
            result_instances = execute_insert_sparql_query(insertInstancesQuery)
            return result_instances
        else:
            print("Error inserting classes and subclass relationships")
            return False

    # Example of translating "participatesAtSomeTime" relationship
    elif "participatesAtSomeTime" in expression:
        process_name = expression.split("(")[1].split(")")[0]
        machine_name = expression.split("(")[3].split(")")[0]

        insertSparqlQuery =   f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
        PREFIX bfo: <http://purl.obolibrary.org/obo/>
        PREFIX msdl: <http://infoneer.txstate.edu/ontology/MSDL_>

        INSERT {{
          GRAPH <http://mcsk.enit.fr/chaikmat> {{
            # Define classes if they don't already exist
            chaikmat:{process_name} rdf:type owl:Class ;
                                     rdfs:subClassOf core:ManufactringProcess .
            chaikmat:{machine_name} rdf:type owl:Class ;
                                     rdfs:subClassOf msdl:MSDL_0000030 .
          }}
        }} WHERE {{
          GRAPH <http://mcsk.enit.fr/chaikmat> {{
            OPTIONAL {{
              chaikmat:{process_name} rdf:type owl:Class .
              FILTER NOT EXISTS {{ chaikmat:{process_name} rdfs:subClassOf bfo:Process }}
            }}
            OPTIONAL {{
              chaikmat:{machine_name} rdf:type owl:Class .
              FILTER NOT EXISTS {{ chaikmat:{machine_name} rdfs:subClassOf msdl:MSDL_0000030 }}
            }}
          }}
        }}
    """
        print("inserting classes")
        result =  execute_insert_sparql_query(insertSparqlQuery)

        if result:
            process_instance = f"{process_name}_{str(uuid.uuid4())}"
            machine_instance = f"{machine_name}_{str(uuid.uuid4())}"

        # Query to insert instances and relationship
        insertInstancesQuery = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX chaikmat: <http://mcsk.enit.fr/chaikmat#>
            PREFIX bfo: <http://purl.obolibrary.org/obo/>

            INSERT {{
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                # Assert instances
                chaikmat:{process_instance} rdf:type chaikmat:{process_name} .
                chaikmat:{machine_instance} rdf:type chaikmat:{machine_name} .

                # Assert the participatesAtSomeTime relationship
                chaikmat:{machine_instance} bfo:BFO_0000056 chaikmat:{process_instance} .
              }}
            }} WHERE {{
              GRAPH <http://mcsk.enit.fr/chaikmat> {{
                # Ensure instances are not already asserted
                FILTER NOT EXISTS {{
                  chaikmat:{process_instance} rdf:type chaikmat:{process_name} .
                }}
                FILTER NOT EXISTS {{
                  chaikmat:{machine_instance} rdf:type chaikmat:{machine_name} .
                }}
              }}
            }}
        """

        # Execute insert instances query
        print("Inserting instances and participatesAtSomeTime relationship")
        result_instances = execute_insert_sparql_query(insertInstancesQuery)
        return result_instances
    else:
        print("Error inserting classes and subclass relationships for participatesAtSomeTime")
        return False




def execute_ask_sparql_query(query: str) -> bool:
    """
    Execute ask a SPARQL query against GraphDB and return True if successful, False otherwise.
    """

    headers = {
        "Content-Type": "application/sparql-query",
    }
    url = f"{os.getenv('GRAPHDB_URL')}/repositories/{os.getenv('REPOSITORY_ID')}/statements"
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 200:
        return True
    else:
        print(f"SPARQL ask query execution failed: {response.text}")
        return False
    
def execute_insert_sparql_query(query: str) -> bool:
    """
    Execute insert a SPARQL query against GraphDB and return True if successful, False otherwise.
    """
    print(query)

    headers = {
        "Content-Type": "application/sparql-update",
    }
    url = f"{os.getenv('GRAPHDB_URL')}/repositories/{os.getenv('REPOSITORY_ID')}/statements"
    response = requests.post(url, headers=headers, data=query)

    if response.status_code == 204:
        return True
    else:
        print(f"SPARQL insert query execution failed with code: {response.status_code}: {response.text}")
        return False
    
def execute_select_sparql_query(query: str, graph_name: str) -> dict:
    headers = {
        "Accept": "application/sparql-results+json",
    }
    url = f"{os.getenv('GRAPHDB_URL')}/repositories/{os.getenv('REPOSITORY_ID')}"

    params = {
        "query": query,
        "default-graph-uri": graph_name if graph_name else ""
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"SPARQL select query execution failed with code: {response.status_code}: {response.text}")
        return {"error": f"SPARQL select query execution failed with code: {response.status_code}"}
        return []
    
    
def getTriplesFromGraph(graph_name: str):
    """
    Prepare and execute a SPARQL SELECT query to fetch all triples from the graph.
    """
    query = f"""
    SELECT ?subject ?predicate ?object
    FROM <{graph_name}>
    WHERE {{
        ?subject ?predicate ?object
    }}
    """

    results = execute_select_sparql_query(query, graph_name)

    return results.get('results', {}).get('bindings', [])