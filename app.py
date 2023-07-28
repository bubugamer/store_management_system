import base64
import datetime as dt
import json

from barcode import Code128
from barcode.writer import ImageWriter
from barcode import EAN13
from barcode.writer import ImageWriter
from flask import Flask, render_template, request, redirect, jsonify, session, flash
from flask import Response
from io import BytesIO
from models.product import Product, db
from util import Util

app = Flask(__name__)
app.secret_key = '0123456789' #session数据的密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/workspace/dgmmansys/data/dgm.db' #指定数据库文件地址
db.init_app(app)

# 检查数据库连接
try:
    db.session.execute('SELECT 1')
    print('Database connection established')
except:
    print('Database connection failed')


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 商品列表路由
@app.route('/products_list', methods=['GET', 'POST'])
def products_list():
    # 获取在库商品列表
    products = Product.query.filter_by(status=1).all()

    #获取出库和报废商品数据
    # soldandscraps = Product.query.filter((Product.status == 2) | (Product.status == 3)).all()

    #获取已卖商品数据
    solds = Product.query.filter_by(status=2).all()

    #获取报废商品数据
    abandonments = Product.query.filter_by(status=3).all()


    # 计算同名商品的数量
    quantity_dict = {}
    for product in products:
        if product.name in quantity_dict:
            quantity_dict[product.name] += 1
        else:
            quantity_dict[product.name] = 1

    return render_template('products_list.html', products=products, solds=solds, abandonments=abandonments, quantity_dict=quantity_dict)

# 商品入库路由
@app.route('/product/add/<category>', methods=['GET'])
def add_product(category):
    # 生成条形码
    barcode = Util.generate_barcode()

    return render_template('add_product.html', barcode=barcode, category=category)

