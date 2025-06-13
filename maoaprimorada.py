import cv2
import mediapipe as mp
import time

# Inicializações
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

ALTURA, LARGURA = 480, 640
CÉLULA = 100
OFFSET_X, OFFSET_Y = 100, 50

# Estado
tabuleiro = [["" for _ in range(3)] for _ in range(3)]
jogador_simbolo = "X"
simbolo_ia = "O"
vez_do_jogador = True
jogo_encerrado = False
score_jogador = 0
score_ia = 0
ultima_jogada = 0
confirmando = False
tempo_confirmacao = 0
celula_confirmada = (None, None)

# Funções
def desenhar_grade(img):
    for i in range(1, 3):
        cv2.line(img, (OFFSET_X + i * CÉLULA, OFFSET_Y), (OFFSET_X + i * CÉLULA, OFFSET_Y + 3 * CÉLULA), (255, 255, 255), 2)
        cv2.line(img, (OFFSET_X, OFFSET_Y + i * CÉLULA), (OFFSET_X + 3 * CÉLULA, OFFSET_Y + i * CÉLULA), (255, 255, 255), 2)

def desenhar_pecas(img):
    for i in range(3):
        for j in range(3):
            cx = OFFSET_X + j * CÉLULA + CÉLULA // 2
            cy = OFFSET_Y + i * CÉLULA + CÉLULA // 2
            if tabuleiro[i][j] == "X":
                cv2.line(img, (cx - 25, cy - 25), (cx + 25, cy + 25), (255, 0, 0), 3)
                cv2.line(img, (cx - 25, cy + 25), (cx + 25, cy - 25), (255, 0, 0), 3)
            elif tabuleiro[i][j] == "O":
                cv2.circle(img, (cx, cy), 30, (0, 255, 0), 3)

def posicao_para_celula(x, y):
    col = (x - OFFSET_X) // CÉLULA
    lin = (y - OFFSET_Y) // CÉLULA
    if 0 <= col < 3 and 0 <= lin < 3:
        return int(lin), int(col)
    return None, None

def verificar_vitoria(simbolo):
    for i in range(3):
        if all(tabuleiro[i][j] == simbolo for j in range(3)) or all(tabuleiro[j][i] == simbolo for j in range(3)):
            return True
    if (tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] == simbolo) or \
       (tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] == simbolo):
        return True
    return False

def jogo_empate():
    return all(tabuleiro[i][j] != "" for i in range(3) for j in range(3))

def movimento_ia():
    # IA simples: primeiro vazio
    for i in range(3):
        for j in range(3):
            if tabuleiro[i][j] == "":
                tabuleiro[i][j] = simbolo_ia
                return i, j

def mostrar_info(img):
    cv2.putText(img, "Jogador (X - gesto paz)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, "IA (O)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(img, f"Placar: Voce {score_jogador} - IA {score_ia}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def contar_dedos(hand_landmarks):
    dedos_levantados = 0
    # Verifica indicador e médio
    if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y:
        dedos_levantados += 1
    if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y:
        dedos_levantados += 1
    return dedos_levantados

def reset_jogo(zera_placar=False):
    global tabuleiro, vez_do_jogador, jogo_encerrado, ultima_jogada, confirmando, tempo_confirmacao, celula_confirmada, score_jogador, score_ia
    tabuleiro = [["" for _ in range(3)] for _ in range(3)]
    vez_do_jogador = True
    jogo_encerrado = False
    ultima_jogada = 0
    confirmando = False
    tempo_confirmacao = 0
    celula_confirmada = (None, None)
    if zera_placar:
        score_jogador = 0
        score_ia = 0

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
    desenhar_pecas(img)
    mostrar_info(img)

    if not jogo_encerrado:
        if vez_do_jogador and resultado.multi_hand_landmarks:
            for hand_landmarks in resultado.multi_hand_landmarks:
                dedos = contar_dedos(hand_landmarks)
                x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * LARGURA)
                y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * ALTURA)
                lin, col = posicao_para_celula(x, y)
                if lin is not None:
                    if not confirmando:
                        if dedos == 2 and tabuleiro[lin][col] == "":
                            celula_confirmada = (lin, col)
                            confirmando = True
                            tempo_confirmacao = time.time()
                    else:
                        cv2.putText(img, "Confirmando...", (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        if time.time() - tempo_confirmacao > 1.5:
                            lin_c, col_c = celula_confirmada
                            tabuleiro[lin_c][col_c] = jogador_simbolo
                            if verificar_vitoria(jogador_simbolo):
                                jogo_encerrado = True
                                score_jogador += 1
                            elif jogo_empate():
                                jogo_encerrado = True
                            else:
                                vez_do_jogador = False
                                ultima_jogada = time.time()
                            confirmando = False
                break

        elif not vez_do_jogador and time.time() - ultima_jogada > 1.0:
            lin, col = movimento_ia()
            if verificar_vitoria(simbolo_ia):
                jogo_encerrado = True
                score_ia += 1
            elif jogo_empate():
                jogo_encerrado = True
            else:
                vez_do_jogador = True

    if jogo_encerrado:
        if verificar_vitoria(jogador_simbolo):
            msg = "Voce venceu!"
        elif verificar_vitoria(simbolo_ia):
            msg = "IA venceu!"
        else:
            msg = "Empate!"
        cv2.putText(img, msg, (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        cv2.putText(img, "R = nova rodada, Q = novo jogo, X = sair", (50, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow("Jogo da Velha - Visao Computacional", img)
    tecla = cv2.waitKey(10) & 0xFF
    if tecla == ord('x'):
        break
    if tecla == ord('r') and jogo_encerrado:
        reset_jogo()
    if tecla == ord('q') and jogo_encerrado:
        reset_jogo(zera_placar=True)

cap.release()
cv2.destroyAllWindows()
