#What you are missing it that the joined QLineEdit on the connecting line needs to be created when the join button is pressed. I have removed any parts unnecessary parts of your code, and cleaned it up a bit. I also added in some error handling. The function move_join_edit will keep the QLineEdit in the center of the line, and move it around as the circles get moved by the mouse. Review the Circle class and the join_action function in the main class. It not only pairs up two circles but ensures there are no duplicates and mixed up lines / text boxes.

import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter
class Circle(QRect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_to = self.line_from = self.join_edit = None

    def join(self, other):
        self.line_to = other
        other.line_from = self
        self.line_from = other.line_to = None

    def move_line_edit(self):
        self.line_edit.move(self.topLeft().x(), self.topLeft().y() - 40)

    def move_join_edit(self):
        other = self.line_to if self.line_to else self.line_from
        x = self.center().x() + other.center().x()
        y = self.center().y() + other.center().y()
        rect = self.join_edit.geometry()
        rect.moveCenter(QPoint(x / 2, y / 2))
        self.join_edit.move(rect.topLeft())


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.rect = QRect()
        self.drag_position = QPoint()
        self.circles = []
        self.labels = []
        self.linelabels = []
        self.current_circle = None
        self.last_two_clicked = self.circles[:]

        button = QPushButton("Add", self)
        button.clicked.connect(self.on_clicked)
        joinb = QPushButton("Join", self)
        joinb.setGeometry(100, 0, 100, 30)
        joinb.clicked.connect(self.join_action)

        Delete = QPushButton("Delete", self)
        Delete.setGeometry(200, 0, 100, 30)
        Report = QPushButton("Generate Report", self)
        Report.setGeometry(QRect(300, 0, 120, 30))
        self.textEdit=QTextEdit()
        self.textEdit.setGeometry(100,150,200,200)
        self.textEdit.hide()
        Saveimg = QPushButton("Save", self)
        Saveimg.setGeometry(QRect(420, 0, 100, 30))

        self.resize(640, 480)
    def on_clicked(self):
        coor = (random.randrange(self.width() - 100), random.randrange(self.height() - 100))
        c = Circle(*coor, 100, 100)
        self.circles.append(c)
        c.line_edit = QLineEdit(self)
        c.line_edit.show()
        self.labels.append(c.line_edit)
        c.line_edit.setText(f'Circle {len(self.labels)}')
        c.move_line_edit()

        self.last_two_clicked.insert(0, c)
        self.last_two_clicked = self.last_two_clicked[:2]
        self.update()

    def join_action(self):
        try:
            c1, c2 = self.last_two_clicked
        except ValueError:
            return
        if (c1.line_to == c2 and c2.line_from == c1) or (c1.line_from == c2 and c2.line_to == c1):
            return

        c1.join(c2)
        if c1.join_edit and c2.join_edit and c1.join_edit != c2.join_edit:
            c2.join_edit.setParent(None)
            c2.join_edit = c1.join_edit
        elif c1.join_edit and not c2.join_edit:
            c2.join_edit = c1.join_edit
        elif c2.join_edit and not c1.join_edit:
            c1.join_edit = c2.join_edit
        elif not c1.join_edit and not c2.join_edit:
            c1.join_edit = c2.join_edit = QLineEdit(self)
            c1.join_edit.show()
            self.linelabels.append(c1.join_edit)

        for c in [x for x in self.circles if x not in (c1, c2)]:
            if c.line_to in (c1, c2):
                c.line_to = None
            if c.line_from in (c1, c2):
                c.line_from = None
            if not c.line_to and not c.line_from:
                if c.join_edit and c.join_edit != c1.join_edit:
                    c.join_edit.setParent(None)
                c.join_edit = None

        c1.join_edit.setText(f'Line {len(self.linelabels)}')
        c1.move_join_edit()
        self.textEdit.setText("")
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
        for circle in self.circles:
            painter.drawEllipse(circle)
            if circle.line_to:
                painter.drawLine(circle.center(), circle.line_to.center())

    def mousePressEvent(self, event):
        for circle in self.circles:
            line = QLineF(circle.center(), event.pos())
            if line.length() < circle.width() / 2:
                self.current_circle = circle
                self.drag_position = event.pos()
                if not self.last_two_clicked[0] == circle:
                    self.last_two_clicked.insert(0, circle)
                self.last_two_clicked = self.last_two_clicked[:2]
                break

    def mouseMoveEvent(self, event):
        if self.current_circle is not None:
            self.current_circle.translate(event.pos() - self.drag_position)
            self.current_circle.move_line_edit()
            if self.current_circle.join_edit:
                self.current_circle.move_join_edit()
            self.drag_position = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        self.current_circle = None
    # def printPDF(self):
    #     fn,_=_QFileDialog.getSaveFileName(self,'Export PDF',None,'PDF Files(.pdf);;AllFiles()')
    #     if fn!='':
    #         if QFileInfo(fn).suffix()=="":fn+='.pdf':
    #            printer=QPrinter(QPrinter.HighResolution)
    #            printer.setOutputFormat(QPrinter.Pdf Format)
    #            printer.setOutputFileName(fn)
    #            self.textEdit.document().print._(QPrinter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    Rect = Window()
    Rect.show()
    sys.exit(app.exec_())
