import cv2 

camera = cv2.VideoCapture(0)

# Tamanho da captura da imagem
camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,640)
# Nome e tamanho da janela 
cv2.namedWindow('Captura', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Captura', 640, 480)
# foi deixado as duas dimensões da janela e da captura iguais
# retorno = 1 ele conseguiu ler a camera, é um boleano, se não conseguiu ler a camera o codigo não continua
while True:
    retorno, frame = camera.read()
    if not retorno:
        break

    cv2.imshow('Captura', frame )

    if cv2.waitKey(1) & 0xFF == 'q':
        break

camera.release()
cv2.destroyAllWindows()