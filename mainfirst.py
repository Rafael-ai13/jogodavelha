import cv2 
from cvzone.HandTrackingModule import HandDetector

camera = cv2.VideoCapture(0)
detector = HandDetector()

# Tamanho da captura da imagem
camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
# Nome e tamanho da janela 
cv2.namedWindow('Captura', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Captura', 640, 480)
# foi deixado as duas dimensões da janela e da captura iguais
# retorno = 1 ele conseguiu ler a camera, é um boleano, se não conseguiu ler a camera o codigo não continua

desenho = []

while True:
    retorno, frame = camera.read()
    if not retorno:
        break

    resultado = detector.findHands(frame, draw=True)
    mao = resultado[0]
    
    if mao:
        lm_list = mao[0]['lmList']
        dedos = detector.fingersUp(mao[0])
        dedos_levantados = dedos.count(1)
        print(dedos_levantados)

        if dedos_levantados ==1:
            x, y = lm_list[8][0], lm_list[8][1]
            cv2.circle(frame, (x, y), 15, (255,0,0),cv2.FILLED)
            desenho.append((x,y))
        elif dedos_levantados == 0:
            desenho.append((0, 0))
        elif dedos_levantados ==5:
            desenho = []

        for indice, coordenada in enumerate(desenho):
            x,y = coordenada[0],coordenada[1]
            cv2.circle(frame, (x,y), 10, (255,0,0),cv2.FILLED)
            if indice>=1:
                coordenada_anterior_x, coordenada_anterior_y = desenho[indice-1][0], desenho[indice-1][1]
                if coordenada_anterior_x!=0 and coordenada_anterior_y!=0:
                    cv2.line(frame, (x,y), (coordenada_anterior_x, coordenada_anterior_y), (255,0,0), 20)

    imagem_invertida = cv2.flip(frame,1)
    cv2.imshow('Captura', imagem_invertida)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()