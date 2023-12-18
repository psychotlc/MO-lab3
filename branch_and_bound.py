
import math

from simplex_b_b import *


class BranchAndBound:
    """Класс задачи ветвей и границ."""

    def __init__(self, simplex_problem):
        """
        Переопределённый метод __init__. Определяем условие задачи на основе задачи ЛП.
        :param simplex_problem: задача ЛП.
        """

        self.obj_func_coffs_ = simplex_problem.obj_func_coffs_  # вектор-строка с - коэффициенты ЦФ.
        self.constraint_system_lhs_ = simplex_problem.constraint_system_lhs_  # матрица ограничений А.
        self.constraint_system_rhs_ = simplex_problem.constraint_system_rhs_  # вектор-столбец ограничений b.
        self.func_direction_ = simplex_problem.func_direction_  # направление задачи (min или max).
        self.simplex_table_ = simplex_problem.simplex_table_  # симплекс-таблица

        self.extra_constraints_lhs_ = []  # дополнительные строки ограничений для матрицы А.
        self.extra_constraints_rhs_ = []  # дополнительные элементы ограничений для столбца b.
        self.solutions_storage_ = []  # хранилише целочисленных решений, найденных в ходе ветвления.

        if not is_integer_solution(self.simplex_table_):
            self.branching(self.simplex_table_, self.extra_constraints_lhs_, self.extra_constraints_rhs_)

    def __str__(self):
        """
        Переопренный метод __str__ для вывода задачи ЦЛП методом ветвей и границ.
        :return: Строка с выводом задачи.
        """

        output = "В процессе решения задачи ЦЛП методом ветвей и границ найдены решения:\n"
        for solution in self.solutions_storage_:
            output += f"F = {solution[0]}; x1 = {solution[1][0]}, x2 = {solution[1][1]}, x3 = {solution[1][2]}\n"

        best_solution = self.find_best_solution()
        output += "-------------------\n"
        output += f"Тогда решением задачи ЦЛП будет являться решение:\n" \
                  f"F = {best_solution[0]}; " \
                  f"x1 = {best_solution[1][0]}, " \
                  f"x2 = {best_solution[1][1]}, " \
                  f"x3 = {best_solution[1][2]}\n "
        output += "-------------------"
        return output

    def branching(self, simplex_table, extra_constraints_lhs, extra_constraints_rhs):
        """
        Метод производит ветвление на основе текущей симплекс таблицы.
        :param simplex_table: текущая симплекс таблица.
        :param extra_constraints_lhs: дополнительные ограничения в левой части системы.
        :param extra_constraints_rhs: дополнительные ограничения в правой части системы.
        """

        # В столбце свободных членов симплекс таблицы ищем нецелую и нефиктивную переменную.
        b_var_number, b_var_value = branch_var_search(simplex_table)
        constraint_system_lhs = self.constraint_system_lhs_
        constraint_system_rhs = self.constraint_system_rhs_

        print(f"Осуществим ветвление по переменной x{b_var_number} = {round(b_var_value, 1)}")
        print(
            f"x{b_var_number} <= {math.floor(b_var_value)} и x{b_var_number} >= {math.ceil(b_var_value)} "
            f"(-x{b_var_number} <= {-math.ceil(b_var_value)})")

        # Строка ограничений для ветвления x <= [x*] (левая ветка)

        # Заготавливаем строку ограничений для левой части системы.
        lhs_constraint_temp_row = np.zeros(3)
        lhs_constraint_temp_row[b_var_number - 1] = 1

        extra_constraints_lhs.append(lhs_constraint_temp_row)
        extra_constraints_rhs.append(math.floor(b_var_value))

        for i in range(len(extra_constraints_rhs)):
            # Добавляем строку в левую часть системы ограничений.
            constraint_system_lhs = np.vstack((constraint_system_lhs, extra_constraints_lhs[i]))
            # Добавляем элемент в правую часть системы ограничений.
            constraint_system_rhs = np.append(constraint_system_rhs, extra_constraints_rhs[i])

        # Оборачиваем в try-except: если поднимется исключение в задаче, решение пойдёт дальше по другим веткам и узлам.
        try:
            left_branch_task = SimplexBB(self.obj_func_coffs_, constraint_system_lhs,
                                         constraint_system_rhs,
                                         self.func_direction_)

            print(f"Ограничение: x{b_var_number} <= {math.floor(b_var_value)}")
            left_branch_task.reference_solution()
            left_branch_task.optimal_solution()

            if not is_integer_solution(left_branch_task.simplex_table_):
                print("От левой ветки ветвимся дальше...")
                self.branching(left_branch_task.simplex_table_, extra_constraints_lhs, extra_constraints_rhs)
            else:
                self.add_solution(left_branch_task.simplex_table_)

        except SimplexException as err:
            print(
                f"При ветвлении по x{b_var_number} <= {math.floor(b_var_value)} Решение не было найдено:\n{err}")

        constraint_system_lhs = np.delete(constraint_system_lhs, constraint_system_lhs.shape[0] - 1, axis=0)
        constraint_system_rhs = np.delete(constraint_system_rhs, constraint_system_rhs.shape[0] - 1, axis=0)
        extra_constraints_lhs = extra_constraints_lhs[:-1]
        extra_constraints_rhs = extra_constraints_rhs[:-1]

        # Строка ограничений для ветвления x >= [x*] + 1 (правая ветка)

        # Заготавливаем строку ограничений для левой части системы.
        lhs_constraint_temp_row = np.zeros(3)
        lhs_constraint_temp_row[b_var_number - 1] = -1

        extra_constraints_lhs.append(lhs_constraint_temp_row)
        extra_constraints_rhs.append(-math.ceil(b_var_value))
        # Добавляем строку в левую часть системы ограничений.
        constraint_system_lhs = np.vstack((constraint_system_lhs, lhs_constraint_temp_row))
        # Добавляем элемент в правую часть системы ограничений.
        constraint_system_rhs = np.append(constraint_system_rhs, -math.ceil(b_var_value))

        # Оборачиваем в try-except: если поднимется исключение в задаче, решение пойдёт дальше по другим веткам и узлам.
        try:
            right_branch_task = SimplexBB(self.obj_func_coffs_, constraint_system_lhs,
                                          constraint_system_rhs,
                                          self.func_direction_)
            print(f"Ограничение: x{b_var_number} >= {math.ceil(b_var_value)}")
            right_branch_task.reference_solution()
            right_branch_task.optimal_solution()

            if not is_integer_solution(right_branch_task.simplex_table_):
                print("От правой ветки ветвимся дальше...")
                self.branching(right_branch_task.simplex_table_, extra_constraints_lhs, extra_constraints_rhs)

            if is_integer_solution(right_branch_task.simplex_table_):
                self.add_solution(right_branch_task.simplex_table_)
                return

        except SimplexException as err:
            print(
                f"При ветвлении по x{b_var_number} >= {math.ceil(b_var_value)} Решение не было найдено:\n{err}")

    def find_best_solution(self):
        """Метод производит отыскание наилучшего целочисленного решения среди полученных в ходе ветвлений."""

        if self.func_direction_ == "max":
            maximum_solution = None
            for solution in self.solutions_storage_:
                if maximum_solution is None or maximum_solution[0] < solution[0]:
                    maximum_solution = solution

            return maximum_solution
        else:
            minimum_solution = None
            for solution in self.solutions_storage_:
                if minimum_solution is None or minimum_solution[0] > solution[0]:
                    minimum_solution = solution

            return minimum_solution

    def add_solution(self, simplex_table):
        """Метод добавляет целочисленное решение в self.solutions_storage_."""

        rows_num = simplex_table.main_table_.shape[0]

        f = simplex_table.main_table_[rows_num - 1][0]

        vars_values = [0, 0, 0]

        for i in range(rows_num - 1):
            if simplex_table.left_column_[i] in ["x1", "x2", "x3"]:
                vars_values[int(simplex_table.left_column_[i][1]) - 1] = simplex_table.main_table_[i][0]

        self.solutions_storage_.append((f, vars_values))


def is_integer_solution(simplex_table):
    """
    Проверяет, является ли найденное решение целовчисленным.
    :param simplex_table: текущее состояние задачи ЦЛП.
    return: True - решение задачи ЛП целочисленно. False - не целочисленно.
    """

    for i in range(simplex_table.main_table_.shape[0]):
        if (simplex_table.left_column_[i] in ["x1", "x2", "x3"]) and (not simplex_table.main_table_[i][0].is_integer()):
            return False

    return True


def branch_var_search(simplex_table):
    """
    Производит поиск переменной ветвления в симплекс-таблице.
    :param simplex_table: текущее состояние задачи ЦЛП.
    return: возвращает номер переменной ветвления и её значение в симплекс-таблице.
    """

    for i in range(len(simplex_table.left_column_) - 1):
        if (not simplex_table.main_table_[i][0].is_integer()) and (simplex_table.left_column_[i] in ["x1", "x2", "x3"]):
            return int(simplex_table.left_column_[i][1]), simplex_table.main_table_[i][0]
