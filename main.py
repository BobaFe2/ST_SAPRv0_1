import sys
import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure

from interface import *
from PyQt5 import (
    QtCore,
    QtGui,
    QtWidgets,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QWidget,
)


class GraphWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        fig = Figure(figsize=(5, 5))
        self.can = FigureCanvasQTAgg(fig)
        self.toolbar = NavigationToolbar2QT(self.can, self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.can)

        # here you can set up your figure/axis
        self.ax = self.can.figure.add_subplot(111)

    def plot_basic_line(self, X, Y, label):
        # plot a basic line plot from x and y values.
        self.ax.cla() # clears the axis
        self.ax.plot(X, Y, label=label)
        self.ax.grid(True)
        self.ax.legend()
        self.can.figure.tight_layout()
        self.can.draw()


class GraphRendererSignals(QtCore.QObject):
    # SIGNALS
    CLOSE = QtCore.pyqtSignal()

class GraphRenderer(QtWidgets.QWidget):
    def __init__(
        self,
        parent=None,
        x_values=[],
        y_values=[],
    ):
        super(GraphRenderer, self).__init__(parent)

        self.x_values = x_values
        self.y_values = y_values

        fig = Figure(figsize=(5, 5), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        ax.plot(x_values, y_values, label='График функции')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        ax.legend()
        
        # Создай новое окно для графика
        graph_window = QtWidgets.QMainWindow()
        graph_window.setWindowTitle('График')
        graph_window.setGeometry(100, 100, 800, 600)

        # Добавь виджет с графиком в центральную область окна
        graph_window.setCentralWidget(canvas)

        # Покажи окно с графиком
        graph_window.show()

        # make the window frameless
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.fillColor = QtGui.QColor(30, 30, 30, 120)
        self.penColor = QtGui.QColor("#333333")

        self.popup_fillColor = QtGui.QColor(240, 240, 240, 255)
        self.popup_penColor = QtGui.QColor(200, 200, 200, 255)

        self.close_btn = QtWidgets.QPushButton(self)
        self.close_btn.setText("x")
        font = QtGui.QFont()
        font.setPixelSize(18)
        font.setBold(True)
        self.close_btn.setFont(font)
        self.close_btn.setStyleSheet("background-color: rgb(0, 0, 0, 0)")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self._onclose)

        self.SIGNALS = GraphRendererSignals()

    def resizeEvent(self, event):
        s = self.size()
        popup_width = 800
        popup_height = 800
        ow = int(s.width() / 2 - popup_width / 2)
        oh = int(s.height() / 2 - popup_height / 2)
        self.close_btn.move(ow + 265, oh + 5)

    def paintEvent(self, event):
        # This method is, in practice, drawing the contents of
        # your window.

        # get current window size
        s = self.size()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(self.penColor)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        # drawpopup
        qp.setPen(self.popup_penColor)
        qp.setBrush(self.popup_fillColor)
        popup_width = 800
        popup_height = 800
        ow = int(s.width() / 2 - popup_width / 2)
        oh = int(s.height() / 2 - popup_height / 2)
        qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)

        font = QtGui.QFont()
        font.setPixelSize(18)
        font.setBold(True)
        qp.setFont(font)
        qp.setPen(QtGui.QColor(70, 70, 70))
        tolw, tolh = 80, -5

        qp.end()

    def _onclose(self):
        print("Close")
        self.SIGNALS.CLOSE.emit()


