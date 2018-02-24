var express = require('express');
var router = express.Router();
var workoutController = require('../controllers/workoutController.js');

router.get('/', workoutController.read_workout_from_id);
router.get('/routine', workoutController.read_workout_by_routine);
router.post('/create', workoutController.create_workout);
router.post('/link', workoutController.link_workout_to_routine);
router.post('/edit', workoutController.update_workout);
router.post('/delete', workoutController.delete_workout);

module.exports = router;