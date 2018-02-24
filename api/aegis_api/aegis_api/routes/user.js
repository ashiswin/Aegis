var express = require('express');
var router = express.Router();
var userController = require('../controllers/userController');

router.get('/', userController.read_user_from_nric);

module.exports = router;