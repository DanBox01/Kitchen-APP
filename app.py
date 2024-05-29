# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytesseract
from PIL import Image

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kitchen_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Ingredient model
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'expiration_date': self.expiration_date.strftime('%Y-%m-%d') if self.expiration_date else None
        }

# Route to get all ingredients
@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    try:
        ingredients = Ingredient.query.all()
        return jsonify([ingredient.to_dict() for ingredient in ingredients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to add a new ingredient
@app.route('/ingredients', methods=['POST'])
def add_ingredient():
    try:
        data = request.json
        ingredient = Ingredient(
            name=data['name'],
            quantity=data['quantity'],
            expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d') if data.get('expiration_date') else None
        )
        db.session.add(ingredient)
        db.session.commit()
        return jsonify(ingredient.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to update an ingredient
@app.route('/ingredients/<int:id>', methods=['PUT'])
def update_ingredient(id):
    try:
        ingredient = Ingredient.query.get(id)
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        data = request.json
        ingredient.name = data.get('name', ingredient.name)
        ingredient.quantity = data.get('quantity', ingredient.quantity)
        ingredient.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d') if data.get('expiration_date') else ingredient.expiration_date

        db.session.commit()
        return jsonify(ingredient.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to delete an ingredient
@app.route('/ingredients/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    try:
        ingredient = Ingredient.query.get(id)
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        db.session.delete(ingredient)
        db.session.commit()
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to upload a receipt image and extract text
@app.route('/upload-receipt', methods=['POST'])
def upload_receipt():
    try:
        file = request.files['receipt']
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)
        # Process the text and update inventory
        return jsonify({'text': text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to create the Flask application
def create_app():
    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
