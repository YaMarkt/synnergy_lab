import gspread
import os
import time


#что то типо моей библиотеки для быстрого доступа к частым функциям

def set_pale_red_background(sheet, row_number, array, max_len): #в этом проекте не используется
    """
    Устанавливает бледно-красный фон для ячеек в строке
    
    Параметры:
    sheet - объект листа gspread
    row_number - номер строки (начиная с 1)
    """
    # Определяем диапазон ячеек
    range_str = f"A{row_number}:{array[len(max_len)-1]}{row_number}"
    
    # Создаем форматирование
    pale_red = {
        'backgroundColor': {
            'red': 245/255,
            'green': 200/255,
            'blue': 200/255
        }
    }
    sheet.format(range_str, pale_red)

def color_cell(sheet, row_number, col_letter, color): #в этом проекте не используется
    """
    Красит одну ячейку в указанный цвет.

    sheet - объект листа
    row_number - номер строки
    col_letter - буква столбца (например 'A')
    color - словарь с цветом {'red': ..., 'green': ..., 'blue': ...}
    """
    range_str = f"{col_letter}{row_number}"
    sheet.format(range_str, {
        'backgroundColor': color
    })


def safe_api_call(func, *args, **kwargs): #для того чтобы не улетало в ошибку гугл доков(лимит и т.д)
    while True:
        try:
            return func(*args, **kwargs)
        except gspread.exceptions.APIError as e:
            if "Quota exceeded" in str(e):
                print("Достигнут лимит запросов. Ожидание...")
                time.sleep(10)  # Увеличьте паузу, если ошибка повторяется
            else:
                raise

def list_files(directory): #в этом проекте не используется
    files_xlsx = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            files_xlsx.append(file_path)
    return files_xlsx  

def find_longest_array(array_of_arrays): #в этом проекте не используется
    longest_array = max(array_of_arrays, key=len)
    return longest_array


def count_repeated_elements(array):
    element_count = {}
    for element in array: #пока в array есть "element" цикл не кончится
        if element in element_count:
            element_count[element] += 1
        else:
            element_count[element] = 1
    return element_count


