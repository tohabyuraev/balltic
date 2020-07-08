from balltic import Pneumatic, AirGun, Gas

my_big_gun = AirGun(
    shell = 0.1,
    kurant = 0.5,
    barrel = 2,
    chamber = 0.5,
    caliber = 0.03,
    initialp = 5 * 1e6,
)

boom_gas = Gas(
    k = 1.4,
    R = 287,
    ro = 141.471,
)

# Получить решение для условий и параметров,
#   приведенных в `my_big_gun` и `boom_gas`
solution = Pneumatic(gun=my_big_gun, gas=boom_gas)

# Скорость снаряда в момент вылета из канала ствола
solution.shell_velocity[-1]

# Сохранить решение
solution.save()

# Загрузить ранее полученное решение
solution.load()
