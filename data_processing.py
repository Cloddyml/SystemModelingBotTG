# data_processing.py
from math import factorial
import numpy as np
import pandas as pd
from scipy.optimize import minimize, fsolve
from scipy.special import erfc
from cfg import APPARATUS


def calculate_moments(data):
    """Расчет первых четырех моментов распределения времени пребывания."""
    theta = data['t'] / APPARATUS['tau']
    psi = data['Cind'] * APPARATUS['V'] / APPARATUS['Q']

    SumPsi = np.sum(np.array(psi))
    SumThetaPsi1 = np.sum(np.array(theta) * np.array(psi))
    SumThetaPsi2 = np.sum(np.array(theta) ** 2 * np.array(psi))
    SumThetaPsi3 = np.sum(np.array(theta) ** 3 * np.array(psi))
    SumThetaPsi4 = np.sum(np.array(theta) ** 4 * np.array(psi))

    alpha1 = SumThetaPsi1 / SumPsi  # Первый момент
    alpha2 =  SumThetaPsi2 / SumPsi # Второй момент
    alpha3 =  SumThetaPsi3 / SumPsi # Третий момент
    alpha4 =  SumThetaPsi4 / SumPsi # Четвертый момент

    moments = {
        'alpha1': round(alpha1, 3),
        'alpha2': round(alpha2, 3),
        'alpha3': round(alpha3, 3),
        'alpha4': round(alpha4, 3)
    }

    return moments


def calculate_statistics(data, moments):
    """Расчет дополнительных статистических параметров."""
    theta = data['t'] / APPARATUS['tau']
    psi = data['Cind'] * APPARATUS['V'] / APPARATUS['Q']
    alpha1 = moments['alpha1']
    alpha2 = moments['alpha2']
    alpha3 = moments['alpha3']
    alpha4 = moments['alpha4']

    psiMax = np.max(psi)
    psiN = np.argmax(psi)
    m = theta[psiN] # Мода
    cm = psiMax  # Плотность вероятности в моде

    variance = alpha2 - alpha1 ** 2  # Дисперсия

    skewness = (alpha3 - 3 * alpha1 * alpha2 + 2 * alpha1 ** 3) / (variance ** 1.5)  # Асимметрия

    kurtosis = (alpha4 - 4 * alpha3 * alpha1 + 6 * alpha2 * alpha1 ** 2 - 3 * alpha1 ** 4) / (variance ** 2)  # Эксцесс

    statistics = {
        'Мода': round(m, 6),
        'Плотность моды': round(cm, 6),
        'Дисперсия': round(variance, 6),
        'Асимметрия': round(skewness, 6),
        'Эксцесс': round(kurtosis, 6)
    }

    return statistics

