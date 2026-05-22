from player import PLAYER_RADIUS

BULLET_RADIUS = 5
ENEMY_DAMAGE = 10


def check_bullet_enemy_collisions(bullets, enemies):
    """Bullet hits enemies; bullet is removed on hit."""
    for bullet in bullets:
        if not bullet.alive:
            continue
        for enemy in enemies:
            if not enemy.is_alive:
                continue
            if enemy.hits_circle(bullet.x, bullet.y, BULLET_RADIUS):
                enemy.take_damage(1)
                bullet.alive = False
                break


def check_enemy_player_collisions(enemies, player):
    """Enemies damage the player on contact."""
    if not player.alive:
        return
    for enemy in enemies:
        if not enemy.is_alive:
            continue
        if enemy.hits_circle(player.x, player.y, PLAYER_RADIUS):
            player.take_damage(ENEMY_DAMAGE)


def cleanup_bullets(bullets):
    """Remove bullets marked as not alive."""
    bullets[:] = [b for b in bullets if b.alive]
