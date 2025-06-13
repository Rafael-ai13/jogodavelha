import cv2
import mediapipe as mp
import time
import servo_braco3d as mao  # controle da mão robótica

# Inicializações
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

ALTURA, LARGURA = 480, 640
CÉLULA = 100
OFFSET_X, OFFSET_Y = 100, 50
TEMPO_ENTRE_JOGADAS = 3.0

tabuleiro = [["" for _ in range(3)] for _ in range(3)]
jogador_simbolo = "X"
simbolo_ia = "O"
vez_do_jogador = True
ultima_jogada = 0
jogo_encerrado = False
score_jogador = 0
score_ia = 0
mensagem_fim = ""
confirmando = False
tempo_confirmacao = 0

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

def verificar_vitoria(tab, simb):
    for i in range(3):
        if all([tab[i][j] == simb for j in range(3)]) or all([tab[j][i] == simb for j in range(3)]):
            return True
    if tab[0][0] == tab[1][1] == tab[2][2] == simb or tab[0][2] == tab[1][1] == tab[2][0] == simb:
        return True
    return False

def jogo_empate(tab):
    return all(tab[i][j] != "" for i in range(3) for j in range(3))

def mostrar_infos(img):
    cv2.putText(img, f"Jogador (X - paz): {score_jogador}  IA (O): {score_ia}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

def movimento_ia(tab, simb_ia, simb_jog):
    def pontuacao(tab, prof):
        if verificar_vitoria(tab, simb_ia):
            return 10 - prof
        if verificar_vitoria(tab, simb_jog):
            return prof - 10
        return 0

    def minimax(tab, prof, maximizando):
        if verificar_vitoria(tab, simb_ia) or verificar_vitoria(tab, simb_jog) or jogo_empate(tab):
            return pontuacao(tab, prof), None
        melhor = -float('inf') if maximizando else float('inf')
        melhor_mov = None
        for i in range(3):
            for j in range(3):
                if tab[i][j] == "":
                    tab[i][j] = simb_ia if maximizando else simb_jog
                    val, _ = minimax(tab, prof+1, not maximizando)
                    tab[i][j] = ""
                    if maximizando and val > melhor:
                        melhor, melhor_mov = val, (i,j)
                    elif not maximizando and val < melhor:
                        melhor, melhor_mov = val, (i,j)
        return melhor, melhor_mov

    _, mov = minimax(tab, 0, True)
    if mov:
        tab[mov[0]][mov[1]] = simb_ia
        return mov
    return None

def gesto_vitoria():
    mao.abrir_fechar(9, 1)
    mao.abrir_fechar(8, 1)
    mao.abrir_fechar(7, 0)
    mao.abrir_fechar(6, 0)
    mao.abrir_fechar(10, 0)

def gesto_empate():
    mao.abrir_fechar(9, 1)
    mao.abrir_fechar(8, 1)
    mao.abrir_fechar(7, 1)
    mao.abrir_fechar(6, 1)
    mao.abrir_fechar(10, 1)

def gesto_derrota():
    mao.abrir_fechar(9, 0)
    mao.abrir_fechar(8, 0)
    mao.abrir_fechar(7, 0)
    mao.abrir_fechar(6, 0)
    mao.abrir_fechar(10, 0)

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
    mostrar_infos(img)

    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            dedo = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x_pixel = int(dedo.x * LARGURA)
            y_pixel = int(dedo.y * ALTURA)

            lin, col = posicao_para_celula(x_pixel, y_pixel)

            if vez_do_jogador and not jogo_encerrado:
                if lin is not None and tabuleiro[lin][col] == "":
                    if not confirmando:
                        confirmando = True
                        tempo_confirmacao = time.time()
                    else:
                        if time.time() - tempo_confirmacao > 1.0:  # 1 segundo para confirmar
                            tabuleiro[lin][col] = jogador_simbolo
                            vez_do_jogador = False
                            ultima_jogada = time.time()
                            confirmando = False
                            if verificar_vitoria(tabuleiro, jogador_simbolo):
                                mensagem_fim = "Voce venceu!"
                                score_jogador += 1
                                jogo_encerrado = True
                                gesto_vitoria()
                            elif jogo_empate(tabuleiro):
                                mensagem_fim = "Empate!"
                                jogo_encerrado = True
                                gesto_empate()
                else:
                    confirmando = False

    if not vez_do_jogador and not jogo_encerrado and time.time() - ultima_jogada > TEMPO_ENTRE_JOGADAS:
        movimento_ia(tabuleiro, simbolo_ia, jogador_simbolo)
        vez_do_jogador = True
        if verificar_vitoria(tabuleiro, simbolo_ia):
            mensagem_fim = "IA venceu!"
            score_ia += 1
            jogo_encerrado = True
            gesto_derrota()
        elif jogo_empate(tabuleiro):
            mensagem_fim = "Empate!"
            jogo_encerrado = True
            gesto_empate()

    if jogo_encerrado:
        cv2.putText(img, mensagem_fim, (150, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.putText(img, "R = nova rodada | Q = novo jogo | X = sair", (50, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

    cv2.imshow("Jogo da Velha com Braco Robotico", img)
    tecla = cv2.waitKey(10) & 0xFF
    if tecla == 27 or tecla == ord('x'):
        break
    if jogo_encerrado:
        if tecla == ord('r'):
            tabuleiro = [["" for _ in range(3)] for _ in range(3)]
            jogo_encerrado = False
            vez_do_jogador = True
        elif tecla == ord('q'):
            tabuleiro = [["" for _ in range(3)] for _ in range(3)]
            score_jogador = 0
            score_ia = 0
            jogo_encerrado = False
            vez_do_jogador = True

cap.release()
cv2.destroyAllWindows()

