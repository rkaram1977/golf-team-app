from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)  # Aumentado para 255 caracteres
    handicap = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, default=0) # Pontuação por vitórias
    games_played = db.Column(db.Integer, default=0) # Quantas vezes participou do sorteio

    def __repr__(self):
        return f'<Player {self.name}>'

    # Função auxiliar para calcular o handicap ponderado individual
    def get_weighted_handicap(self):
        hcp = self.handicap
        if 0 <= hcp <= 10: # Categoria A
            return hcp * 0.25
        elif 11 <= hcp <= 18: # Categoria B
            return hcp * 0.20
        elif 19 <= hcp <= 27: # Categoria C
            return hcp * 0.15
        elif hcp >= 28: # Categoria D
            return hcp * 0.10
        else: # Caso de handicap inválido (embora a validação deva prevenir isso)
            return 0
