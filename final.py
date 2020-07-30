import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import QPrinter
from PyQt5 import Qt

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
        button.setToolTip("<h3>This is for creating random circles<h3>")
        joinb = QPushButton("Join", self)
        joinb.setGeometry(100, 0, 100, 30)
        joinb.clicked.connect(self.join_action)
        joinb.setToolTip('This is for joining the two circles with a line')
        Report = QPushButton("Generate Report", self)
        Report.setGeometry(QRect(200, 0, 100, 30))
        Report.clicked.connect(self.printPDF)
        Report.setToolTip("This is for generating pdf report of connection between two circles")
        self.textEdit = QTextEdit()
        self.textEdit.setGeometry(100, 150, 400, 400)
       

    def on_clicked(self):
        coor = (random.randrange(self.width() - 100), random.randrange(self.height() - 100))
        circleobj = Circle(*coor, 100, 100)
        self.circles.append(circleobj)
        circleobj.line_edit = QLineEdit(self)
        circleobj.line_edit.show()
        self.labels.append(circleobj.line_edit)
        circleobj.line_edit.setText(f'Sphere {len(self.labels)}:')
        circleobj.move_line_edit()

        self.last_two_clicked.insert(0, circleobj)
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

        for circleobj in [x for x in self.circles if x not in (c1, c2)]:
            if circleobj.line_to in (c1, c2):
                circleobj.line_to = None
            if circleobj.line_from in (c1, c2):
                circleobj.line_from = None
            if not circleobj.line_to and not circleobj.line_from:
                if circleobj.join_edit and circleobj.join_edit != c1.join_edit:
                    circleobj.join_edit.setParent(None)
                circleobj.join_edit = None

        c1.join_edit.setText(f'Connection {len(self.linelabels)}:')
        c1.move_join_edit()
        self.textEdit.append(f'[{c1.join_edit.text()}:({c1.line_edit.text()} to {c2.line_edit.text()})')
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # pixmap = QPixmap("self.ImageWindow.png")
        # painter.drawPixmap(self.rect(), pixmap)
        # painter.drawLine(10, 10, self.rect().width() - 10, 10)
        # painter.setPen(QPen(Qt.black, 5, Qt.SolidLine))
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



    def contextMenuEvent(self, event):
        contextmenu = QMenu(self)
        deletecir = contextmenu.addAction("Delete Circle")
        action = contextmenu.exec_(self.mapToGlobal(event.pos()))
        if action == deletecir:
            self.DeleteFigure(event)

    def printPDF(self):
        filen, _ = QFileDialog.getSaveFileName(self, 'Export PDF', None, 'PDF Files(.pdf);;AllFiles()')
        print(filen)
        if filen != '':
            if QFileInfo(filen).suffix() != "pdf":
                filen += '.pdf'
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filen)
            self.textEdit.document().print(printer)


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
        rect.moveCenter(QPoint(int(x / 2), int(y / 2)))
        self.join_edit.move(rect.topLeft())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    Rect = Window()
    Rect.show()
    sys.exit(app.exec_())

