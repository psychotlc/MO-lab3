
import json
import numpy as np


class BruteForceMethod:
    """Класс для решения задачи ЦЛП путём полного перебора."""

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
                raise Exception("Ошибка при вводе данных. Число строк в матрице и столбце ограничений не совпадает.")

            if len(self.constraint_system_rhs_) > len(self.obj_func_coffs_):
                raise Exception("СЛАУ несовместна! Число уравнений больше числа переменных.")

            self.all_solutions_ = self.list_of_solutions()
            self.max_ind_, self.max_func_value_ = self.search_optimal_solution()

    def __str__(self):
        """
        Переопренный метод __str__ для вывода всех целочисленных решений, включая наилучшее.
        :return: Строка с выводом всех решений и наилучшего из них.
        """

        output = "Метод полного перебора.\n"
        output += f"Всего имеется {len(self.all_solutions_)} допустимых целочисленных решений:\n"
        for solution in self.all_solutions_:
            output += f"({solution[0]}, {solution[1]}, {solution[2]});\n"

        output += "-----------\n"
        output += "Полный перебор всех решений даёт решение:\n"
        output += f"x1 = {self.all_solutions_[self.max_ind_][0]}," \
                  f" x2 = {self.all_solutions_[self.max_ind_][1]}," \
                  f" x3 = {self.all_solutions_[self.max_ind_][2]}," \
                  f" F = {self.max_func_value_} \n"
        output += "-----------\n"

        return output

    def is_satisfies_constraints(self, x1, x2, x3):
        """
        Метод проверяет, удовлетворяет ли заданный набор значений переменных ограничениям.
        :return: True -- удовлетворяет ограничениям, False -- не удовлетворяет им.
        """
        for i in range(len(self.constraint_system_rhs_)):
            if self.constraint_system_lhs_[i][0] * x1 + \
                    self.constraint_system_lhs_[i][1] * x2 + \
                    self.constraint_system_lhs_[i][2] * x3 > self.constraint_system_rhs_[i]:
                return False

        return True

    def list_of_solutions(self):
        """
        Перебирает все возможные целочисленные значения переменных и добавляет их в список.
        :return: Список решений задачи ЦЛП.
        """
        maximum = 0
        list_of_solutions = []

        # Находим максимальное в столбце ограничений
        for i in range(len(self.constraint_system_lhs_)):
            if self.constraint_system_rhs_[i] > maximum:
                maximum = self.constraint_system_rhs_[i]

        for x1 in range(maximum + 1):
            for x2 in range(maximum + 1):
                for x3 in range(maximum + 1):
                    if self.is_satisfies_constraints(x1, x2, x3):
                        list_of_solutions.append(np.array([x1, x2, x3]))

        return list_of_solutions

    def search_optimal_solution(self):
        """
        В списке всех целочисленных решений производит отыскание максимального.
        :return: возвращает индекс решения задачи ЦЛП в списке целочисленных решений и сам набор значений переменных.
        """
        list_of_func_values = []

        # Получаем список
        for i in range(len(self.all_solutions_)):
            f = 0
            for j in range(len(self.obj_func_coffs_)):
                f += self.obj_func_coffs_[j] * self.all_solutions_[i][j]
            list_of_func_values.append(f)

        # В этом списке ищем максимальное значение ЦФ и находим её индекс.
        max_f_ind = 0
        for i in range(len(list_of_func_values)):
            if list_of_func_values[i] > list_of_func_values[max_f_ind]:
                max_f_ind = i

        return max_f_ind, list_of_func_values[max_f_ind]
