var express = require('express');
var router = express.Router();
var workoutController = require('../controllers/workoutController.js');

router.get('/', workoutController.read_workout_from_id);
router.get('/routine', workoutController.read_workout_by_routine);
router.get('/create', workoutController.create_workout);
router.get('/link', workoutController.link_workout_to_routine);
router.get('/edit', workoutController.update_workout);
router.get('/delete', workoutController.delete_workout);

module.exports = router;