from flask import Blueprint, request, jsonify
from models import db, Product

api = Blueprint('api', __name__)

# получить все товары или создать новый
@api.route('/products', methods=['GET', 'POST'])
def api_products():
    # get - получить список всех товаров в формате json
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'category': p.category,
            'image_url': p.image_url
        } for p in products])
    
    # post - создать новый товар
    data = request.get_json()
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'error': 'name и price обязательны'}), 400
    
    p = Product(
        name=data['name'],
        price=data['price'],
        category=data.get('category', 'Общее'),
        image_url=data.get('image_url', '')
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'message': 'created'}), 201

# работа с конкретным товаром
@api.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_product(id):
    p = db.session.get(Product, id)
    if not p:
        return jsonify({'error': 'not found'}), 404
    
    # get - получить один товар
    if request.method == 'GET':
        return jsonify({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'category': p.category,
            'image_url': p.image_url
        })
    
    # put - обновить товар
    if request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'no data'}), 400
        p.name = data.get('name', p.name)
        p.price = data.get('price', p.price)
        p.category = data.get('category', p.category)
        p.image_url = data.get('image_url', p.image_url)
        db.session.commit()
        return jsonify({'message': 'updated'})
    
    # delete - удалить товар
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'deleted'})