def calc_peclet_numbers(moments, stat):
    """Расчет чисел Пекле и дополнительных параметров."""
    alpha1 = moments['alpha1']
    alpha2 = moments['alpha2']
    alpha3 = moments['alpha3']
    alpha4 = moments['alpha4']
    m = stat['Мода']
    cm = stat['Плотность моды']
    sig = stat['Дисперсия']
    A = stat['Асимметрия']
    kurt = stat['Эксцесс']

    peclet_numbers = []

    def pecle1():
        if alpha1 > 1.001:
            Pe1 = 1 / (alpha1 - 1)
        else:
            Pe1 = 0
        return Pe1

    def pecle2(x):
        return alpha2 - 1 - (4 / x) - (4 / (x ** 2))

    def pecle3(x):
        return alpha3 - 1 - (9 / x) - (30 / (x ** 2)) - (30 / (x ** 3))

    def pecle4(x):
        return alpha4 - 1 - (16 / x) - (108 / (x ** 2)) - (336 / (x ** 3)) - (336 / (x ** 4))

    def f(x):
        a1 = erfc((1 + x) / ((2 + x) ** 0.5))
        a2 = ((2 + x) / np.pi) ** 0.5
        a3 = np.exp(-1 / (2 + x))
        a4 = (x / 2) * a1 * (1 + x + (x ** 2) / 2 + (x ** 3) / 6 + (x ** 4) / 24 + (x ** 5) / 120)
        return a2 * a3 * a4

    def pecle5():
        if m < 1:
            Pe5 = 2 * m / (1 - m)
        else:
            Pe5 = 0
        return Pe5

    def pecle6(x):
        return cm - f(x)

    def pecle7(x):
        return sig - 2 / x - 3 / (x ** 2)

    def pecle8(x):
        return A - (20 + 12 * x) / ((3 + 2 * x) ** 1.5)

    def pecle9(x):
        return kurt - (210 + 120 * x) / ((3 + 2 * x) ** 2)

    x0 = np.array([1.0])

    for func in [pecle1, pecle2, pecle3, pecle4, pecle5, pecle6, pecle7, pecle8, pecle9]:
        if func == pecle1:
            peclet_numbers.append(pecle1())
        elif func == pecle5:
            peclet_numbers.append(pecle5())
        else:
            try:
                Pe = fsolve(func, x0)
                peclet_numbers.append(abs(Pe[0]))
            except RuntimeError as e:
                peclet_numbers.append(0)  # В случае ошибки добавляем 0

    nAll = 9
    if peclet_numbers[0] == 0:
        nAll -= 1
    if peclet_numbers[4] == 0:
        nAll -= 1
    nAll = np.array(nAll)
    peclet_numbers = np.array(peclet_numbers)

    PesrAll = np.sum((1 / nAll) * peclet_numbers)

    DsrAll = APPARATUS['v'] * APPARATUS['L'] / PesrAll

    n1 = PesrAll / 2
    n4 = 4

    if peclet_numbers[0] == 0:
        n4 -= 1
    if peclet_numbers[4] == 0:
        n4 -= 1

    Pesr4 = (1 / n4) * (peclet_numbers[0] + peclet_numbers[1] + peclet_numbers[4] + peclet_numbers[6])
    Dsr4 = APPARATUS['v'] * APPARATUS['L'] / Pesr4

    n2 = Pesr4 / 2

    peclet_results = {
        'Числа Пекле': peclet_numbers,
        'Ср. знач. Пекле(9)': PesrAll,
        'Ср. знач. Пекле(4)': Pesr4,
        'Знач. коэф. продольного перемешивания (9)': DsrAll,
        'Знач. коэф. продольного перемешивания (4)': Dsr4,
        'n1': n1,
        'n2': n2
    }

    return peclet_results

def calc_cells_and_С(data):
    """Расчет числа ячеек и входной концентрации индикатора."""
    def ff(x):
        return np.sum(
            Cind - x[1] * (1 / (factorial(int(np.ceil(x[0]) - 1)))) * ((t / APPARATUS['tau']) ** (np.ceil(x[0] - 1))) * np.exp(-t / APPARATUS['tau'])) ** 2

    Cind = data['Cind']
    t = data['t']
    x0 = np.array([5.0, 10.0])

    res = minimize(ff, x0, method='Nelder-Mead', options={'disp': True, 'maxiter': 1000, 'maxfev': 3000})

    n = np.ceil(res.x[0])
    Cinput = res.x[1]

    results = {
        'n': n,
        'Входная концентрация': Cinput
    }

    return results

def calc_simple_method(data):
    """Упрощенное вычисление числа ячеек по вероятностным характеристикам."""
    theta = data['t'] / APPARATUS['tau']
    theta = np.array(theta)
    psi = data['Cind'] * APPARATUS['V'] / APPARATUS['Q']

    sumC = np.sum(data['Cind'])
    sumtC = np.sum(data['t'] + data['Cind'])

    tau1 = sumtC / sumC
    deltaT = 0.25
    deltaTheta = deltaT / tau1
    Csr = []
    for i in range(len(psi) - 1):
        Csr.append(((psi[i + 1] - psi[i]) / 2 + psi[i]))

    """ Вычисление нулевого момента """
    M0 = np.sum(deltaTheta * np.array(Csr))
    M1 = np.sum(deltaTheta * np.array(Csr) * theta[:-1])
    M2 = np.sum(deltaTheta * np.array(Csr) * (theta[:-1] ** 2))

    M1m = M1 / M0
    M2m = M2 / M0
    M2t = M2m / (M1m ** 2)

    Pe = 2 / (M2t - 1)
    n = 1 / (M2t - 1)

    results = {
        'τ': round(tau1, 6),
        'Delta θ': round(deltaT, 6),
        'Csr': [round(value, 6) for value in Csr],
        'M0': round(M0, 6),
        'M1': round(M1, 6),
        'M2': round(M2, 6),
        'Pe': round(Pe, 6),
        'n': round(n, 6)
    }

    return results

def read_csv_data(file_path):
    """Чтение данных из CSV-файла и возврат их в виде таблицы."""
    try:
        data = pd.read_csv(file_path, delimiter=';')
        return data
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла: {e}")
