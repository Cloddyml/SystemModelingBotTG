# cfg.py
from math import pi

TOKEN = "SOMETOKEN"
APPARATUS = {
    "L": 20,  # длина в метрах
    "d": 0.03,  # диаметр в метрах
    "w": 0.001,  # объемная скорость потока, м3/с
    "Q": 0.3, # в кг
    "gamma": 0.7, # насадочный коэффициент
    "V": pi * (0.03 / 2) ** 2 * 20 * (1 - 0.7),  # объем аппарата, м3
    "tau": (pi * (0.03 / 2) ** 2 * 20 * (1 - 0.7)) / 0.001,  # время пребывания в аппарате, с
    "v": 0.001 / (pi * (0.03 / 2) ** 2 * 20 * (1 - 0.7)) # линейная скорость потока, м/с
}