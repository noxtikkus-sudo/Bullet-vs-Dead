from settings import ENEMY_DAMAGE, PLAYER_RADIUS


def check_enemy_player_collisions(enemies, player):
    if not player.alive:
        return
    for enemy in enemies:
        if enemy.is_alive and enemy.hits_circle(player.x, player.y, PLAYER_RADIUS):
            player.take_damage(ENEMY_DAMAGE)


def cleanup_alive(items):
    items[:] = [item for item in items if item.alive]
