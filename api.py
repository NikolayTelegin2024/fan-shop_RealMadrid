from flask import Blueprint, request, jsonify
from models import db, Product

api = Blueprint('api', __name__)

@api.route('/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'image_url': p.image_url} for p in Product.query.all()])
    data = request.json
    p = Product(name=data['name'], price=data['price'], category=data.get('category', 'Общее'), image_url=data.get('image_url', ''))
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id}), 201

@api.route('/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_product(id):
    p = db.session.get(Product, id)
    if not p:
        return jsonify({'error': 'not found'}), 404
    if request.method == 'GET':
        return jsonify({'id': p.id, 'name': p.name, 'price': p.price, 'image_url': p.image_url})
    if request.method == 'PUT':
        data = request.json
        p.name = data.get('name', p.name)
        p.price = data.get('price', p.price)
        p.image_url = data.get('image_url', p.image_url)
        db.session.commit()
        return jsonify({'message': 'updated'})
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'deleted'})