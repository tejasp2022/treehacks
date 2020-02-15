from neo4j import GraphDatabase

class DiagnoseDisease(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_nodes(self, node_type):
        with self._driver.session() as session:
            result = session.run(f"MATCH (n:{node_type}) RETURN n.name")
            return result.records()

    def create_graph(self, symptoms, diseases, relationships):
        diagnoser.create_nodes('Symptom', symptoms)
        diagnoser.create_nodes('Disease', diseases)
        diagnoser.create_relationships(relationships)

    def create_node(self, node_type, name):
        with self._driver.session() as session:
            session.run(f"CREATE (n:{node_type} {{ name: '{name}'}})")
            print(f"Node created: {node_type}, {name}")

    def create_nodes(self, node_type, node_list):
        for node in node_list:
            self.create_node(node_type, node)

    def create_relationship(self, symptom, disease):
        with self._driver.session() as session:
            session.run(f"MATCH (a:Symptom),(b:Disease) WHERE a.name='{symptom}' AND b.name='{disease}' CREATE (a)-[r:IS_SYMPTOM_OF]->(b) RETURN r")
            print(f"Relationship created: {symptom}, {disease}")

    def create_relationships(self, relationship_dict):
        for disease in relationship_dict:
            for symptom in relationship_dict[disease]:
                self.create_relationship(symptom, disease)

# Establish initial graph with symptoms, diseases, and relationships
def set_up_program(diagnoser):
    symptoms = ['Persistent Cough', 'Confusion', 'Fever', 'Fatigue', 'Bronchitis', 'Pleural Effusion', 'Nausea', 'Dyspnea', 'Neck Swelling', 'Weight Loss', 'Chest Pain']
    diseases = ['Pulmonary Tuberculosis', "Lung Tumor", "Pneumonia"]
    relationships = {"Pulmonary Tuberculosis": ["Persistent Cough", "Fatigue", "Weight Loss", "Chest Pain", "Fever"],
                    "Lung Tumor": ["Persistent Cough", "Chest Pain", "Bronchitis", "Neck Swelling", "Dyspnea"],
                    "Pneumonia": ["Dyspnea", "Nausea", "Fatigue", "Pleural Effusion", "Confusion"]}
    diagnoser.create_graph(symptoms, diseases, relationships)

# Given symptom, return tuple of remaining possible_diseases and ignored_diseases
def narrow_down(diagnoser, symptom, possible_diseases, ignored_diseases):
    pass

# Run Alexa to assess disease
def run_alexa_program(diagnoser):
    symptoms = set([elem[0] for elem in diagnoser.get_nodes("Symptom")])
    possible_diseases = set([elem[0] for elem in diagnoser.get_nodes("Disease")])
    ignored_diseases = set()

    first_symptom = input("What is you primary concern?")
    while (first_symptom not in symptoms):
        first_symptom = input("Not a valid symptom. Please try again.")

    # Narrow down to remaining possible diseases
    while len(possible_diseases) > 1:
        possible_diseases, ignored_diseases = narrow_down_from_symptom(diagnoser, symptom, possible_diseases, ignored_diseases)
    
    print(possible_diseases)

if __name__ == "__main__":
    diagnoser = DiagnoseDisease('bolt://localhost:7687','neo4j','hellohello')
    set_up = False
    run_alexa = True
    if set_up: set_up_program(diagnoser)
    if run_alexa: run_alexa_program(diagnoser)
    diagnoser.close()