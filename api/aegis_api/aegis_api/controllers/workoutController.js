var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
});

con.connect();

exports.read_workout_from_id = function (req, res, next) {
    // Return all Workout
    if (typeof (req.query.id) == "undefined") {
        var query = "SELECT * FROM Workout WHERE isDeleted = FALSE";
    }
    // Return only Workout with given workoutId
    else {
        var query = "SELECT * FROM Workout WHERE `id` = \"" +
            req.query.id + "\" AND isDeleted = FALSE";
    }
    con.query(query, function (err, result) {
        if (err) throw err;
        res.json(result);
        console.log(result);
    });
}

exports.read_workout_by_routine = function (req, res, next) {
    var check_query = "SELECT workoutId FROM RoutineWorkoutRelationship WHERE `routineId` = \'" + req.query.routineId + "\' AND isDeleted = FALSE";
    console.log(check_query);
    con.query(check_query, function (err, result) {
        if (err) throw err;
        console.log(result);
        if (result != null && result.length > 0) {
            var workoutIds = [];
            for (i = 0; i < result.length; i++) {
                if (!workoutIds.includes(result[i].workoutId)) {
                    workoutIds.push(result[i].workoutId);
                }
            }
            var query = "SELECT * FROM Workout WHERE id IN (" + workoutIds.toString() + ")";
            con.query(query, function (err2, result2) {
                if (err2) throw err2;
                res.json(result2);
            });
        }
        else {
            res.send("No workout with routineId " + req.query.routineId);
        }
    });
}

exports.create_workout = function (req, res, next) {
    var query = "INSERT INTO Workout (`name`, `bodyPart`) VALUES (\'"
        + req.query.name + "\', \'" + req.query.bodyPart + "\')";
    con.query(query, function (err, result) {
        if (err) throw err;
        if (result.affectedRows == 1) {
            query2 = "SELECT * FROM Workout WHERE `id` = \'" + result.insertId + "\'";
            console.log(query2);
            con.query(query2, function (err2, result2) {
                res.json(result2);
            })
        }
        else {
            res.send("Cannot find created Workout");
        }
    });
}

exports.link_workout_to_routine = function (req, res, next) {
    var check_query = "SELECT id FROM RoutineWorkoutRelationship WHERE `routineId` = \'" +
        req.query.routineId + "\' AND " + "`workoutId` = \'" + req.query.workoutId + "\'";
    var query = "INSERT INTO RoutineWorkoutRelationship (`routineId`, `workoutId`) VALUES (\'" + req.query.routineId + "\', \'" + req.query.workoutId + "\')";

    console.log(check_query);
    con.query(check_query, function (err, result) {
        if (err) throw err;
        console.log(result);
        if (result.length == 0) {
            console.log(query);
            con.query(query, function (err2, result2) {
                if (err2) throw err2;
                if (result2.affectedRows === 1) {
                    query3 = "SELECT * FROM RoutineWorkoutRelationship WHERE `id` = \'" +
                        result2.insertId + "\'";
                    console.log(query3);
                    con.query(query3, function (err3, result3) {
                        res.json(result3);
                    })
                }
                else {
                    res.send("Cannot find created RoutineWorkoutRelationship");
                }
            });
        }
        else {
            console.log("Relationship already exist");
            res.send("Relationship already exist");
        }
    });
}

exports.update_workout = function (req, res, next) {
    // TODO
}

exports.delete_workout = function (req, res, next) {
    // TODO
}