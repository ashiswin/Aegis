var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
})

con.connect();

exports.read_routine_from_id = function (req, res, next) {
    // Return all Routine
    if (typeof(req.query) === "undefined" || typeof (req.query.id) === "undefined") {
        var query = "SELECT * FROM Routine WHERE `isDeleted` = FALSE";
    }
    //Return only the Routine with the given routineId
    else {
        var query = "SELECT * FROM Routine WHERE `id` = \"" +
            req.query.id + "\" AND `isDeleted` = FALSE";
    }
    console.log(query);
    con.query(query, function (err, result) {
        if (err) throw err;
        res.json(result);
        console.log(result);
    });
}

exports.read_routine_by_workout = function (req, res, next) {
    var check_query = "SELECT routineId FROM RoutineWorkoutRelationship WHERE `workoutId` = \'" + req.query.workoutId + "\' AND `isDeleted` = FALSE";
    con.query(check_query, function (err, result) {
        if (err) throw err;
        if (result != null && result.length > 0) {
            var routineIds = [];
            for (i = 0; i < result.length; i++) {
                if (!routineIds.includes(result[i].routineId)) {
                    routineIds.push(result[i].routineId);
                }
            }
            var query = "SELECT * FROM Routine WHERE id IN (" + routineIds.toString() + ")";
            con.query(query, function (err2, result2) {
                if (err2) throw err2;
                res.json(result2);
            });
        }
        else {
            res.send("No routine with workoutId " + req.query.workoutId);
        }
    });
}

exports.create_routine = function (req, res, next) {
    var query = "INSERT INTO Routine (`name`, `type`) VALUES (\'"
        + req.query.name + "\', \'" + req.query.type + "\')";
    con.query(query, function (err, result) {
        if (err) throw err;
        if (result.affectedRows === 1) {
            var query2 = "SELECT * FROM Routine WHERE `id` = \"" + result.insertId + "\"";
            console.log(query2);
            con.query(query2, function (err2, result2) {
                res.json(result2)
            })
        }
        else {
            console.log("Cannot find created Routine");
            res.send("Cannot find created Routine");
        }
    });
}

exports.update_routine = function (req, res, next) {
    //TODO
}

exports.delete_routine = function (req, res, next) {
    //TODO
}