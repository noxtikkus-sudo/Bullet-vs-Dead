from player import PLAYER_RADIUS
from settings import ENEMY_DAMAGE


def check_enemy_player_collisions(enemies, player):
    if not player.alive:
        return
    for enemy in enemies:
        if not enemy.is_alive:
            continue
        if enemy.hits_circle(player.x, player.y, PLAYER_RADIUS):
            player.take_damage(ENEMY_DAMAGE)


def cleanup_bullets(bullets):
    bullets[:] = [b for b in bullets if b.alive]
