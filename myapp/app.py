from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytesseract
from PIL import Image
import random
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kitchen_inventory.db'
db = SQLAlchemy(app)

# Specify the path to Tesseract if not in PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = Ingredient.query.all()
    return jsonify([ingredient.to_dict() for ingredient in ingredients])

@app.route('/ingredients', methods=['POST'])
def add_ingredient():
    data = request.json
    ingredient = Ingredient(
        name=data['name'],
        quantity=data['quantity'],
        expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d') if data.get('expiration_date') else None
    )
    db.session.add(ingredient)
    db.session.commit()
    return jsonify(ingredient.to_dict()), 201

@app.route('/ingredients/<int:id>', methods=['PUT'])
def update_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error': 'Ingredient not found'}), 404
    
    data = request.json
    ingredient.name = data.get('name', ingredient.name)
    ingredient.quantity = data.get('quantity', ingredient.quantity)
    ingredient.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d') if data.get('expiration_date') else ingredient.expiration_date

    db.session.commit()
    return jsonify(ingredient.to_dict())

@app.route('/ingredients/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error': 'Ingredient not found'}), 404
    
    db.session.delete(ingredient)
    db.session.commit()
    return '', 204

@app.route('/upload-receipt', methods=['POST'])
def upload_receipt():
    file = request.files['receipt']
    image = Image.open(file.stream)
    text = pytesseract.image_to_string(image)
    
    # Process the text and extract ingredients
    lines = text.split('\n')
    for line in lines:
        match = re.match(r'(\d+)\s+(\w+)', line)
        if match:
            quantity = float(match.group(1))
            name = match.group(2).lower()
            # Update inventory
            ingredient = Ingredient.query.filter_by(name=name).first()
            if ingredient:
                ingredient.quantity += quantity
            else:
                new_ingredient = Ingredient(name=name, quantity=quantity)
                db.session.add(new_ingredient)
            db.session.commit()
    
    return jsonify({'message': 'Inventory updated successfully'})

@app.route('/meal-plan', methods=['GET'])
def meal_plan():
    ingredients = Ingredient.query.all()
    meals = []
    for i in range(7):  # 7 days in a week
        meal_ingredients = random.sample(ingredients, min(3, len(ingredients)))
        meal = {'day': i + 1, 'ingredients': [ingredient.name for ingredient in meal_ingredients]}
        meals.append(meal)
    
    return jsonify(meals)

@app.route('/grocery-list', methods=['GET'])
def grocery_list():
    required_ingredients = request.args.getlist('ingredients')
    grocery_list = []
    
    for item in required_ingredients:
        ingredient = Ingredient.query.filter_by(name=item.lower()).first()
        if not ingredient or ingredient.quantity == 0:
            grocery_list.append({'name': item, 'quantity': 1})  # Default quantity
    
    return jsonify(grocery_list)

def create_app():
    db.create_all()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
