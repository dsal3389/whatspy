import os


__all__ = ('generate_qr', 'remove_qr')


QR_PATH = 'whatsapp-qr.png'


def generate_qr(text):
    import qrcode

    qr = qrcode.make(text)
    qr.save(QR_PATH, 'PNG')

def remove_qr():
    path = os.path.abspath(QR_PATH)

    if os.path.exists(path):
        os.remove(path)
