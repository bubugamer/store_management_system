import time
import random

import qrcode
from barcode import EAN13
from barcode.writer import ImageWriter

class Util:
    @staticmethod
    def generate_barcode():
        random_number = random.randint(1, 1000000)
        timestamp = int(time.time() * 1000)
        barcode = str(random_number) + str(timestamp)
        return barcode

    @staticmethod
    def generate_qrcode(data):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        filename = f'qrcode_{data}.png'
        img.save(filename)
        return filename
