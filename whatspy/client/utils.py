

def generate_qr(text):
    import qrcode

    qr = qrcode.make(text)
    qr.save('whatsapp-qr.png', 'PNG')

