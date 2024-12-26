# bot.py
import telebot
import os
from plots import (plot_model1, plot_model2, plot_comparison,
                   plot_time_distribution, plot_probability_distribution)
from data_processing import (read_csv_data, calculate_moments,
                             calculate_statistics, calc_peclet_numbers,
                             calc_cells_and_С,
                             calc_simple_method)
from time import sleep
from cfg import APPARATUS,TOKEN

def send_photo(image, mes):
    with open(image, 'rb') as img:
        bot.send_photo(mes.chat.id, img)
    if os.path.exists(image):
        try:
            os.remove(image)
        except Exception as e:
            bot.reply_to(mes, f"Ошибка при удалении файла: {e}")

bot = telebot.TeleBot(TOKEN)

data_dir = "temp/csv"
os.makedirs(data_dir, exist_ok=True)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать! Пришлите CSV-файл с данными для анализа.")

@bot.message_handler(commands=['example'])
def send_example(message):
    """Отправка примера файла пользователю."""
    try:
        example_file_path = "example_files/input_example.csv"
        with open(example_file_path, 'rb') as example_file:
            bot.send_document(message.chat.id, example_file)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Файл примера не найден. Пожалуйста, проверьте путь.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = os.path.join(data_dir, message.document.file_name)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)

        data = read_csv_data(file_path)
        bot.send_message(message.chat.id, 'Параметры аппарата:\n\n' +
                         f"L={APPARATUS['L']} м (длина)\n" +
                         f"d={APPARATUS['d']} м (диаметр)\n" +
                         f"w={APPARATUS['w']} м3/с (объемная скорость потока)\n" +
                         f"Q={APPARATUS['Q']} кг\n" +
                         f"gamma={APPARATUS['gamma']} (осадочный коэффициент)\n" +
                         f"V={APPARATUS['V']} м3 (объем аппарата)\n" +
                         f"tau={APPARATUS['tau']} с (время пребывания аппарата)\n" +
                         f"v={APPARATUS['v']} м/с (линейная скорость потока)\n")
        sleep(1)

        bot.reply_to(message, "Файл успешно загружен и обработан.")
        os.remove(file_path) # Удаление файла
        bot.send_message(message.chat.id, 'Начинаю анализ...')
        bot.send_message(message.chat.id, f'Исходные данные:\n{data.to_string(index=False)}')
        sleep(0.5)

        p = plot_time_distribution(data)
        # Построение графика функции времени пребывания
        send_photo(p, message)
        sleep(0.5)

        p = plot_probability_distribution(data)
        # Построение функции распределения времени пребывания
        send_photo(p, message)
        sleep(0.5)

        moments = calculate_moments(data)
        statistics = calculate_statistics(data, moments)

        response = "Моменты распределения:\n" + "\n".join([f"{k}: {v}" for k, v in moments.items()])
        response += "\n\nСтатистические параметры:\n" + "\n".join([f"{k}: {v}" for k, v in statistics.items()])
        bot.send_message(message.chat.id, response)
        sleep(0.5)

        peclet_data = calc_peclet_numbers(moments, statistics)
        peclet_text = (
                f"Числа Пекле:\n" +
                "\n".join([f"Pe{i + 1}: {round(pe, 6)}" for i, pe in enumerate(peclet_data['Числа Пекле'])]) +
                f"\n\nСредние значения Пекле:\n"
                f"Pesr (9): {round(peclet_data['Ср. знач. Пекле(9)'], 6)}\n"
                f"Pesr (4): {round(peclet_data['Ср. знач. Пекле(4)'], 6)}\n\n"
                f"Коэффициенты продольного перемешивания:\n"
                f"Dsr (9): {round(peclet_data['Знач. коэф. продольного перемешивания (9)'], 6)}\n"
                f"Dsr (4): {round(peclet_data['Знач. коэф. продольного перемешивания (4)'], 6)}\n\n"
                f"Дополнительные параметры:\n"
                f"n1: {round(peclet_data['n1'], 6)}\n"
                f"n2: {round(peclet_data['n2'], 6)}"
        )
        bot.send_message(message.chat.id, f"Числа Пекле и операции с ними:\n{peclet_text}")
        sleep(0.5)

        cells_data = calc_cells_and_С(data)
        response = "Определение числа ячеек и входной концентрации:\n\n"
        response += "\n".join([f"{k}: {v}" for k, v in cells_data.items()])
        bot.send_message(message.chat.id, response)
        sleep(0.5)

        bot.send_message(message.chat.id, "Расчет числа ячеек упрощенным методом (по вероятностным характеристикам)...")

        simple_data = calc_simple_method(data)
        response = f"Результаты упрощенного вычисления:\n\n" + \
        f"Среднее время пребывания (τ): {simple_data['τ']}\n" + \
        f"Шаг по времени (Delta θ): {simple_data['Delta θ']}\n\n" + \
        f"Средние концентрации (Csr):\n" + \
        f"{', '.join(map(str, simple_data['Csr']))}\n\n" + \
        f"Моменты распределения:\n" + \
        f"M0: {simple_data['M0']}\n" + \
        f"M1: {simple_data['M1']}\n" + \
        f"M2: {simple_data['M2']}\n\n" + \
        f"Число Пекле (Pe): {simple_data['Pe']}\n" + \
        f"Число ячеек (n): {simple_data['n']}"
        bot.send_message(message.chat.id, response)
        sleep(0.5)

        p = plot_model1(data, cells_data)
        # Моделирование процесса по ячеечной модели при импульсном возмущении
        send_photo(p, message)
        sleep(0.5)

        p = plot_model2(cells_data)
        # Моделирование процесса по известному из литератур решению
        send_photo(p, message)
        sleep(0.5)

        p = plot_comparison(data, cells_data)
        # Сравнение
        send_photo(p, message)
        sleep(0.5)

        bot.send_message(message.chat.id, "Анализ завершен.")


    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
