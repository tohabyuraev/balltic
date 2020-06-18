from balltic import Pneumatic

cannon = {
    'nodes': 100,
    'press': 5e6,
    'ro': 141.471,
    'L0': 0.5,
    'd': 0.03,
    'L': 2,
    'shell_mass': 0.1,
    'k': 1.4,
    'Ku': 0.5,
    'R': 287
}

# Получить решение для условий и характеристик, приведенных в `cannon`
solution = Pneumatic(cannon)

# Скорость снаряда в момент вылета из канала ствола
solution.shell_velocity[-1]

# Сохранить решение
solution.save()

# Загрузить ранее полученное решение
solution.load()
