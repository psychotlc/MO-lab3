# Copyright 2020 Alexey Alexandrov <sks2311211@yandex.ru>

from simplex import *


class SimplexBB(Simplex):
    """Класс Simplex для метода ветвей и границ."""

    def __init__(self, obj_func_coffs, constraint_system_lhs, constraint_system_rhs, func_direction):
        self.obj_func_coffs_ = obj_func_coffs  # вектор-строка с - коэффициенты ЦФ
        self.constraint_system_lhs_ = constraint_system_lhs  # матрица ограничений А
        self.constraint_system_rhs_ = constraint_system_rhs  # вектор-столбец ограничений b
        self.func_direction_ = func_direction  # направление задачи (min или max)

        if len(self.constraint_system_rhs_) != self.constraint_system_rhs_.shape[0]:
            raise Exception(
                "Ошибка при вводе данных. Число строк в матрице и столбце ограничений не совпадает.")

        # Инициализация симплекс-таблицы.
        self.simplex_table_ = SimplexTable(self.obj_func_coffs_, self.constraint_system_lhs_,
                                           self.constraint_system_rhs_)
