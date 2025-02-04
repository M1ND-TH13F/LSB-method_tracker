from PIL import Image
from glob import glob
import os


def sum_of_differences(lst):
    # Новый список для хранения модулей разности
    differences = []

    # Перебираем элементы списка по парам (i, i+1)
    for i in range(0, len(lst) - 1, 2):  # Шаг 2 для пары элементов
        diff = abs(lst[i] - lst[i + 1])  # Модуль разности
        differences.append(diff)

    # Возвращаем сумму элементов списка differences
    return sum(differences)


def lsb_hide_method(image, payload_data, image_number):

    image_dir = "../../Desktop/Проект_регион/empty_s"

    image_path = os.path.join(image_dir, image.split(os.sep)[-1])


    # Открываем изображение
    sempty = Image.open(image_path)
    sempty = sempty.convert('RGB')
    width_empty, height_empty = sempty.size
    pix_empty = sempty.load()  # Выгружаем значения пикселей

    # Читаем весь payload в список, убираем все символы новой строки
    with open(payload_data, 'r+') as payload:  # Теперь payload_data — это путь к файлу
        payload_data = payload.read().replace("\n", "")  # Все данные из файла без '\n'
    # Преобразуем весь payload в строку из двоичных представлений
    binary_payload = ''.join([bin(ord(symbol))[2:].zfill(8) for symbol in payload_data])

    c = 0  # Индекс для получения символа из binary_payload

    for y in range(width_empty):
        for x in range(height_empty):
            if c + 2 < len(binary_payload):  # Убедимся, что хватает бит на 1 пиксель
                r, g, b = pix_empty[y, x]

                # Преобразуем каждый цвет в двоичный вид, заполняем до 8 бит
                r_bin = bin(r)[2:].zfill(8)
                g_bin = bin(g)[2:].zfill(8)
                b_bin = bin(b)[2:].zfill(8)

                # Заменяем последние биты каждого компонента на биты из payload
                r_bin = r_bin[:-1] + binary_payload[c]
                c += 1
                g_bin = g_bin[:-1] + binary_payload[c]
                c += 1
                b_bin = b_bin[:-1] + binary_payload[c]
                c += 1

                # Преобразуем обратно в целые числа
                r = int(r_bin, 2)
                g = int(g_bin, 2)
                b = int(b_bin, 2)

                # Обновляем пиксель
                pix_empty[y, x] = (r, g, b)
            elif c + 1 > len(binary_payload):
                break

    # Сохраняем измененное изображение
    return sempty.save(f"full_s/stego_full{image_number}.png")





def lsb_method_reveal(image):
    s = Image.open(image)
    s = s.convert('RGB')
    width_s, height_s = s.size
    pix = s.load()  # Выгружаем значения пикселей

    a = 0
    neigh_list = []

    for y in range(width_s):
        for x in range(height_s):
            neigh_r = 0
            neigh_l = 0
            # Получаем компоненты R, G, B для текущего пикселя
            r = pix[y, x][0]
            g = pix[y, x][1]
            b = pix[y, x][2]

            # Перебираем все пиксели, кроме самого себя
            for i in range(width_s):
                for j in range(height_s):
                    if (i != y) or (j != x):  # Исключаем сам пиксель
                        r_neigh = pix[i, j][0]
                        g_neigh = pix[i, j][1]
                        b_neigh = pix[i, j][2]

                        # Проверяем, отличаются ли компоненты цвета на 1
                        if (abs(r - r_neigh) == 1) or (abs(g - g_neigh) == 1) or (abs(b - b_neigh) == 1):
                            # Считаем соседей, которые отличаются на 1
                            if (r == r_neigh + 1) or (g == g_neigh + 1) or (b == b_neigh + 1):
                                neigh_r += 1  # Увеличиваем для правых соседей
                            elif (r == r_neigh - 1) or (g == g_neigh - 1) or (b == b_neigh - 1):
                                neigh_l += 1  # Увеличиваем для левых соседей

            neigh_list.append(neigh_r)
            neigh_list.append(neigh_l)
            a += 1

            # Перемещаем проверку сюда, чтобы прервать выполнение кода после 100 итераций
            if a >= 100:
                break
        if a >= 100:  # Добавляем еще одну проверку, чтобы выйти из внешнего цикла
            break
    return sum_of_differences(neigh_list)



def create_container():
    payload = "stego_payload.txt"
    count = 0
    for filename in glob('empty_s/*.png'):
        lsb_hide_method(filename, payload, count)
        count += 1



empty_c = []
full_c = []
a = input(f"Создать стегоконтейнеры в папке full_s на основе изображений, лежащих в папке empty_s?[y/n]:")
if a == "y" or a == "Y":
    create_container()



print("Ждите, идёт подсчёт пикселей 'соседних' цветов в пустых и заполненных контейнерах")
for filename in glob('empty_s/*.png'):
    empty_c.append(lsb_method_reveal(filename))
for filename in glob('full_s/*.png'):
    full_c.append(lsb_method_reveal(filename))


print("Теперь вы можете видеть результаты анализа")
for i in range(len(empty_c)):
    if empty_c[i] < full_c[i]:
        print(f"stego_empty{i}.png - пустой контейнер")
    elif empty_c[i] > full_c[i]:
        print(f"stego_empty{i}.png - заполненный контейнер")
