from balltic import Gunpowder

my_cannon = {
    'nodes': 100,
    'boostp': 30 * 1e6,
    'press_vsp': 5 * 1e6,
    'denload': 775,
    'K': 1.03,
    'caliber': 0.057,
    'shell': 3.75,
    'kurant': 0.4,
    'barrel': 3.861,
    'omega_q': 0.257
}

# Получить решение для условий и характеристик, приведенных в `cannon`
solution = Gunpowder(cannon=my_cannon, powder='16\\1 тр')

# Скорость снаряда в момент вылета из канала ствола
solution.shell_velocity[-1]

# Сохранить решение
solution.save()

# Загрузить ранее полученное решение
solution.load()