@app.route('/submit_product', methods=['POST'])
def submit_product():
    try:
        quantity = request.form['quantity']
        category = request.form['category']
        brand = request.form['brand']
        # 商品状态码：1-新入库，2-销售出库，3-报废出库
        status = 1
        cost_price = request.form['cost_price']
        list_price = request.form['list_price']
        supplier = request.form['supplier']
        unit = request.form['unit']
        specification = request.form['specification']
        barcode128 = str(Code128(request.form['rawbarcode']))
        remark = request.form['remark']
        attribute1 = request.form.get('attribute1', '')
        attribute2 = request.form.get('attribute2', '')
        attribute3 = request.form.get('attribute3', '')
        attribute4 = request.form.get('attribute4', '')
        attribute5 = request.form.get('attribute5', '')
        #salesperson = request.form.get('salesperson', '')#初始化为空字符串，避免等于None
        now = dt.datetime.now()
        name = request.form['name']
        if name == "" or None:
            if category == 'Lens':
                category_c='镜片'
            elif category == 'Frame':
                category_c = '镜架'
            elif category == 'Contact Lens':
                category_c = '隐形眼镜'
            elif category == 'Sunglasses':
                category_c = '太阳镜'
            elif category == 'Other':
                category_c = '配件/护理液等'
            else :
                category_c = '未知'
            name = brand + category_c + specification

        for i in range(int(quantity)):
            new_product = Product(name=name, category=category, brand=brand, status=status, cost_price=cost_price,
                                  supplier=supplier, unit=unit, specification=specification,list_price=list_price,
                                  barcode=barcode128, remark=remark, attribute1=attribute1, attribute2=attribute2,
                                  attribute3=attribute3, attribute4=attribute4, attribute5=attribute5, in_time=now, salesperson='')
            new_product.save_to_db()

        # 保存之前填写的信息
        session['name'] = name
        session['category'] = category
        session['brand'] = brand
        session['cost_price'] = cost_price
        session['list_price'] = list_price
        session['supplier'] = supplier
        session['unit'] = unit
        session['specification'] = specification
        session['remark'] = remark
        session['attribute1'] = attribute1
        session['attribute2'] = attribute2
        session['attribute3'] = attribute3
        session['attribute4'] = attribute4
        session['attribute5'] = attribute5

        return jsonify({'success': True, 'message': 'Product added successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/add_stock/<int:product_id>', methods=['POST'])
def add_stock(product_id):
    try:
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({'success': False, 'message': 'error'})
        now = dt.datetime.now()
        # 复制一份商品记录
        new_product = Product(name=product.name, category=product.category, brand=product.brand, status=product.status, cost_price=product.cost_price,
                              supplier=product.supplier, unit=product.unit, specification=product.specification, list_price=product.list_price,
                              barcode=product.barcode, remark=product.remark, attribute1=product.attribute1, attribute2=product.attribute2,
                              attribute3=product.attribute3, attribute4=product.attribute4, attribute5=product.attribute5, in_time=now,
                              salesperson=product.salesperson)

        db.session.add(new_product)
        db.session.commit()
        # 返回新商品的库存数量
        return jsonify({'success': True, 'message': 'stock added successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/barcode/<barcode>', methods=['GET'])
def barcode_image(barcode):
    # 生成Code128格式的条形码
    #barcode128 = Code128(barcode, writer=ImageWriter())
    ean = EAN13(barcode, writer=ImageWriter())

    # 将条形码转换为字节流
    buffer = BytesIO()
    ean.write(buffer, options={'scale': 0.1})
    # 返回条形码图片
    return Response(buffer.getvalue(), mimetype='image/png')

# 商品销售出库路由
@app.route('/sell_product', methods=['POST'])
def sell_product():
    try:
        out_time = request.form.get('out_time')
        if not out_time:
            out_time = dt.datetime.now()
        else:
            out_time = dt.datetime.fromisoformat(out_time)
        salesPerson = request.form.get('salesPerson')
        sales_price = request.form.get('sell_price')
        print(type(sales_price))
        if not sales_price:
            sales_price = '0.00'

        print("salesPerson:" + salesPerson + " sales_price:" + sales_price)

        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        if product:
            product.update(status=2, out_time=out_time, salesperson=salesPerson, sales_price=sales_price)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Product not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# 商品报废出库路由
@app.route('/discard_product', methods=['POST'])
def discard_product():
    try:
        abandonment_time = request.form.get('abandonment_time')
        if not abandonment_time:
            abandonment_time = dt.datetime.now()
        else:
            abandonment_time = dt.datetime.fromisoformat(abandonment_time)
        remark = request.form.get('remark','')
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        if product:
            product.update(status=3, abandonment_time=abandonment_time, remark=remark)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Product not found'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/get_product_info', methods=['GET'])
def get_product_info():
    product_id = request.args.get('product_id')
    product = Product.query.get(product_id)
    if product:
        # Generate barcode image
        if product.barcode:
            # 生成Code128格式的条形码
            barcode128 = Code128(product.barcode, writer=ImageWriter())
            # 将条形码转换为字节流
            buffer = BytesIO()
            barcode128.write(buffer, options={'scale': 0.1})
            barcode_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            barcode_img = ''
        data = {
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'cost_price': product.cost_price,
            'supplier': product.supplier,
            'list_price': product.list_price,
            'sales_price': product.sales_price,
            'salesperson': product.salesperson,
            'unit': product.unit,
            'specification': product.specification,
            'barcode': barcode_img,
            'remark': product.remark,
            'attribute1': product.attribute1,
            'attribute2': product.attribute2,
            'attribute3': product.attribute3,
            'attribute4': product.attribute4,
            'attribute5': product.attribute5,
            'in_time': product.in_time.strftime('%Y-%m-%d %H:%M:%S') if product.in_time else '',
            'out_time': product.out_time.strftime('%Y-%m-%d %H:%M:%S') if product.out_time else '',
            'abandonment_time': product.abandonment_time.strftime('%Y-%m-%d %H:%M:%S') if product.abandonment_time else '',
        }
        return jsonify({'status': 'success', 'data': data})
    else:
        return jsonify({'status': 'fail'})

@app.route('/edit_products/<product_id>', methods=['GET'])
def edit_products(product_id):

    product = Product.query.get(product_id)

    if product:
        # Generate barcode image
        if product.barcode:
            # 生成Code128格式的条形码
            barcode128 = Code128(product.barcode, writer=ImageWriter())
            # 将条形码转换为字节流
            buffer = BytesIO()
            barcode128.write(buffer, options={'scale': 0.1})
            barcode_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            barcode_img = ''

        return render_template('edit_products.html', product=product, barcode_img=barcode_img)

@app.route('/edit_product/<product_id>', methods=['GET'])
def edit_product(product_id):

    product = Product.query.get(product_id)

    if product:
        # Generate barcode image
        if product.barcode:
            # 生成Code128格式的条形码
            barcode128 = Code128(product.barcode, writer=ImageWriter())
            # 将条形码转换为字节流
            buffer = BytesIO()
            barcode128.write(buffer, options={'scale': 0.1})
            barcode_img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        else:
            barcode_img = ''

        return render_template('edit_one_item.html', product=product, barcode_img=barcode_img)

@app.route('/submit_edit', methods=['POST'])
def submit_edit():

    try:
        product_id = request.form['id']

        product = Product.query.get(product_id)

        # 2. 根据当前产品的名字获取同名产品id，存储在product_ids数组中
        product_name = product.name
        same_name_products = Product.query.filter_by(name=product_name, status=1).all()
        product_ids = [product.id for product in same_name_products]

        changed = False

        product_data = {}

        if request.form['name'] and request.form['name'] != product.name:
            if Product.query.filter_by(name=request.form['name'], status=1).first():
                print(Product.query.filter_by(name=request.form['name'], status=1).first())
                raise ValueError("same product name already existed")
            product_data['name'] = request.form['name']
            changed = True

        if request.form['category'] and request.form['category'] != product.category:
            product_data['category'] = request.form['category']
            changed = True

        if request.form['brand'] and request.form['brand'] != product.brand:
            product_data['brand'] = request.form['brand']
            changed = True

        if request.form['specification'] and request.form['specification'] != product.specification:
            product_data['specification'] = request.form['specification']
            changed = True

        if request.form['unit'] and request.form['unit'] != product.unit:
            product_data['unit'] = request.form['unit']
            changed = True

        if request.form['cost_price'] and float(request.form['cost_price']) != product.cost_price:
            product_data['cost_price'] = request.form['cost_price']
            changed = True

        if request.form['supplier'] and request.form['supplier'] != product.supplier:
            product_data['supplier'] = request.form['supplier']
            changed = True

        if request.form['list_price'] and float(request.form['list_price']) != product.list_price:
            product_data['list_price'] = request.form['list_price']
            changed = True

        if request.form['sales_price'] and float(request.form['sales_price']) != product.sales_price:
            product_data['sales_price'] = request.form['sales_price']
            changed = True

        if request.form['salesperson'] and request.form['salesperson'] != product.salesperson:
            product_data['salesperson'] = request.form['salesperson']
            changed = True

        if request.form['remark'] != product.remark:
            product_data['remark'] = request.form['remark']
            changed = True

        if request.form['attribute1'] != product.attribute1:
            product_data['attribute1'] = request.form['attribute1']
            changed = True

        if request.form['attribute2'] != product.attribute2:
            product_data['attribute2'] = request.form['attribute2']
            changed = True

        if request.form['attribute3'] != product.attribute3:
            product_data['attribute3'] = request.form['attribute3']
            changed = True

        if request.form['attribute4'] != product.attribute4:
            product_data['attribute4'] = request.form['attribute4']
            changed = True

        if request.form['attribute5'] != product.attribute5:
            product_data['attribute5'] = request.form['attribute5']
            changed = True

        if request.form['in_time']:
            #in_time为空
            if not product.in_time:
                product_data['in_time'] = dt.datetime.fromisoformat(request.form['in_time'])
                changed = True
            #in_time不等
            elif request.form['in_time'] != product.in_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product_data['in_time'] = dt.datetime.fromisoformat(request.form['in_time'])
                changed = True

        if request.form['out_time']:
            #为空
            if not product.out_time:
                product_data['out_time'] = dt.datetime.fromisoformat(request.form['out_time'])
                product_data['status'] = 2
                changed = True
            #不等
            elif request.form['out_time'] != product.out_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product_data['out_time'] = dt.datetime.fromisoformat(request.form['out_time'])
                product_data['status'] = 2
                changed = True

        if request.form['abandonment_time']:
            #为空
            if not product.abandonment_time:
                product_data['abandonment_time'] = dt.datetime.fromisoformat(request.form['abandonment_time'])
                product_data['status'] = 3
                changed = True
            #不等
            elif request.form['abandonment_time'] != product.abandonment_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product_data['abandonment_time'] = dt.datetime.fromisoformat(request.form['abandonment_time'])
                product_data['status'] = 3
                changed = True

        if changed:
            Product.query.filter(Product.id.in_(product_ids)).update(product_data)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Product added successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Nothing Changed'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/submit_edit_one_item', methods=['POST'])
