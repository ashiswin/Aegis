var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
});

con.connect();

exports.read_user_from_id = function (req, res, next) {
    con.query("SELECT * FROM User WHERE `id` = \"" + req.query.nric + "\" AND isDeleted = FALSE", function (err, result) {
        if (err) throw err;
        res.json(result);
        console.log(result);
    });
}

exports.read_user_from_nric = function (req, res, next) {
    var query = "SELECT * FROM User WHERE `nric` = \"" + req.query.nric + "\" AND isDeleted = FALSE";
    con.query(query, function (err, result) {
        if (err) throw err;
        res.json(result);
        console.log(result);
    });
}

exports.add_score = function (req, res, next) {
    if (req.query.score != null && req.query.userId != null) {
        var user_query = "SELECT * FROM User WHERE `id` = \'" + req.query.userId + "\'";
        con.query(user_query, function (err, result) {
            if (err) throw err;
            var new_score = parseInt(result[0].points) + parseInt(req.query.score);
            var update_query = "UPDATE User SET `points` = \'" + new_score + "\' WHERE `id` = \'" + req.query.userId + "\'";
            console.log(result);
            console.log(update_query);
            con.query(update_query, function (err2, result2) {
                if (err) throw err;
                console.log(result2); // gives undefined
                if (typeof (result2) === "undefined") {
                    res.send("Row not updated")
                }
                else if (result2.affectedRows == 1) {
                    return_query = "SELECT * FROM User WHERE `id` = \'" + req.query.userId + "\'";
                    con.query(return_query, function (err3, result3) {
                        res.json(result3);
                    })
                }
                else {
                    res.send("Row not updated");
                }
            });
        });
    }
    else {
        res.send("userId or score not provided");
    }
}

exports.add_result_score = function (req, res, next) {
    
}