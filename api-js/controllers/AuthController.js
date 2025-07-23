const jwt = require('jsonwebtoken');

class AuthController {
    static login(req, res) {
        // Dans un cas réel, vérifiez les credentials dans la base de données
        const user = {
            id: 1,
            username: 'admin'
        };

        const token = jwt.sign(
            { userId: user.id },
            process.env.JWT_SECRET,
            { expiresIn: process.env.JWT_EXPIRES_IN }
        );

        res.json({
            token,
            user: {
                id: user.id,
                username: user.username
            }
        });
    }
}

module.exports = AuthController;
