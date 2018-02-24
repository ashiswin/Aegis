var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
});

con.connect();

exports.read_result_from_id = function (req, res, next) {
    // Return all Result
    if (typeof (req.query.id) == "undefined") {
        var query = "SELECT * FROM Result WHERE isDeleted = FALSE";
    }
    //Return only the Result with the given routineId
    else {
        var query = "SELECT * FROM Result WHERE `id` = \"" +
            req.query.id + "\" AND isDeleted = FALSE";
    }
    con.query(query, function (err, result) {
        if (err) throw err;
        res.json(result);
        console.log(result);
    });
}

exports.read_result_by_user = function (req, res, next) {
    var query = "SELECT * FROM Result WHERE userId = \'" + req.query.userId + "\' AND isDeleted = FALSE";
    con.query(query, function (err, result) {
        res.json(result);
        console.log(result);
    });
}

exports.create_result = function (req, res, next) {
    var query = "INSERT INTO Result (`name`, `userId`, `workoutId`, `score`, `routineId`) VALUES (\'" +
        req.query.name + "\', \'" +
        req.query.userId + "\', \'" +
        req.query.workoutId + "\', \'" +
        req.query.score + "\', \'" +
        req.query.routineId + "\')";
    con.query(query, function (err, result) {
        if (err) throw err;
        if (result.affectedRows == 1) {
            query2 = "SELECT * FROM Result WHERE `id` = \"" + result.insertId + "\"";
            console.log(query2);
            con.query(query2, function (err2, result2) {
                res.json(result2)
            })
        }
        else {
            res.send("Cannot find created Result");
        }
    });
}