class CAE(QtWidgets.QMainWindow, Ui_MainWindow):
    node_mas = []
    rod_hei = []
    rod_upr = []
    rod_direction = []
    force_SU = []
    force_type = []
    force_value = []

    is_left_support = True
    is_right_support = False

    def __init__(self, parent=None):
        try:
            QtWidgets.QWidget.__init__(self, parent)
            self.setupUi(self)

            # image button
            self.refresh.clicked.connect(self.refresh_plot)

            # support
            self.left_support.clicked.connect(self.render_left_support)
            self.right_support.clicked.connect(self.render_right_support)
            self.dual_support.clicked.connect(self.render_dual_support)

            # menu
            self.menu_open.triggered.connect(self.file_open)
            self.menu_save.triggered.connect(self.file_save)
            self.menu_calc.triggered.connect(self.calc)
            self.show_graph.triggered.connect(self.render_graph)

            self.menu_help.triggered.connect(self.help)
            self.menu_about.triggered.connect(self.info)

        except Exception as e:
            print(e)

    def render_graph(self):
        n_forces = self.calc()
 
        y_values = n_forces
        x_values = list(range(1, len(y_values) + 1))

        graph_window = GraphWindow(self)
        X, Y = (1, 2), (1, 2)
        graph_window.plot_basic_line(X, Y, label='plot1')

        """
        self._popframe = GraphRenderer(self, x_values, y_values)

        self._popframe.move(0, 0)
        self._popframe.resize(self.width(), self.height())
        self._popframe.SIGNALS.CLOSE.connect(self._closepopup)
        self._popflag = True
        self._popframe.show()
        """

    def _closepopup(self):
        self._popframe.close()
        self._popflag = False

    def calc(self):
        if self.check_arrays():
            l = []
            for i in range(len(self.node_mas)-1):
                l.append(self.node_mas[i+1] - self.node_mas[i])
            e = self.rod_upr
            a = self.rod_hei
            u: int = len(l)+1  # размер массива узлов
            k = []

            for i in range(len(l)):
                k.append(e[i]*a[i]/l[i])

            m = [0] * u
            for i in range(u):
                m[i] = [0] * u
            m[0][0] = k[0]
            m[-1][-1] = k[-1]

            if len(m) > 2:
                for i in range(len(m)-1):
                    for j in range(len(m)-1):
                        if i == j:
                            m[i][j+1] = -k[i]
                            m[i+1][j] = -k[i]

                for i in range(1, len(m)-1):
                    m[i][i] = k[i] + k[i-1]

            """-vector b-"""
            f = [0] * u
            q = [0] * len(l)
            q_2 = [0] * len(l)

            for i in range(len(self.force_type)):
                if self.force_type[i] == 1:
                    f[self.force_SU[i]-1] = (self.force_value[i])
                elif self.force_type[i] == 2:
                    q[self.force_SU[i]-1] = (self.force_value[i] * l[self.force_SU[i] - 1] / 2)
                    q_2[self.force_SU[i]-1] = self.force_value[i]

            b = [q[0] + f[0]]
            for i in range(1, u-1):
                b.append(q[i-1] + q[i] + f[i])
            b.append(q[-1] + f[-1])

            if self.is_left_support:
                m[0][0] = 1
                m[0][1] = 0
                b[0] = 0
            if self.is_right_support:
                m[-1][-1] = 1
                m[-1][-2] = 0
                b[-1] = 0

            M = np.array(m)
            det = np.linalg.det(M)
            if det != 0:
                print(M)
                print(b)
                delta = list(np.linalg.solve(M, b))
                del_mes = 'deltas = ['
                for i in delta:
                    del_mes += str(i)+', '
                del_mes += ']'
                QtWidgets.QMessageBox.information(self,
                                                  "Результаты расчета", del_mes,
                                                  buttons=QtWidgets.QMessageBox.Close)
                return self.calc_n_forces(delta, e, a, l, q_2, self.node_mas)
            else:
                self.det_error()

        else: self.alert_nan()

