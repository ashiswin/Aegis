var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
})

exports.read_routine_from_id = function (req, res, next) {
    con.connect(function (err) {
        if (err) console.log(err);
        // Return all Routine
        if (typeof(req.query.id) == "undefined") {
            var query = "SELECT * FROM Routine WHERE isDeleted = FALSE";
        }
        //Return only the Routine with the given routineId
        else {
            var query = "SELECT * FROM Routine WHERE `id` = \"" +
                req.query.id + "\" AND isDeleted = FALSE";
        }
        con.query(query, function (err, result) {
            if (err) throw err;
            res.json(result);
            console.log(result);
        });
    });
}

exports.read_routine_by_workout = function (req, res, next) {
    con.connect(function (err) {
        // TODO
    })
}

exports.create_routine = function (req, res, next) {
    con.connect(function (err) {
        if (err) console.log(err);
        var query = "INSERT INTO Routine (`name`, `type`) VALUES (\'"
            + req.query.name + "\', \'" + req.query.type + "\')";
        con.query(query, function (err, result) {
            if (err) throw err;
            if (result.affectedRows == 1) {
                query2 = "SELECT * FROM Routine WHERE `id` = \"" + result.insertId + "\"";
                console.log(query2);
                con.query(query2, function (err2, result2) {
                    res.json(result2)
                })
            }
            else {
                res.send("Cannot find created Routine");
            }
        });
    });
}

exports.update_routine = function (req, res, next) {
    con.connect(function (err) {
        // TODO
    });
}

exports.delete_routine = function (req, res, next) {
    con.connect(function (err) {
    // TODO
    }); 
}