
import numpy as np
import warnings


class SimplexException(Exception):
    """Пользовательское исключение для решения задач симплекс-методом."""

    def __init__(self, text):
        self.txt = text


class SimplexTable:
    """
    Класс симплекс-таблицы.
    """

    def __init__(self, obj_func_coffs, constraint_system_lhs, constraint_system_rhs):
        """
        Переопределённый метод __init__ для создания экземпляра класса SimplexTable.
        :param obj_func_coffs: коэффициенты ЦФ.
        :param constraint_system_lhs: левая часть системы ограничений.
        :param constraint_system_rhs: правая часть системы ограничений.
        """
        var_count = len(obj_func_coffs)
        constraint_count = constraint_system_lhs.shape[0]

        # Заполнение верхнего хедера.
        self.top_row_ = ["  ", "Si0"]
        for i in range(var_count):
            self.top_row_.append("x" + str(i + 1))

        # Заполнение левого хедера.
        self.left_column_ = []
        ind = var_count
        for i in range(constraint_count):
            ind += 1
            self.left_column_.append("x" + str(ind))
        self.left_column_.append("F ")

        self.main_table_ = np.zeros((constraint_count + 1, var_count + 1))
        # Заполняем столбец Si0.
        for i in range(constraint_count):
            self.main_table_[i][0] = constraint_system_rhs[i]
        # Заполняем строку F.
        for j in range(var_count):
            self.main_table_[constraint_count][j + 1] = -obj_func_coffs[j]

        # Заполняем А.
        for i in range(constraint_count):
            for j in range(var_count):
                self.main_table_[i][j + 1] = constraint_system_lhs[i][j]

    def __str__(self):
        """
        Переопренный метод __str__ для симплекс-таблицы.
        :return: Строка с выводом симплекс-таблицы.
        """
        output = ""
        for header in self.top_row_:
            output += '{:>6}'.format(header)
        output += "\n"

        for i in range(self.main_table_.shape[0]):
            output += '{:>6}'.format(self.left_column_[i])
            for j in range(self.main_table_.shape[1]):
                output += '{:>6}'.format(round(self.main_table_[i][j], 1))
            output += "\n"

        return output

    def is_find_ref_solution(self):
        """
        Функция проверяет, найдено ли опорное решение по свободным в симплекс-таблице.
        :return: True - опорное решение уже найдено. False - полученное решение пока не является опорным.
        """

        # Проверяем все, кроме коэффициента ЦФ
        for i in range(self.main_table_.shape[0] - 1):
            if self.main_table_[i][0] < 0:
                return False
        return True

    def search_ref_solution(self):
        """
        Функция производит одну итерацию поиска опорного решения.
        """
        res_row = None
        for i in range(self.main_table_.shape[0] - 1):
            if self.main_table_[i][0] < 0:
                res_row = i
                break

        # Если найден отрицательный элемент в столбце свободных членов, то ищем первый отрицательный в строке с ней.
        res_col = None
        if res_row is not None:
            for j in range(1, self.main_table_.shape[1]):
                if self.main_table_[res_row, j] < 0:
                    res_col = j
                    break

        # Если найден разрешающий столбец, то находим в нём разрешающий элемент.
        res_element = None
        if res_col is not None:
            # Ищем минимальное положительное отношение Si0 / x[res_col]
            minimum = None
            ind = -1
            # for i in range(self.main_table_.shape[0] - 1):
            #     curr = self.main_table_[i][0] / self.main_table_[i][res_col]
            #     if curr <= 0 or (self.main_table_[i][res_col] == 0):
            #         continue
            #     elif minimum is None:
            #         minimum = curr
            #         ind = i
            #     elif curr < minimum:
            #         minimum = curr
            #         ind = i
            for i in range(self.main_table_.shape[0] - 1):
                # Ищем минимальное отношение -- разрешающую строку.
                curr = self.main_table_[i][res_col]
                s_i0 = self.main_table_[i][0]
                if curr == 0:
                    continue
                elif (s_i0 / curr) > 0 and (minimum is None or (s_i0 / curr) < minimum):
                    minimum = (s_i0 / curr)
                    ind = i

            if minimum is None:
                raise SimplexException("Решения не существует! При нахождении опорного решения не нашлось минимального "
                                       "положительного отношения.")
            else:
                res_row = ind

            # Разрешающий элемент найден.
            res_element = self.main_table_[res_row][res_col]
            print("Разрешающая строка: {}".format(self.left_column_[res_row]))
            print("Разрешающий столбец: {}".format(self.top_row_[res_col + 1]))

            # Пересчёт симплекс-таблицы.
            self.recalc_table(res_row, res_col, res_element)
        else:
            raise SimplexException("Задача не имеет допустимых решений! При нахождении опорного решения не нашлось "
                                   "отрицательного элемента в строке с отрицательным свободным членом.")

    def is_find_opt_solution(self):
        """
        Функция проверяет, найдено ли оптимальное решение по коэффициентам ЦФ в симплекс-таблице.
        :return: True - оптимальное решение уже найдено. False - полученное решение пока не оптимально.
        """

        for i in range(1, self.main_table_.shape[1]):
            if self.main_table_[self.main_table_.shape[0] - 1][i] > 0:
                return False
        # Если положительных не нашлось, то оптимальное решение уже найдено.
        return True

    def optimize_ref_solution(self):
        """
        Функция производит одну итерацию поиска оптимального решения на основе
        уже полученного опорного решения.
        """
        res_col = None
        ind_f = self.main_table_.shape[0] - 1

        # В строке F ищем первый положительный.
        for j in range(1, self.main_table_.shape[1]):
            curr = self.main_table_[ind_f][j]
            if curr > 0:
                res_col = j
                break

        minimum = None
        res_row = None

        # Идём по всем, кроме ЦФ ищём минимальное отношение.
        for i in range(self.main_table_.shape[0] - 1):
            # Ищем минимальное отношение -- разрешающую строку.
            curr = self.main_table_[i][res_col]
            s_i0 = self.main_table_[i][0]
            if curr < 0:
                continue
            elif (s_i0 / curr) >= 0 and (minimum is None or (s_i0 / curr) < minimum):
                minimum = (s_i0 / curr)
                res_row = i

        if res_row is None:
            raise SimplexException("Функция не ограничена! Оптимального решения не существует.")

        else:
            # Разрешающий элемент найден.
            res_element = self.main_table_[res_row][res_col]
            print("Разрешающая строка: {}".format(self.left_column_[res_row]))
            print("Разрешающий столбец: {}".format(self.top_row_[res_col + 1]))
            # Пересчёт симплекс-таблицы.
            self.recalc_table(res_row, res_col, res_element)

    def recalc_table(self, res_row, res_col, res_element):
        """
        Функция по заданным разрешающим строке, столбцу и элекменту производит перерасчёт
        симплекс-таблицы методом жордановых искоючений.
        :param res_row: индекс разрешающей строки
        :param res_col: индекс разрешающего столбца
        :param res_element: разрешающий элемент
        """

        recalced_table = np.zeros((self.main_table_.shape[0], self.main_table_.shape[1]))

        # Пересчёт разрешающего элемента.
        recalced_table[res_row][res_col] = 1 / res_element

        # Пересчёт разрешающей строки.
        for j in range(self.main_table_.shape[1]):
            if j != res_col:
                recalced_table[res_row][j] = self.main_table_[res_row][j] / res_element

        # Пересчёт разрешающего столбца.
        for i in range(self.main_table_.shape[0]):
            if i != res_row:
                recalced_table[i][res_col] = -(self.main_table_[i][res_col] / res_element)

        # Пересчёт оставшейся части таблицы.
        for i in range(self.main_table_.shape[0]):
            for j in range(self.main_table_.shape[1]):
                if (i != res_row) and (j != res_col):
                    recalced_table[i][j] = self.main_table_[i][j] - (
                            (self.main_table_[i][res_col] * self.main_table_[res_row][j]) / res_element)

        self.main_table_ = recalced_table

        self.swap_headers(res_row, res_col)

        print(self.__str__())

    def swap_headers(self, res_row, res_col):
        """
        Функция меняет меняет переменные в строке и столбце местами.
        :param res_row: разрешающая строка
        :param res_col: разрешающий столбец
        """

        temp = self.top_row_[res_col + 1]
        self.top_row_[res_col + 1] = self.left_column_[res_row]
        self.left_column_[res_row] = temp


warnings.filterwarnings("ignore", category=RuntimeWarning)
