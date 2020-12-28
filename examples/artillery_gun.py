from balltic import ArtilleryGrid, ArtilleryGun

my_big_gun = ArtilleryGun(
    K=1.03,
    shell=3.75,
    barrel=3.861,
    kurant=0.4,
    boostp=30 * 1e6,
    caliber=0.057,
    denload=775,
    omega_q=0.257,
    press_vsp=5 * 1e6,
)

# Получить решение для условий и характеристик,
#   приведенных в `my_big_gun`
solution = ArtilleryGrid(gun=my_big_gun, gunpowder='16\\1 тр')

# Скорость снаряда в момент вылета из канала ствола
solution.shell_velocity[-1]

# Сохранить решение
solution.save()

# Загрузить ранее полученное решение
solution.load()
