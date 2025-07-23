const db = require('../config/db');

class MeteoController {
    static async getAllData(req, res) {
        try {
            const [rows] = await db.query('SELECT * FROM bme ORDER BY date DESC');
            res.json(rows);
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }

    static async getData(req, res) {
        try {
            const [rows] = await db.query('SELECT * FROM bme WHERE id = ?', [req.params.id]);
            if (rows.length > 0) {
                res.json(rows[0]);
            } else {
                res.status(404).json({ message: 'Données non trouvées' });
            }
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }

    static async createData(req, res) {
        try {
            const { temperature, humidity, pressure } = req.body;
            const [result] = await db.query(
                'INSERT INTO bme (temperature, humidity, pressure, date) VALUES (?, ?, ?, NOW())',
                [temperature, humidity, pressure]
            );
            res.status(201).json({ id: result.insertId });
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }

    static async updateData(req, res) {
        try {
            const { temperature, humidity, pressure } = req.body;
            await db.query(
                'UPDATE bme SET temperature = ?, humidity = ?, pressure = ? WHERE id = ?',
                [temperature, humidity, pressure, req.params.id]
            );
            res.json({ message: 'Données mises à jour' });
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }

    static async deleteData(req, res) {
        try {
            await db.query('DELETE FROM bme WHERE id = ?', [req.params.id]);
            res.json({ message: 'Données supprimées' });
        } catch (error) {
            res.status(500).json({ message: error.message });
        }
    }
}

module.exports = MeteoController;
