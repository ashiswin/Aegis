var express = require('express');
var router = express.Router();
var resultController = require('../controllers/resultController');

router.get('/', resultController.read_result_from_id);
router.get('/user', resultController.read_result_by_user);
router.get('/create', resultController.create_result);

module.exports = router;