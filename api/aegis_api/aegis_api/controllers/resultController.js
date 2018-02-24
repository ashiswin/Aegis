var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info",
    user: "aegis",
    password: "aegis",
    database: "aegis"
});


exports.read_result_from_id = function (req, res, next) {
    con.connect(function (err) {
        // TODO
    })
}

exports.read_result_by_user = function (req, res, next) {
    con.connect(function (err) {
        // TODO
    })
}

exports.create_result = function (req, res, next) {
    con.connect(function (err) {
        // TODO
    })
}