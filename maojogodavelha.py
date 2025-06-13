import cv2
import mediapipe as mp
import time
import random

# Inicializações
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Parâmetros
ALTURA, LARGURA = 480, 640
CÉLULA = 100
OFFSET_X, OFFSET_Y = 100, 50
TEMPO_ENTRE_JOGADAS = 1.0  # segundos

# Estado do jogo
tabuleiro = [["" for _ in range(3)] for _ in range(3)]
jogador_simbolo = "X"
simbolo_ia = "O"
vez_do_jogador = True
ultima_jogada = 0
jogo_encerrado = False

# Funções auxiliares
def desenhar_grade(img):
    for i in range(1, 3):
        cv2.line(img, (OFFSET_X + i * CÉLULA, OFFSET_Y), (OFFSET_X + i * CÉLULA, OFFSET_Y + 3 * CÉLULA), (255, 255, 255), 2)
        cv2.line(img, (OFFSET_X, OFFSET_Y + i * CÉLULA), (OFFSET_X + 3 * CÉLULA, OFFSET_Y + i * CÉLULA), (255, 255, 255), 2)

def desenhar_pecas(img, tab):
    for i in range(3):
        for j in range(3):
            x = OFFSET_X + j * CÉLULA + CÉLULA // 2
            y = OFFSET_Y + i * CÉLULA + CÉLULA // 2
            if tab[i][j] == "X":
                cv2.line(img, (x - 25, y - 25), (x + 25, y + 25), (255, 0, 0), 3)
                cv2.line(img, (x - 25, y + 25), (x + 25, y - 25), (255, 0, 0), 3)
            elif tab[i][j] == "O":
                cv2.circle(img, (x, y), 30, (0, 255, 0), 3)

def posicao_para_celula(x, y):
    col = (x - OFFSET_X) // CÉLULA
    lin = (y - OFFSET_Y) // CÉLULA
    if 0 <= col < 3 and 0 <= lin < 3:
        return int(lin), int(col)
    return None, None

def verificar_vitoria(tab, simbolo):
    for i in range(3):
        if all([tab[i][j] == simbolo for j in range(3)]) or all([tab[j][i] == simbolo for j in range(3)]):
            return True
    if tab[0][0] == tab[1][1] == tab[2][2] == simbolo or tab[0][2] == tab[1][1] == tab[2][0] == simbolo:
        return True
    return False

def jogo_empate(tab):
    return all(tab[i][j] != "" for i in range(3) for j in range(3))

def mostrar_turno(img, turno_jogador):
    texto = "Sua vez" if turno_jogador else "Vez da IA"
    cor = (0, 255, 255) if turno_jogador else (0, 100, 255)
    cv2.putText(img, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

def movimento_ia_inteligente(tabuleiro, simbolo_ia, simbolo_jogador):
    def pontuacao(tab, profundidade):
        if verificar_vitoria(tab, simbolo_ia):
            return 10 - profundidade
        elif verificar_vitoria(tab, simbolo_jogador):
            return profundidade - 10
        return 0

    def minimax(tab, profundidade, maximizando):
        if verificar_vitoria(tab, simbolo_ia) or verificar_vitoria(tab, simbolo_jogador) or jogo_empate(tab):
            return pontuacao(tab, profundidade), None

        melhor_valor = -float('inf') if maximizando else float('inf')
        melhor_movimento = None

        for i in range(3):
            for j in range(3):
                if tab[i][j] == "":
                    tab[i][j] = simbolo_ia if maximizando else simbolo_jogador
                    valor, _ = minimax(tab, profundidade + 1, not maximizando)
                    tab[i][j] = ""
                    if maximizando and valor > melhor_valor:
                        melhor_valor, melhor_movimento = valor, (i, j)
                    elif not maximizando and valor < melhor_valor:
                        melhor_valor, melhor_movimento = valor, (i, j)

        return melhor_valor, melhor_movimento

    _, movimento = minimax(tabuleiro, 0, True)
    if movimento:
        i, j = movimento
        tabuleiro[i][j] = simbolo_ia
        return i, j
    return None

# 💡 Mão robótica — simulação visual
def animar_mao_jogador(img, lin, col):
    x = OFFSET_X + col * CÉLULA + CÉLULA // 2
    y = OFFSET_Y + lin * CÉLULA + CÉLULA // 2
    cv2.circle(img, (x, y), 40, (0, 150, 255), 4)
    cv2.putText(img, "👆", (x - 20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 150, 255), 2)

def animar_mao_ia(img, lin, col):
    x = OFFSET_X + col * CÉLULA + CÉLULA // 2
    y = OFFSET_Y + lin * CÉLULA + CÉLULA // 2
    cv2.rectangle(img, (x - 30, y - 30), (x + 30, y + 30), (0, 255, 150), 3)
    cv2.putText(img, "🤖", (x - 20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 150), 2)

# Loop principal
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    img = cv2.resize(frame, (LARGURA, ALTURA))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultado = hands.process(img_rgb)

    desenhar_grade(img)
    desenhar_pecas(img, tabuleiro)
    mostrar_turno(img, vez_do_jogador)

    if jogo_encerrado:
        cv2.putText(img, "Pressione R para reiniciar", (150, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    elif resultado.multi_hand_landmarks and vez_do_jogador:
        for hand_landmarks in resultado.multi_hand_landmarks:
            dedo = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x_pixel = int(dedo.x * LARGURA)
            y_pixel = int(dedo.y * ALTURA)
            lin, col = posicao_para_celula(x_pixel, y_pixel)

            if lin is not None and tabuleiro[lin][col] == "":
                tabuleiro[lin][col] = jogador_simbolo
                vez_do_jogador = False
                ultima_jogada = time.time()
                animar_mao_jogador(img, lin, col)
                if verificar_vitoria(tabuleiro, jogador_simbolo) or jogo_empate(tabuleiro):
                    jogo_encerrado = True
                break

    elif not vez_do_jogador and time.time() - ultima_jogada > TEMPO_ENTRE_JOGADAS and not jogo_encerrado:
        lin, col = movimento_ia_inteligente(tabuleiro, simbolo_ia, jogador_simbolo)
        vez_do_jogador = True
        ultima_jogada = time.time()
        animar_mao_ia(img, lin, col)
        if verificar_vitoria(tabuleiro, simbolo_ia) or jogo_empate(tabuleiro):
            jogo_encerrado = True

    if jogo_encerrado:
        if verificar_vitoria(tabuleiro, jogador_simbolo):
            texto = "Voce venceu!"
        elif verificar_vitoria(tabuleiro, simbolo_ia):
            texto = "IA venceu!"
        else:
            texto = "Empate!"
        cv2.putText(img, texto, (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)

    cv2.imshow("Jogo da Velha com Mao Robotica", img)
    tecla = cv2.waitKey(10) & 0xFF
    if tecla == 27:
        break
    if tecla == ord('r') and jogo_encerrado:
        tabuleiro = [["" for _ in range(3)] for _ in range(3)]
        jogo_encerrado = False
        vez_do_jogador = True

cap.release()
cv2.destroyAllWindows()