#n_forces=[],
#sigma_tensions=[],
#u_moves=[],
    
    def calc_n_forces(self, delta, e, a, l, q, node_mas):
        print(delta, e, a, l, q, node_mas)
        n_forces = []
        u = delta
        x = node_mas

        for i in range(len(a)):
            n_forces.append(self.calc_n(e[i], a[i], l[i], q[i], x[i], u[i], u[i + 1]))
            n_forces.append(self.calc_n(e[i], a[i], l[i], q[i], x[i + 1], u[i], u[i + 1]))
            print(i, n_forces)

        if len(a) > 1:
            crutch = n_forces[-3] - n_forces[-2]
            print("crutch", crutch)
            n_forces[-1] += crutch
            n_forces[-2] += crutch

        return n_forces

    def calc_n(self, e, a, l, q, x, u1, u2):
        return (e * a) * (u2 - u1) / l + (q * l / 2) * (1 - 2 * x / l)

    def get_sigma_tensions(self, delta):
        ...

    def get_u_moves(self, delta):
        ...

    def refresh_plot(self):
        try:
            if self.check_text():
                # узлы
                self.node_mas = self.conv(self.NodeTable.toPlainText())
                self.node_mas.sort()
                # стержни
                self.rod_hei = self.conv(self.RodTable_3.toPlainText())
                self.rod_upr = self.conv(self.RodTable_4.toPlainText())
                self.rod_direction = self.conv(self.RodTable_5.toPlainText())
                # силы
                self.force_SU = self.conv(self.ForceTable_1.toPlainText())
                self.force_type = self.conv(self.ForceTable_2.toPlainText())
                self.force_value = self.conv(self.ForceTable_3.toPlainText())

                if self.check_arrays():
                    self.draw()
                else: self.alert_nan()
            else: self.alert()
        except Exception as e:
            print(e)

    def check_arrays(self):
        flag = True
        if len(self.node_mas) < 2: flag = False
        if len(self.rod_hei) != len(self.node_mas)-1: flag = False
        if len(self.rod_upr) != len(self.node_mas)-1: flag = False
        if len(self.rod_direction) != len(self.node_mas)-1: flag = False
        for i in self.rod_upr:
            if i < 0: flag = False
        for i in self.rod_direction:
            if i < 0: flag = False

        for i in self.force_SU:
            if i > len(self.node_mas): flag = False
            if self.force_type == 2 and self.force_SU > len(self.force_SU):
                flag = False
        if len(self.force_type) != len(self.force_SU): flag = False
        if len(self.force_value) != len(self.force_SU): flag = False
        return flag

    def check_text(self):
        flag = True
        if self.NodeTable.toPlainText() == '': flag = False
        if self.RodTable_3.toPlainText() == '': flag = False
        if self.RodTable_4.toPlainText() == '': flag = False
        if self.RodTable_5.toPlainText() == '': flag = False
        if self.ForceTable_1.toPlainText() == '': flag = False
        if self.ForceTable_2.toPlainText() == '': flag = False
        if self.ForceTable_3.toPlainText() == '': flag = False
        return flag

    def file_save(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить файл', '.', 'Sapr (*.sapr)')[0]
        if not name:
            self.name_alert()
        elif self.check_text() and self.check_arrays():
            file = open(name, 'w')
            file.write(self.NodeTable.toPlainText()+'\n')
            file.write(self.RodTable_3.toPlainText()+'\n')
            file.write(self.RodTable_4.toPlainText()+'\n')
            file.write(self.RodTable_5.toPlainText()+'\n')
            file.write(self.ForceTable_1.toPlainText()+'\n')
            file.write(self.ForceTable_2.toPlainText()+'\n')
            file.write(self.ForceTable_3.toPlainText())
            file.close()
        else: self.alert()

    def file_open(self):
        text_arr = []
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть файл', '.', 'Sapr (*.sapr)')[0]
        if name:
            file = open(name, 'r')
            with file:
                for line in file:
                    data = line.rstrip('\n')
                    text_arr.append(data)
            # Nodes
            self.NodeTable.setText(text_arr[0])
            # Rods
            self.RodTable_3.setText(text_arr[1])
            self.RodTable_4.setText(text_arr[2])
            self.RodTable_5.setText(text_arr[3])
            # Forces
            self.ForceTable_1.setText(text_arr[4])
            self.ForceTable_2.setText(text_arr[5])
            self.ForceTable_3.setText(text_arr[6])

        if self.check_text():
            self.refresh_plot()

    def draw(self):
        scene = QtWidgets.QGraphicsScene()
        self.paint_widget.setScene(scene)
        pen = QtGui.QPen(QtCore.Qt.black)
        no_pen = QtGui.QPen(QtCore.Qt.NoPen)
        os_pen = QtGui.QPen(QtCore.Qt.DashDotLine)
        s_pen = QtGui.QPen(QtCore.Qt.red)
        r_pen = QtGui.QPen(QtCore.Qt.green)
        rr_pen = QtGui.QPen(QtCore.Qt.green)
        s_pen.setWidth(3)
        rr_pen.setWidth(3)
        brush = QtGui.QBrush(QtCore.Qt.DiagCrossPattern)
        brush2 = QtGui.QBrush(QtGui.QColor(40, 250, 40),
                              QtCore.Qt.VerPattern)

        node_arr = self.node_mas.copy()
        rod_hei = self.rod_hei.copy()
        for i in range(len(node_arr)):
            node_arr[i] = node_arr[i] * 50
        for i in range(len(rod_hei)):
            rod_hei[i] = rod_hei[i] * 50

        middle = 140
        x0 = 615/2 - (node_arr[-1] - node_arr[0])/2
        sh = 10
        scene.addLine(0, middle, 615, middle, os_pen)

        # отрисовка заделки
        for i in range(len(node_arr)-1):
            r = QtCore.QRectF(x0+node_arr[i]+sh, middle-rod_hei[i]/2,
                              node_arr[i+1]-node_arr[i], rod_hei[i])
            scene.addRect(r, pen)
    
        # отрисовка сил
        for j in range(len(self.force_SU)):
            i = self.force_SU[j]-1
            if self.force_type[j] == 1:
                if self.force_value[j] > 0:
                    scene.addLine(x0+node_arr[i]+sh*2, middle-sh,
                                  x0+node_arr[i]+sh*3, middle, s_pen)
                    scene.addLine(x0+node_arr[i]+sh*2, middle+sh,
                                  x0+node_arr[i]+sh*3, middle, s_pen)
                    scene.addLine(x0+node_arr[i]+sh, middle,
                                  x0+node_arr[i]+sh*3, middle, s_pen)
                elif self.force_value[j] < 0:
                    scene.addLine(x0+node_arr[i], middle-sh,
                                  x0+node_arr[i]-sh, middle, s_pen)
                    scene.addLine(x0+node_arr[i], middle+sh,
                                  x0+node_arr[i]-sh, middle, s_pen)
                    scene.addLine(x0+node_arr[i]+sh, middle,
                                  x0+node_arr[i]-sh, middle, s_pen)
                elif self.force_value[j] == 0:
                    pass
            elif self.force_type[j] == 2:
                if self.force_value[j] > 0:
                    r = QtCore.QRectF(x0+node_arr[i]+sh, middle-sh,
                                      node_arr[i+1]-node_arr[i], sh*2)
                    scene.addRect(r, r_pen, brush2)

                    scene.addLine(x0+node_arr[i]+sh*3, middle-sh,
                                  x0+node_arr[i]+sh*4, middle, rr_pen)
                    scene.addLine(x0+node_arr[i]+sh*3, middle+sh,
                                  x0+node_arr[i]+sh*4, middle, rr_pen)
                    scene.addLine(x0+node_arr[i]+sh, middle,
                                  x0+node_arr[i]+sh*4, middle, rr_pen)
                elif self.force_value[j] < 0:
                    r = QtCore.QRectF(x0+node_arr[i]+sh, middle-sh,
                                      node_arr[i+1]-node_arr[i], sh*2)
                    scene.addRect(r, r_pen, brush2)
                    # стрелка влево
                    scene.addLine(x0+node_arr[i+1]-sh, middle-sh,
                                  x0+node_arr[i+1]-sh*2, middle, rr_pen)
                    scene.addLine(x0+node_arr[i+1]-sh, middle+sh,
                                  x0+node_arr[i+1]-sh*2, middle, rr_pen)
                    scene.addLine(x0+node_arr[i+1]+sh, middle,
                                  x0+node_arr[i+1]-sh*2, middle, rr_pen)
                elif self.force_value[j] == 0:
                    pass
            else:
                QtWidgets.QMessageBox.critical(self, "ERROR!",
                                               'Введены неверные данные в поле "Типы сил"!',
                                               defaultButton=QtWidgets.QMessageBox.Ok)

        # отрисовка заделок
        if self.is_left_support:
            rl = QtCore.QRectF(x0+node_arr[0], middle-rod_hei[0]/2-sh,
                               sh-1, rod_hei[0]+2*sh)
            scene.addRect(rl, no_pen, brush)

        if self.is_right_support:
            rr = QtCore.QRectF(x0+node_arr[-1]+sh+1, middle-rod_hei[-1]/2-sh,
                               sh+1, rod_hei[-1]+2*sh)
            scene.addRect(rr, no_pen, brush)

    def render_left_support(self):
        self.is_left_support = True
        self.is_right_support = False
        self.refresh_plot()

    def render_right_support(self):
        self.is_left_support = False
        self.is_right_support = True
        self.refresh_plot()

    def render_dual_support(self):
        self.is_right_support = True
        self.is_left_support = True
        self.refresh_plot()

    def conv(self, data):
        data = data.split(' ')
        for i in range(len(data)):
            data[i] = int(data[i])
        return data

    def alert(self):
        QtWidgets.QMessageBox.critical(self, "ERROR!",
                                       "Введены не все данные!", defaultButton = QtWidgets.QMessageBox.Ok)

    def name_alert(self):
        QtWidgets.QMessageBox.critical(self, "ERROR!",
                                       "Файл не был сохранен!", defaultButton = QtWidgets.QMessageBox.Ok)

    def alert_nan(self):
        QtWidgets.QMessageBox.critical(self, "ERROR!",
                                       "Введены неверные данные!", defaultButton = QtWidgets.QMessageBox.Ok)

    def det_error(self):
        QtWidgets.QMessageBox.critical(self, "ERROR!",
                                       "Вырожденная матрица!", defaultButton = QtWidgets.QMessageBox.Ok)

    def info(self):
        QtWidgets.QMessageBox.about(self,
                                    "О разработчике", 'Программу разработал студент группы ИДБ-21-09 Жданов Никита Артемьевич')

    def help(self):
        QtWidgets.QMessageBox.about(self,
                                    "Помощь", 'Вводите данные через пробел, координаты узлов начинаются с "0", расстояние между узлами считается в метрах, площадь считается в квадратных метрах, количество чисел во всех полях "Стержни" должно совпадать друг с другом, количество чисел во всех полях "Силы" должно совпадать друг с другом, в поле "Тип" группы "Силы" допустим ввод только "1" и "2", в полях "Упругость" и "Максимальное напряжение" отрицательные числа недопустимы, перед рассчетом конструкции убедитесь что все заделки выставлены.')
        
        
if __name__ == '__main__':
    qt = QtWidgets.QApplication(sys.argv)
    cae = CAE()
    cae.show()
    sys.exit(qt.exec_())