def submit_edit_one_item():

    try:
        product_id = request.form['id']

        product = Product.query.get(product_id)

        changed = False

        if request.form['name'] and request.form['name'] != product.name:
            product.name = request.form['name']
            changed = True

        if request.form['category'] and request.form['category'] != product.category:
            product.category = request.form['category']
            changed = True

        if request.form['brand'] and request.form['brand'] != product.brand:
            product.brand = request.form['brand']
            changed = True

        if request.form['specification'] and request.form['specification'] != product.specification:
            product.specification = request.form['specification']
            changed = True

        if request.form['unit'] and request.form['unit'] != product.unit:
            product.unit = request.form['unit']
            changed = True

        if request.form['cost_price'] and float(request.form['cost_price']) != product.cost_price:
            product.cost_price = request.form['cost_price']
            changed = True

        if request.form['supplier'] and request.form['supplier'] != product.supplier:
            product.supplier = request.form['supplier']
            changed = True

        if request.form['list_price'] and float(request.form['list_price']) != product.list_price:
            product.list_price = request.form['list_price']
            changed = True

        if request.form['sales_price'] and float(request.form['sales_price']) != product.sales_price:
            product.sales_price = request.form['sales_price']
            changed = True

        if request.form['salesperson'] and request.form['salesperson'] != product.salesperson:
            product.salesperson = request.form['salesperson']
            changed = True

        if request.form['remark'] != product.remark:
            product.remark = request.form['remark']
            changed = True

        if request.form['attribute1'] != product.attribute1:
            product.attribute1 = request.form['attribute1']
            changed = True

        if request.form['attribute2'] != product.attribute2:
            product.attribute2 = request.form['attribute2']
            changed = True

        if request.form['attribute3'] != product.attribute3:
            product.attribute3 = request.form['attribute3']
            changed = True

        if request.form['attribute4'] != product.attribute4:
            product.attribute4 = request.form['attribute4']
            changed = True

        if request.form['attribute5'] != product.attribute5:
            product.attribute5 = request.form['attribute5']
            changed = True

        if request.form['in_time']:
            #in_time为空
            if not product.in_time:
                product.in_time = dt.datetime.fromisoformat(request.form['in_time'])
                changed = True
            #in_time不等
            elif request.form['in_time'] != product.in_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product.in_time = dt.datetime.fromisoformat(request.form['in_time'])
                changed = True

        if request.form['out_time']:
            #为空
            if not product.out_time:
                product.out_time = dt.datetime.fromisoformat(request.form['out_time'])
                product.status = 2
                changed = True
            #不等
            elif request.form['out_time'] != product.out_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product.out_time = dt.datetime.fromisoformat(request.form['out_time'])
                product.status = 2
                changed = True

        if request.form['abandonment_time']:
            #为空
            if not product.abandonment_time:
                product.abandonment_time = dt.datetime.fromisoformat(request.form['abandonment_time'])
                product.status = 3
                changed = True
            #不等
            elif request.form['abandonment_time'] != product.abandonment_time.strftime('%Y-%m-%dT%H:%M:%S'):
                product.abandonment_time = dt.datetime.fromisoformat(request.form['abandonment_time'])
                product.status = 3
                changed = True

        # if request.form['out_time'] and request.form['out_time'] != product.out_time.strftime('%Y-%m-%d %H:%M:%S'):
        #     if product.out_time == '':
        #         product.status = 2
        #     product.out_time = dt.datetime.fromisoformat(request.form['out_time'])
        #     changed = True
        #
        # if request.form['abandonment_time'] and request.form['abandonment_time'] != product.abandonment_time.strftime('%Y-%m-%d %H:%M:%S'):
        #     if product.abandonment_time == '':
        #         product.status = 3
        #     product.abandonment_time = dt.datetime.fromisoformat(request.form['abandonment_time'])
        #     changed = True

        if changed:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Product added successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Nothing Changed'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# 销售管理路由
