var express = require('express');
var router = express.Router();
var routineController = require('../controllers/routineController.js');

router.get('/', routineController.read_routine_from_id);
router.get('/workout', routineController.read_routine_by_workout);
router.post('/create', routineController.create_routine);
router.post('/edit', routineController.update_routine);
router.post('/delete', routineController.delete_routine);

module.exports = router;