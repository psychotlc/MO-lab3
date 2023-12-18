
from simplex_table import *
import json


class Simplex:
    """
    Класс для решения задачи ЛП симплекс-методом.
    """

    def __init__(self, path_to_file):
        """
        Переопределённый метод __init__. Регистрирует входные данные из JSON-файла.
        Определяем условие задачи.
        :param path_to_file: путь до JSON-файла с входными данными.
        """

        # Парсим JSON-файл с входными данными
        with open(path_to_file, "r") as read_file:
            json_data = json.load(read_file)
            self.obj_func_coffs_ = np.array(json_data["obj_func_coffs"])  # вектор-строка с - коэффициенты ЦФ
            self.constraint_system_lhs_ = np.array(json_data["constraint_system_lhs"])  # матрица ограничений А
            self.constraint_system_rhs_ = np.array(json_data["constraint_system_rhs"])  # вектор-столбец ограничений b
            self.func_direction_ = json_data["func_direction"]  # направление задачи (min или max)

            if len(self.constraint_system_rhs_) != self.constraint_system_rhs_.shape[0]:
                raise SimplexException(
                    "Ошибка при вводе данных. Число строк в матрице и столбце ограничений не совпадает.")

            # Если задача на max, то меняем знаки ЦФ и направление задачи (в конце возьмем решение со знаком минус и
            # получим искомое).
            if self.func_direction_ == "max":
                self.obj_func_coffs_ *= -1

            # Инициализация симплекс-таблицы.
            self.simplex_table_ = SimplexTable(self.obj_func_coffs_, self.constraint_system_lhs_,
                                               self.constraint_system_rhs_)

    def __str__(self):
        """
        Переопренный метод __str__ для условия задачи.
        :return: Строка с выводом условия задачи.
        """
        output = """Условие задачи:
------------------------------------------------------------
Найти вектор x = (x1,x2,..., xn)^T как решение след. задачи:"""

        output += f"\nF = cx -> {self.func_direction_},"
        output += "\nAx <= b,\nx1,x2, ..., xn >= 0"
        output += f"\nC = {self.obj_func_coffs_},"
        output += f"\nA =\n{self.constraint_system_lhs_},"
        output += f"\nb^T = {self.constraint_system_rhs_}."
        output += "\n------------------------------------------------------------"

        return output

    # Этап 1. Поиск опорного решения.
    def reference_solution(self):
        """
        Метод производит отыскание опорного решения.
        """
        print("Процесс решения:\n1) Поиск опорного решения:")
        print("Исходная симплекс-таблица:", self.simplex_table_, sep="\n")

        while not self.simplex_table_.is_find_ref_solution():
            self.simplex_table_.search_ref_solution()

        print("-----------")
        print("Опорное решение найдено!")
        self.output_solution()
        print("-----------")

    # Этап 2. Поиск оптимального решения.
    def optimal_solution(self):
        """
        Метод производит отыскание оптимального решения.
        """
        print("2) Поиск оптимального решения:")

        while not self.simplex_table_.is_find_opt_solution():
            self.simplex_table_.optimize_ref_solution()

        # Если задача на max, то в начале свели задачу к поиску min, а теперь
        # возьмём это решение со знаком минус и получим ответ для мак.
        if self.func_direction_ == "max":
            self.simplex_table_.main_table_[self.simplex_table_.main_table_.shape[0] - 1][0] *= -1

        print("-----------")
        print("Оптимальное решение найдено!")
        self.output_solution()
        print("-----------")

    def output_solution(self):
        """
        Метод выводит текущее решение, используется для вывода опорного и потимального решений.
        """
        fict_vars = self.simplex_table_.top_row_[2:]
        last_row_ind = self.simplex_table_.main_table_.shape[0] - 1

        for var in fict_vars:
            print(var, "= ", end="")
        print(0, end=", ")

        for i in range(last_row_ind):
            print(self.simplex_table_.left_column_[i], "= ", round(self.simplex_table_.main_table_[i][0], 1), end=", ")

        print("\nЦелевая функция: F =", round(self.simplex_table_.main_table_[last_row_ind][0], 1))
