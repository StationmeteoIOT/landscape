const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const MeteoController = require('../controllers/MeteoController');

// Routes publiques
router.get('/', MeteoController.getAllData);
router.get('/:id', MeteoController.getData);

// Routes protégées
router.post('/', auth, MeteoController.createData);
router.put('/:id', auth, MeteoController.updateData);
router.delete('/:id', auth, MeteoController.deleteData);

module.exports = router;
