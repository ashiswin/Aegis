var mysql = require('mysql');
var con = mysql.createConnection({
    host: "devostrum.no-ip.info", 
    user: "aegis", 
    password: "aegis", 
    database: "aegis"
})

exports.read_user_from_nric = function (req, res, next) {
    con.connect(function (err) {
        if (err) throw err;
        console.log("SELECT * FROM User WHERE `nric` = \"" + req.query.nric + "\" WHERE isDeleted = FALSE");
        con.query("SELECT * FROM User WHERE `nric` = \"" + req.query.nric + "\" AND isDeleted = FALSE", function (err, result) {
            if (err) throw err;
            res.json(result);
            console.log(result);
        });
    });
}