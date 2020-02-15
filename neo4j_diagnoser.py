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
            session.run(f"""MATCH (a:Symptom),(b:Disease) WHERE a.name='{symptom}'
                AND b.name='{disease}' CREATE (a)-[r:IS_SYMPTOM_OF]->(b)
                RETURN r""")
            print(f"Relationship created: {symptom}, {disease}")

    def create_relationships(self, relationship_dict):
        for disease in relationship_dict:
            for symptom in relationship_dict[disease]:
                self.create_relationship(symptom, disease)
                
    # Given symptom, return tuple of remaining poss_diseases and ign_diseases
    def narrow_from_symptom(self, symptom, poss_diseases, ign_diseases):
        with self._driver.session() as session:
            diseases_ob = session.run(f"""MATCH (a:Symptom),(b:Disease)
                WHERE (a)-[:IS_SYMPTOM_OF]->(b) and a.name='{symptom}'
                RETURN b.name""")
            new_diseases = set([elem[0] for elem in diseases_ob.records()])
            new_poss_diseases = poss_diseases & new_diseases
            new_ign_diseases = ign_diseases | (poss_diseases - new_diseases)
            return (new_poss_diseases, new_ign_diseases)

    # Given possible diseases and examined symptoms, selects next symptom
    def select_next_symptom(self, symptoms, poss_diseases, examined_symptoms):
        with self._driver.session() as session:
            symptom_counts = dict()
            for symptom in (symptoms - examined_symptoms):
                count = session.run(f"""MATCH (a:Symptom),(b:Disease)
                    WHERE (a)-[:IS_SYMPTOM_OF]->(b) AND a.name='{symptom}'
                    AND b.name IN {repr(list(poss_diseases))} RETURN COUNT(b)""")
                symptom_counts[symptom] = count.single()[0]
            return count_max(symptom_counts)

    # Given not symptom, return tuple of remaining poss_diseases and ign_diseases
    def narrow_from_not_symptom(self, symptom, poss_diseases, ign_diseases):
        with self._driver.session() as session:
            diseases_ob = session.run(f"""MATCH (a:Symptom),(b:Disease)
                WHERE (a)-[:IS_SYMPTOM_OF]->(b) and a.name='{symptom}'
                RETURN b.name""")
            not_diseases = set([elem[0] for elem in diseases_ob.records()])
            new_poss_diseases = poss_diseases - not_diseases
            new_ign_diseases = ign_diseases | not_diseases
            return (new_poss_diseases, new_ign_diseases)

def count_max(symptom_counts):
    max_count = 0
    max_elem = None
    for symptom in symptom_counts:
        if symptom_counts[symptom] > max_count:
            max_count = symptom_counts[symptom]
            max_elem = symptom
    return max_elem

# Establish initial graph with symptoms, diseases, and relationships
def set_up_program(diagnoser):
    symptoms = ['Persistent Cough', 'Confusion', 'Fever', 'Fatigue', 'Bronchitis', 'Pleural Effusion', 'Nausea', 'Dyspnea', 'Neck Swelling', 'Weight Loss', 'Chest Pain']
    diseases = ['Pulmonary Tuberculosis', "Lung Tumor", "Pneumonia"]
    relationships = {"Pulmonary Tuberculosis": ["Persistent Cough", "Fatigue", "Weight Loss", "Chest Pain", "Fever"],
                    "Lung Tumor": ["Persistent Cough", "Chest Pain", "Bronchitis", "Neck Swelling", "Dyspnea"],
                    "Pneumonia": ["Dyspnea", "Nausea", "Fatigue", "Pleural Effusion", "Confusion"]}
    diagnoser.create_graph(symptoms, diseases, relationships)

# Run Alexa to assess disease
def run_alexa_program(diagnoser):
    symptoms = set([elem[0] for elem in diagnoser.get_nodes("Symptom")])
    poss_diseases = set([elem[0] for elem in diagnoser.get_nodes("Disease")])
    ign_diseases = set()
    examined_symptoms = set()

    first_symptom = input("What is your primary concern? ")
    while (first_symptom not in symptoms):
        first_symptom = input("Not a valid symptom. Please try again. ")
    examined_symptoms.add(first_symptom)
    
    poss_diseases, ign_diseases = diagnoser.narrow_from_symptom(first_symptom,
                                    poss_diseases, ign_diseases)

    # Narrow down to remaining possible diseases
    while len(poss_diseases) > 1:
        next_symptom = diagnoser.select_next_symptom(symptoms,
                        poss_diseases, examined_symptoms)
        examined_symptoms.add(next_symptom)
        check = input(f"Are you experiencing {next_symptom}? (y/n) ")
        if check == "y":
            poss_diseases, ign_diseases = diagnoser.narrow_from_symptom(next_symptom,
                                            poss_diseases, ign_diseases)
        if check == "n":
            poss_diseases, ign_diseases = diagnoser.narrow_from_not_symptom(next_symptom,
                                            poss_diseases, ign_diseases)
    
    if len(poss_diseases) == 0:
        print("Sorry, unable to identify the cause of your symptoms.")
    else:
        print(f"You have {list(poss_diseases)[0]}.")

if __name__ == "__main__":
    diagnoser = DiagnoseDisease('bolt://localhost:7687','neo4j','hellohello')
    set_up = False
    run_alexa = True
    if set_up: set_up_program(diagnoser)
    if run_alexa: run_alexa_program(diagnoser)
    diagnoser.close()