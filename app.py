import base64
import datetime as dt

from barcode import Code128
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
        name = request.form['name']
        category = request.form['category']
        brand = request.form['brand']
        # 商品状态码：1-新入库，2-销售出库，3-报废出库
        status = 1
        cost_price = request.form['cost_price']
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
        now = dt.datetime.now()
        for i in range(int(quantity)):
            new_product = Product(name=name, category=category, brand=brand, status=status, cost_price=cost_price,
                                  supplier=supplier, unit=unit, specification=specification,
                                  barcode=barcode128, remark=remark, attribute1=attribute1, attribute2=attribute2,
                                  attribute3=attribute3, attribute4=attribute4, attribute5=attribute5, in_time=now)
            new_product.save_to_db()

        # 保存之前填写的信息
        session['name'] = name
        session['category'] = category
        session['brand'] = brand
        session['cost_price'] = cost_price
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

@app.route('/barcode/<barcode>', methods=['GET'])
def barcode_image(barcode):
    # 生成Code128格式的条形码
    barcode128 = Code128(barcode, writer=ImageWriter())
    # 将条形码转换为字节流
    buffer = BytesIO()
    barcode128.write(buffer, options={'scale': 0.1})
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
        salesPerson = request.form.get('salesPerson','')
        sales_price = request.form.get('sell_price','')
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
        out_time = request.form.get('out_time')
        if not out_time:
            out_time = dt.datetime.now()
        else:
            out_time = dt.datetime.fromisoformat(out_time)
        remark = request.form.get('remark','')
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        if product:
            product.update(status=3, out_time=out_time, remark=remark)
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

        return render_template('edit_product.html', product=product, barcode_img=barcode_img)

@app.route('/submit_edit', methods=['POST'])
def submit_edit():
    try:
        quantity = request.form['quantity']
        name = request.form['name']
        category = request.form['category']
        brand = request.form['brand']
        # 商品状态码：1-新入库，2-销售出库，3-报废出库
        status = 1
        cost_price = request.form['cost_price']
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
        now = dt.datetime.now()
        for i in range(int(quantity)):
            new_product = Product(name=name, category=category, brand=brand, status=status, cost_price=cost_price,
                                  supplier=supplier, unit=unit, specification=specification,
                                  barcode=barcode128, remark=remark, attribute1=attribute1, attribute2=attribute2,
                                  attribute3=attribute3, attribute4=attribute4, attribute5=attribute5, in_time=now)
            new_product.save_to_db()

        # 保存之前填写的信息
        session['name'] = name
        session['category'] = category
        session['brand'] = brand
        session['cost_price'] = cost_price
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


# 销售列表路由
@app.route('/sales')
def sales_list():
    return render_template('sales_list.html')

# 员工列表路由
@app.route('/employee')
def employee_list():
    return render_template('employee_list.html')

if __name__ == '__main__':
    app.run(debug=True)

