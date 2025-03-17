# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'color_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QFormLayout, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QSizePolicy, QSlider, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_ColorDialog(object):
    def setupUi(self, ColorDialog):
        if not ColorDialog.objectName():
            ColorDialog.setObjectName(u"ColorDialog")
        ColorDialog.resize(500, 400)
        ColorDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(ColorDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.paletteGroup = QGroupBox(ColorDialog)
        self.paletteGroup.setObjectName(u"paletteGroup")
        self.verticalLayout_2 = QVBoxLayout(self.paletteGroup)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.colorPaletteTable = QTableWidget(self.paletteGroup)
        if (self.colorPaletteTable.columnCount() < 6):
            self.colorPaletteTable.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.colorPaletteTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        if (self.colorPaletteTable.rowCount() < 6):
            self.colorPaletteTable.setRowCount(6)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(0, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(1, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(2, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(3, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(4, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.colorPaletteTable.setVerticalHeaderItem(5, __qtablewidgetitem11)
        self.colorPaletteTable.setObjectName(u"colorPaletteTable")
        self.colorPaletteTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.colorPaletteTable.setShowGrid(True)
        self.colorPaletteTable.horizontalHeader().setVisible(False)
        self.colorPaletteTable.verticalHeader().setVisible(False)

        self.verticalLayout_2.addWidget(self.colorPaletteTable)


        self.horizontalLayout.addWidget(self.paletteGroup)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.selectedColorGroup = QGroupBox(ColorDialog)
        self.selectedColorGroup.setObjectName(u"selectedColorGroup")
        self.verticalLayout_5 = QVBoxLayout(self.selectedColorGroup)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.colorPreviewFrame = QFrame(self.selectedColorGroup)
        self.colorPreviewFrame.setObjectName(u"colorPreviewFrame")
        self.colorPreviewFrame.setMinimumSize(QSize(100, 100))
        self.colorPreviewFrame.setFrameShape(QFrame.Box)
        self.colorPreviewFrame.setFrameShadow(QFrame.Raised)

        self.verticalLayout_5.addWidget(self.colorPreviewFrame)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.htmlLabel = QLabel(self.selectedColorGroup)
        self.htmlLabel.setObjectName(u"htmlLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.htmlLabel)

        self.htmlLineEdit = QLineEdit(self.selectedColorGroup)
        self.htmlLineEdit.setObjectName(u"htmlLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.htmlLineEdit)


        self.verticalLayout_5.addLayout(self.formLayout)


        self.verticalLayout_3.addWidget(self.selectedColorGroup)

        self.colorValuesGroup = QGroupBox(ColorDialog)
        self.colorValuesGroup.setObjectName(u"colorValuesGroup")
        self.verticalLayout_4 = QVBoxLayout(self.colorValuesGroup)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.redLabel = QLabel(self.colorValuesGroup)
        self.redLabel.setObjectName(u"redLabel")

        self.gridLayout.addWidget(self.redLabel, 0, 0, 1, 1)

        self.redSlider = QSlider(self.colorValuesGroup)
        self.redSlider.setObjectName(u"redSlider")
        self.redSlider.setMaximum(255)
        self.redSlider.setOrientation(Qt.Horizontal)

        self.gridLayout.addWidget(self.redSlider, 0, 1, 1, 1)

        self.redSpinBox = QSpinBox(self.colorValuesGroup)
        self.redSpinBox.setObjectName(u"redSpinBox")
        self.redSpinBox.setMaximum(255)

        self.gridLayout.addWidget(self.redSpinBox, 0, 2, 1, 1)

        self.greenLabel = QLabel(self.colorValuesGroup)
        self.greenLabel.setObjectName(u"greenLabel")

        self.gridLayout.addWidget(self.greenLabel, 1, 0, 1, 1)

        self.greenSlider = QSlider(self.colorValuesGroup)
        self.greenSlider.setObjectName(u"greenSlider")
        self.greenSlider.setMaximum(255)
        self.greenSlider.setOrientation(Qt.Horizontal)

        self.gridLayout.addWidget(self.greenSlider, 1, 1, 1, 1)

        self.greenSpinBox = QSpinBox(self.colorValuesGroup)
        self.greenSpinBox.setObjectName(u"greenSpinBox")
        self.greenSpinBox.setMaximum(255)

        self.gridLayout.addWidget(self.greenSpinBox, 1, 2, 1, 1)

        self.blueLabel = QLabel(self.colorValuesGroup)
        self.blueLabel.setObjectName(u"blueLabel")

        self.gridLayout.addWidget(self.blueLabel, 2, 0, 1, 1)

        self.blueSlider = QSlider(self.colorValuesGroup)
        self.blueSlider.setObjectName(u"blueSlider")
        self.blueSlider.setMaximum(255)
        self.blueSlider.setOrientation(Qt.Horizontal)

        self.gridLayout.addWidget(self.blueSlider, 2, 1, 1, 1)

        self.blueSpinBox = QSpinBox(self.colorValuesGroup)
        self.blueSpinBox.setObjectName(u"blueSpinBox")
        self.blueSpinBox.setMaximum(255)

        self.gridLayout.addWidget(self.blueSpinBox, 2, 2, 1, 1)

        self.alphaLabel = QLabel(self.colorValuesGroup)
        self.alphaLabel.setObjectName(u"alphaLabel")

        self.gridLayout.addWidget(self.alphaLabel, 3, 0, 1, 1)

        self.alphaSlider = QSlider(self.colorValuesGroup)
        self.alphaSlider.setObjectName(u"alphaSlider")
        self.alphaSlider.setMaximum(255)
        self.alphaSlider.setValue(255)
        self.alphaSlider.setOrientation(Qt.Horizontal)

        self.gridLayout.addWidget(self.alphaSlider, 3, 1, 1, 1)

        self.alphaSpinBox = QSpinBox(self.colorValuesGroup)
        self.alphaSpinBox.setObjectName(u"alphaSpinBox")
        self.alphaSpinBox.setMaximum(255)
        self.alphaSpinBox.setValue(255)

        self.gridLayout.addWidget(self.alphaSpinBox, 3, 2, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout)


        self.verticalLayout_3.addWidget(self.colorValuesGroup)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ColorDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ColorDialog)
        self.buttonBox.accepted.connect(ColorDialog.accept)
        self.buttonBox.rejected.connect(ColorDialog.reject)
        self.redSlider.valueChanged.connect(self.redSpinBox.setValue)
        self.redSpinBox.valueChanged.connect(self.redSlider.setValue)
        self.greenSlider.valueChanged.connect(self.greenSpinBox.setValue)
        self.greenSpinBox.valueChanged.connect(self.greenSlider.setValue)
        self.blueSlider.valueChanged.connect(self.blueSpinBox.setValue)
        self.blueSpinBox.valueChanged.connect(self.blueSlider.setValue)
        self.alphaSlider.valueChanged.connect(self.alphaSpinBox.setValue)
        self.alphaSpinBox.valueChanged.connect(self.alphaSlider.setValue)

        QMetaObject.connectSlotsByName(ColorDialog)
    # setupUi

    def retranslateUi(self, ColorDialog):
        ColorDialog.setWindowTitle(QCoreApplication.translate("ColorDialog", u"Color Selector", None))
        self.paletteGroup.setTitle(QCoreApplication.translate("ColorDialog", u"Color Palette", None))
        ___qtablewidgetitem = self.colorPaletteTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ColorDialog", u"1", None));
        ___qtablewidgetitem1 = self.colorPaletteTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ColorDialog", u"2", None));
        ___qtablewidgetitem2 = self.colorPaletteTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ColorDialog", u"3", None));
        ___qtablewidgetitem3 = self.colorPaletteTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ColorDialog", u"4", None));
        ___qtablewidgetitem4 = self.colorPaletteTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ColorDialog", u"5", None));
        ___qtablewidgetitem5 = self.colorPaletteTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("ColorDialog", u"6", None));
        ___qtablewidgetitem6 = self.colorPaletteTable.verticalHeaderItem(0)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("ColorDialog", u"1", None));
        ___qtablewidgetitem7 = self.colorPaletteTable.verticalHeaderItem(1)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("ColorDialog", u"2", None));
        ___qtablewidgetitem8 = self.colorPaletteTable.verticalHeaderItem(2)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("ColorDialog", u"3", None));
        ___qtablewidgetitem9 = self.colorPaletteTable.verticalHeaderItem(3)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("ColorDialog", u"4", None));
        ___qtablewidgetitem10 = self.colorPaletteTable.verticalHeaderItem(4)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("ColorDialog", u"5", None));
        ___qtablewidgetitem11 = self.colorPaletteTable.verticalHeaderItem(5)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("ColorDialog", u"6", None));
        self.selectedColorGroup.setTitle(QCoreApplication.translate("ColorDialog", u"Selected Color", None))
        self.htmlLabel.setText(QCoreApplication.translate("ColorDialog", u"HTML:", None))
        self.htmlLineEdit.setPlaceholderText(QCoreApplication.translate("ColorDialog", u"#RRGGBB", None))
        self.colorValuesGroup.setTitle(QCoreApplication.translate("ColorDialog", u"Color Values", None))
        self.redLabel.setText(QCoreApplication.translate("ColorDialog", u"Red:", None))
        self.greenLabel.setText(QCoreApplication.translate("ColorDialog", u"Green:", None))
        self.blueLabel.setText(QCoreApplication.translate("ColorDialog", u"Blue:", None))
        self.alphaLabel.setText(QCoreApplication.translate("ColorDialog", u"Alpha:", None))
    # retranslateUi