@app.route('/sales')
def sales_list():
    return render_template('sales_list.html')

# 镜片视图路由
@app.route('/lens')
def lens_view():
    all_lens = Product.query.filter_by(category='Lens', status=1).all()

    lens_data  = {}
    for lens in all_lens:
        attribute1 = lens.attribute1
        attribute2 = lens.attribute2
        key = f'{attribute1},{attribute2}'
        lens_data [key] = lens_data .get(key, 0) + 1

    return render_template('lens_view.html', lens_data=lens_data)

# 新增镜片路由
@app.route('/lens/add')
def addlens_view():
    # 生成条形码
    barcode = Util.generate_barcode()

    return render_template('lens_add.html', barcode=barcode)


@app.route('/submit_lens', methods=['POST'])
def submit_lens():
    try:
        # 从表单中获取数据

        brand = request.form.get('brand')
        specification = request.form.get('specification')
        remark = request.form.get('remark')
        unit = request.form.get('unit')
        cost_price = request.form.get('cost_price')
        list_price = request.form.get('list_price')
        supplier = request.form.get('supplier')
        barcode = request.form.get('rawbarcode')
        barcode128 = str(Code128(request.form['rawbarcode']))
        #未在页面提供input
        attribute3 = request.form.get('attribute3', '')
        attribute4 = request.form.get('attribute4', '')
        attribute5 = request.form.get('attribute5', '')
        # 将JSON格式的表格数据转化为Python列表
        data = json.loads(request.form.get('data'))
        now = dt.datetime.now()

        # 循环插入数据
        for key, value in data.items():
            attribute1_value, attribute2_value = key.split(',')
            for i in range(value):
                # 插入数据到数据库
                name = brand+specification+"镜片,S:"+attribute1_value+";C:"+attribute2_value
                new_product = Product(name=name, category='Lens', attribute1=attribute1_value, attribute2=attribute2_value, brand=brand,
                                      specification=specification, supplier=supplier, list_price=list_price,
                                      cost_price=cost_price, remark=remark, unit=unit, barcode=barcode, status=1,
                                      attribute3=attribute3, attribute4=attribute4, attribute5=attribute5, in_time=now,
                                      salesperson='')
                db.session.add(new_product)
                db.session.commit()

        return jsonify({'success': True, 'message': 'Product added successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

