from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    brand = db.Column(db.String(40))
    status = db.Column(db.Integer)
    cost_price = db.Column(db.Float)
    supplier = db.Column(db.String(80))
    unit = db.Column(db.String(6))
    specification = db.Column(db.String(40))
    barcode = db.Column(db.String(80))
    remark = db.Column(db.String(80))
    attribute1 = db.Column(db.String(80))
    attribute2 = db.Column(db.String(80))
    attribute3 = db.Column(db.String(80))
    attribute4 = db.Column(db.String(80))
    attribute5 = db.Column(db.String(80))
    in_time = db.Column(db.DateTime)
    out_time = db.Column(db.DateTime)
    list_price = db.Column(db.Float)
    sales_price = db.Column(db.Float)
    salesperson = db.Column(db.String(12))
    abandonment_time = db.Column(db.DateTime)

    def __init__(self, name, category, brand=None, status=None, cost_price=None, supplier=None, unit=None,
                 specification=None, barcode=None, remark=None, attribute1=None, attribute2=None, attribute3=None,
                 attribute4=None, attribute5=None, in_time=None, out_time=None, list_price=None, sales_price=None, salesperson=None, abandonment_time=None):
        self.name = name
        self.category = category
        self.brand = brand
        self.status = status
        self.cost_price = cost_price
        self.supplier = supplier
        self.unit = unit
        self.specification = specification
        self.barcode = barcode
        self.remark = remark
        self.attribute1 = attribute1
        self.attribute2 = attribute2
        self.attribute3 = attribute3
        self.attribute4 = attribute4
        self.attribute5 = attribute5
        self.in_time = in_time
        self.out_time = out_time
        self.list_price = list_price
        self.sales_price = sales_price
        self.salesperson = salesperson
        self.abandonment_time = abandonment_time

    def json(self):
        return {'id': self.id, 'name': self.name, 'category': self.category, 'brand': self.brand,
                'status': self.status, 'cost_price': self.cost_price, 'supplier': self.supplier, 'unit': self.unit,
                'specification': self.specification, 'barcode': self.barcode, 'remark': self.remark,
                'attribute1': self.attribute1, 'attribute2': self.attribute2, 'attribute3': self.attribute3,
                'attribute4': self.attribute4, 'attribute5': self.attribute5, 'in_time': str(self.in_time),
                'out_time': str(self.out_time),'abandonment_time': str(self.abandonment_time),'list_price': str(self.list_price),'sales_price': str(self.sales_price),'salesperson': str(self.salesperson)}


    @classmethod
    def get_product_by_id(cls, product_id):
        return cls.query.filter_by(id=product_id).first()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
