var neo4j = require('neo4j-driver');

var driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'hellohello'));
var session = driver.session();

var symptoms = new Set();
var poss_diseases = new Set();
var ign_diseases = new Set();

async function get_nodes(node_type) {
    const result = await session
        .run("MATCH (n:'" + node_type + "') RETURN n.name")
        .catch(function (err){
            console.log("Error: " + err);
        })
        .then(function (){
            console.log("Success");
        });
};
/*
function process_first_symptom(symptom) {
	session
           .run('CREATE (n:Group { groupName: \'' + group.groupName + '\'})')
           .catch(function (err) {
               console.log(err);
           })
           .then(function () {
               console.log('success')
           });
}
*/

get_nodes("Symptom");
driver.close();