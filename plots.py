# plots.py
from math import factorial
import matplotlib.pyplot as plt
import os
from scipy.integrate import odeint
import numpy as np
from cfg import APPARATUS

def ensure_directories():
    """Создание директорий для временных файлов, если их нет."""
    os.makedirs('temp/images', exist_ok=True)

def plot_time_distribution(data):
    """Построение графика функции времени пребывания."""
    ensure_directories()
    output_file = "temp/images/time_distribution.png"

    plt.figure(figsize=(10, 6))
    t = data['t']
    Cind = data['Cind']

    plt.plot(t, Cind, 'b-', label="C(t)", marker="o", markersize=5)
    plt.title("Функция времени пребывания")
    plt.xlabel("Время t, с")
    plt.ylabel("Концентрация C, моль/л")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    return output_file

def plot_probability_distribution(data):
    """Построение графика распределения распределения пребывания."""
    ensure_directories()
    output_file = "temp/images/probability_distribution_plot.png"

    plt.figure(figsize=(10, 6))

    theta = data['t'] / APPARATUS['tau']
    psi = data['Cind'] * APPARATUS['V'] / APPARATUS['Q']

    plt.plot(theta, psi, 'r-', label="P(t)", marker="o", markersize=5)
    plt.title("Распределение времени пребывания")
    plt.xlabel("Θ")
    plt.ylabel("Ψ")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    return output_file


def plot_model1(data, cd):
    """Построение графиков для ячеечной модели импульсного возмущения."""
    def D(с, t):
        dc = np.zeros(10)
        dc[0] = (-1 / tau1) * с[0]
        for i in range(1, 10):
            dc[i] = (1 / tau1) * (с[i - 1] - с[i])
        return dc

    ensure_directories()
    output_file = "temp/images/impulse_model_plot.png"

    t = np.array(data['t'])
    n = 10
    C0 = [cd['Входная концентрация'] if i == 0 else 0 for i in range(n)]

    tau1 = APPARATUS['tau'] / n

    t_span = np.linspace(0, max(t), len(t))
    y = odeint(D, C0, t_span)


    plt.figure(figsize=(10, 6))
    plt.plot(t_span, y[:, 0], 'g', label="C1")
    plt.plot(t_span, y[:, 4], 'r', label="C5")
    plt.plot(t_span, y[:, 9], 'b', label="C10")
    plt.title("Результаты моделирования по уравнениям математического описания ячеечной модели", fontsize=14)
    plt.xlabel("Время")
    plt.ylabel("Концентрация")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    return output_file

def plot_model2(ccac):
    """Построение графиков на основе данных из литературы."""
    ensure_directories()
    output_file = "temp/images/literature_solution_plot.png"

    def Cf(t, n):
        c = np.zeros((len(tl), n))  # Создание массива с n столбцами
        for i in range(len(tl)):  # Для каждого значения времени
            for j in range(1, n + 1):  # Для каждого n от 1 до n (включительно)
                c[i, j - 1] = ccac['Входная концентрация'] * (1 / factorial(j - 1)) * ((tl[i] / tau1) ** (j - 1)) * np.exp(
                    -tl[i] / tau1)
        return c
    n = 10
    # Временная сетка
    tl = np.linspace(0, 8, 100)
    tau1 = APPARATUS['tau'] / n

    # Расчёт c
    c = Cf(tl, n)

    plt.figure(figsize=(10, 6))
    plt.plot(tl, c[:, 0], 'g', label="C1")
    plt.plot(tl, c[:, 4], 'r', label="C5")
    plt.plot(tl, c[:, 9], 'b', label="C10")
    plt.title("Результаты моделирования по известному из литературы решению", fontsize=14)
    plt.xlabel("t, min")
    plt.ylabel("C, -")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    return output_file


def plot_comparison(data, ccac):
    """Сравнение расчетных и экспериментальных данных."""

    def Cf(t, n):
        c = np.zeros(len(t))  # Создание массива с n элементов
        for i in range(len(t)):  # Для каждого значения времени
            c[i] = ccac['Входная концентрация'] * (1 / factorial(n - 1)) * ((t[i] / tau1) ** (n - 1)) * np.exp(
                -t[i] / tau1)
        return c

    def D(c, t):
        dc = np.zeros(10)
        dc[0] = (-1 / tau1) * c[0]
        for i in range(1, 10):
            dc[i] = (1 / tau1) * (c[i - 1] - c[i])
        return dc

    ensure_directories()
    output_file = "temp/images/comparison_plot.png"

    tl = np.linspace(0, 8, 100)
    C0 = [ccac['Входная концентрация'] if i == 0 else 0 for i in range(10)]

    t = np.array(data['t'])

    tau1 = APPARATUS['tau'] / 10
    Cind = np.array(data['Cind'])

    # Решение дифференциального уравнения
    y = odeint(D, C0, t)

    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(t, y[:, -1], 'g', label="C10")  # Используем последний столбец y для C10
    plt.plot(tl, Cf(tl, 10), '--b', label="C(t, 10)")  # Cf(t, 10)
    plt.plot(t, Cind, 'ro', label="Cind")  # Экспериментальные данные

    plt.title("Сравнение результатов моделирования")
    plt.xlabel("t, min")
    plt.ylabel("C, -")
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file)
    plt.close()

    return output_file

def cleanup_files(*files):
    """Удаление временных файлов."""
    for file in files:
        if os.path.exists(file):
            os.remove(file)
