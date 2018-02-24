var express = require('express');
var router = express.Router();
var userController = require('../controllers/userController');

router.get('/', userController.read_user_from_id);
router.get('/nric', userController.read_user_from_nric);
router.post('/add_score', userController.add_score);
router.post('/add_result_score', userController.add_result_score);

module.exports = router;