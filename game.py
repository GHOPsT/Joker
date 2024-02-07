import pygame
import threading

# Inicialización de Pygame
pygame.init()

# Definición de constantes
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BALL_SIZE = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
FPS = 60

# Definición de variables globales
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_dx, ball_dy = 5, 5
paddle1_y, paddle2_y = HEIGHT // 2, HEIGHT // 2

# Función para mover la bola
def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, paddle1_y, paddle2_y

    while True:
        # Actualizar posición de la bola
        ball_x += ball_dx
        ball_y += ball_dy

        # Rebotar en la parte superior e inferior de la pantalla
        if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
            ball_dy *= -1

        # Rebotar en las paletas de los jugadores
        if (0 < ball_x < PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT) or \
           (WIDTH - PADDLE_WIDTH < ball_x < WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT):
            ball_dx *= -1

        # Dormir para mantener la velocidad constante
        pygame.time.wait(1000 // FPS)

# Función principal del juego
def main():
    global paddle1_y, paddle2_y

    # Configuración de la pantalla
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")

    # Crear un hilo para mover la bola
    ball_thread = threading.Thread(target=move_ball)
    ball_thread.start()

    # Bucle principal del juego
    clock = pygame.time.Clock()
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    paddle1_y -= 10
                elif event.key == pygame.K_s:
                    paddle1_y += 10
                elif event.key == pygame.K_UP:
                    paddle2_y -= 10
                elif event.key == pygame.K_DOWN:
                    paddle2_y += 10

        # Actualizar pantalla
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, (0, paddle1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, paddle2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_SIZE // 2)
        pygame.display.flip()

        # Controlar la velocidad de fotogramas
        clock.tick(FPS)

    # Esperar a que termine el hilo de la bola
    ball_thread.join()

# Ejecutar el juego
if __name__ == "_main_":
    main()