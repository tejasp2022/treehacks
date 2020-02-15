var neo4j = require('neo4j-driver').v1;

var driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'hellohello'));
var session = driver.session();

function addGroup(group) {
	session
           .run('CREATE (n:Group { groupName: \'' + group.groupName + '\'})')
           .catch(function (err) {
               console.log(err);
           })
           .then(function () {
               console.log('success')
           });
}