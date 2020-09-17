# Импортируем артиллерийское орудие (АО)
#   и определитель уровня давления
from balltic import PressureLevel
from balltic import ArtilleryGun

# Создаем экземпляр АО
my_big_gun = ArtilleryGun(
    K = 1.03,
    fi_1 = 1.03,
    shell = 3.75,
    barrel = 3.861,
    kurant = 0.4,
    boostp = 30 * 1e6,
    caliber = 0.057,
    denload = 775,
    omega_q = 0.257,
    press_vsp = 5 * 1e6,
)

# Получаем решение и сохраняем его в excel-файл
solution = PressureLevel(my_big_gun, 850).to_excel()
