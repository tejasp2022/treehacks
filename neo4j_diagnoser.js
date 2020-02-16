var neo4j = require('neo4j-driver');
var parser = require('parse-neo4j');

var driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'hellohello'));
var session = driver.session();

var symptoms = new Set();
var poss_diseases = new Set();
var ign_diseases = new Set();
var examined_symptoms = new Set();

async function get_nodes(node_type) {
    await session
        .run("MATCH (n:" + node_type + ") RETURN n.name")
        .catch((err) => {
            console.log('Error:' + err);
        })
        .then(parser.parse)
        .then((result) => {
            if (node_type == "Symptom") {
                result.forEach(function(item){
                    symptoms.add(item)
                })
            } else {
                result.forEach(function(item){
                    poss_diseases.add(item)
                })
            }
        });

        
};

function array_to_str(poss_diseases) {
    var output = "["
    const diseases_array = Array.from(poss_diseases);
    for (let i = 0; i < diseases_array.length; i++){
        if (i == 0) {
            output = output.concat("'", diseases_array[i], "'")
        } else {
            output = output.concat(", '", diseases_array[i] + "'")
        }
    }
    output = output.concat("]");
    return output;
};

async function count_max(symptom_counts) {
    var max_count = 0;
    var max_elem = null;
    for (let i = 0; i < symptom_counts.length; i++) {
        symptom_value = symptom_counts[i];
        if (symptom_value[1] >= max_count) {
            max_count = symptom_value[1];
            max_elem = symptom_value[0];
        };
    };
    console.log(max_elem);
    return max_elem;
};

async function select_next_symptom() {
    var symptom_counts = [];
    var symptom;
    const symptoms_to_consider = new Set([...symptoms].filter(i => !examined_symptoms.has(i)));
    const symptoms_array = Array.from(symptoms_to_consider);
    if (poss_diseases.size == 0) {
        return "Sorry, unable to provide a diagnosis for your symptoms."
    } else if (poss_diseases.size == 1) {
        return "Your diagnosis is: " + poss_diseases.values().next().value
    }
    for (let i = 0; i < symptoms_array.length; i++) {
        symptom = symptoms_array[i];
        disease_str = array_to_str(poss_diseases);
        await session
            .run("MATCH (a:Symptom),(b:Disease) WHERE (a)-[:IS_SYMPTOM_OF]->(b) AND a.name='" + symptom + "' AND b.name IN " + disease_str + " RETURN COUNT(b)")
            .catch((err) => {
                console.log('Error:' + err);
            })
            .then(parser.parse)
            .then((result) => {
                symptom_counts.push([symptom,result[0]]);
            });
    }
    return count_max(symptom_counts);
}

async function process_first_symptom(symptom) {
    return narrow_from_symptom(symptom);
}

async function narrow_from_symptom(symptom) {
    examined_symptoms.add(symptom);
	await session
        .run('MATCH (a:Symptom),(b:Disease) WHERE (a)-[:IS_SYMPTOM_OF]->(b) and a.name="' + symptom + '" RETURN b.name')
        .catch((err) => {
            console.log('Error:' + err);
        })
        .then(parser.parse)
        .then((result) => {
            const new_diseases = new Set(result);
            const new_ign_diseases = new Set([...poss_diseases].filter(i => !new_diseases.has(i)));
            poss_diseases = new Set([...poss_diseases].filter(i => new_diseases.has(i)));
            ign_diseases = new Set([...ign_diseases, ...new_ign_diseases]);
        });
    var next = await select_next_symptom();
    return next;
}

async function narrow_from_not_symptom(symptom) {
    examined_symptoms.add(symptom);
	await session
        .run('MATCH (a:Symptom),(b:Disease) WHERE (a)-[:IS_SYMPTOM_OF]->(b) and a.name="' + symptom + '" RETURN b.name')
        .catch((err) => {
            console.log('Error:' + err);
        })
        .then(parser.parse)
        .then((result) => {
            const not_diseases = new Set(result);
            poss_diseases = new Set([...poss_diseases].filter(i => !not_diseases.has(i)));
            ign_diseases = new Set([...ign_diseases, ...not_diseases]);
        });
    var next = await select_next_symptom();
    return next;
}

async function process_next_symptom(symptom, answer) {
    var next;
    if (answer) { 
        next = await narrow_from_symptom(symptom);
    } else {
        next = await narrow_from_not_symptom(symptom);
    }
    return next;
}

async function caller() {
    console.log(poss_diseases, ign_diseases, examined_symptoms);
    await get_nodes("Symptom");
    await get_nodes("Disease");
    console.log(poss_diseases, ign_diseases, examined_symptoms);
    var next_symptom = await process_first_symptom("Chest Pain");
    console.log(poss_diseases, ign_diseases, examined_symptoms);
    console.log(next_symptom);
    next_symptom = await process_next_symptom(next_symptom, false);
    console.log(poss_diseases, ign_diseases, examined_symptoms);
    console.log(next_symptom);
    /*next_symptom = await process_next_symptom(next_symptom, false);
    console.log(poss_diseases, ign_diseases, examined_symptoms);
    console.log(next_symptom);*/
    driver.close();
}

caller();

