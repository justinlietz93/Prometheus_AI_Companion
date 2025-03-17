# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'font_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QListView, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_FontDialog(object):
    def setupUi(self, FontDialog):
        if not FontDialog.objectName():
            FontDialog.setObjectName(u"FontDialog")
        FontDialog.resize(450, 500)
        FontDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(FontDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.fontFamilyGroup = QGroupBox(FontDialog)
        self.fontFamilyGroup.setObjectName(u"fontFamilyGroup")
        self.fontFamilyLayout = QVBoxLayout(self.fontFamilyGroup)
        self.fontFamilyLayout.setObjectName(u"fontFamilyLayout")
        self.fontFamilyListView = QListView(self.fontFamilyGroup)
        self.fontFamilyListView.setObjectName(u"fontFamilyListView")
        self.fontFamilyListView.setAlternatingRowColors(True)

        self.fontFamilyLayout.addWidget(self.fontFamilyListView)


        self.verticalLayout.addWidget(self.fontFamilyGroup)

        self.fontOptionsLayout = QHBoxLayout()
        self.fontOptionsLayout.setObjectName(u"fontOptionsLayout")
        self.fontStyleGroup = QGroupBox(FontDialog)
        self.fontStyleGroup.setObjectName(u"fontStyleGroup")
        self.fontStyleLayout = QVBoxLayout(self.fontStyleGroup)
        self.fontStyleLayout.setObjectName(u"fontStyleLayout")
        self.fontStyleListView = QListView(self.fontStyleGroup)
        self.fontStyleListView.setObjectName(u"fontStyleListView")
        self.fontStyleListView.setAlternatingRowColors(True)

        self.fontStyleLayout.addWidget(self.fontStyleListView)


        self.fontOptionsLayout.addWidget(self.fontStyleGroup)

        self.fontSizeGroup = QGroupBox(FontDialog)
        self.fontSizeGroup.setObjectName(u"fontSizeGroup")
        self.fontSizeLayout = QVBoxLayout(self.fontSizeGroup)
        self.fontSizeLayout.setObjectName(u"fontSizeLayout")
        self.fontSizeListView = QListView(self.fontSizeGroup)
        self.fontSizeListView.setObjectName(u"fontSizeListView")
        self.fontSizeListView.setAlternatingRowColors(True)

        self.fontSizeLayout.addWidget(self.fontSizeListView)


        self.fontOptionsLayout.addWidget(self.fontSizeGroup)


        self.verticalLayout.addLayout(self.fontOptionsLayout)

        self.fontEffectsGroup = QGroupBox(FontDialog)
        self.fontEffectsGroup.setObjectName(u"fontEffectsGroup")
        self.effectsLayout = QGridLayout(self.fontEffectsGroup)
        self.effectsLayout.setObjectName(u"effectsLayout")
        self.strikeoutCheckBox = QCheckBox(self.fontEffectsGroup)
        self.strikeoutCheckBox.setObjectName(u"strikeoutCheckBox")

        self.effectsLayout.addWidget(self.strikeoutCheckBox, 0, 0, 1, 1)

        self.underlineCheckBox = QCheckBox(self.fontEffectsGroup)
        self.underlineCheckBox.setObjectName(u"underlineCheckBox")

        self.effectsLayout.addWidget(self.underlineCheckBox, 0, 1, 1, 1)

        self.colorLabel = QLabel(self.fontEffectsGroup)
        self.colorLabel.setObjectName(u"colorLabel")

        self.effectsLayout.addWidget(self.colorLabel, 1, 0, 1, 1)

        self.colorLayout = QHBoxLayout()
        self.colorLayout.setObjectName(u"colorLayout")
        self.colorPreview = QFrame(self.fontEffectsGroup)
        self.colorPreview.setObjectName(u"colorPreview")
        self.colorPreview.setMinimumSize(QSize(30, 30))
        self.colorPreview.setMaximumSize(QSize(30, 30))
        self.colorPreview.setAutoFillBackground(False)
        self.colorPreview.setFrameShape(QFrame.Box)
        self.colorPreview.setFrameShadow(QFrame.Raised)

        self.colorLayout.addWidget(self.colorPreview)

        self.colorButton = QPushButton(self.fontEffectsGroup)
        self.colorButton.setObjectName(u"colorButton")

        self.colorLayout.addWidget(self.colorButton)

        self.colorSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.colorLayout.addItem(self.colorSpacer)


        self.effectsLayout.addLayout(self.colorLayout, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.fontEffectsGroup)

        self.previewGroup = QGroupBox(FontDialog)
        self.previewGroup.setObjectName(u"previewGroup")
        self.previewLayout = QVBoxLayout(self.previewGroup)
        self.previewLayout.setObjectName(u"previewLayout")
        self.previewTextEdit = QTextEdit(self.previewGroup)
        self.previewTextEdit.setObjectName(u"previewTextEdit")
        self.previewTextEdit.setReadOnly(True)

        self.previewLayout.addWidget(self.previewTextEdit)


        self.verticalLayout.addWidget(self.previewGroup)

        self.buttonBox = QDialogButtonBox(FontDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Apply|QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(FontDialog)
        self.buttonBox.accepted.connect(FontDialog.accept)
        self.buttonBox.rejected.connect(FontDialog.reject)

        QMetaObject.connectSlotsByName(FontDialog)
    # setupUi

    def retranslateUi(self, FontDialog):
        FontDialog.setWindowTitle(QCoreApplication.translate("FontDialog", u"Font Settings", None))
        self.fontFamilyGroup.setTitle(QCoreApplication.translate("FontDialog", u"Font Family", None))
        self.fontStyleGroup.setTitle(QCoreApplication.translate("FontDialog", u"Font Style", None))
        self.fontSizeGroup.setTitle(QCoreApplication.translate("FontDialog", u"Size", None))
        self.fontEffectsGroup.setTitle(QCoreApplication.translate("FontDialog", u"Effects", None))
        self.strikeoutCheckBox.setText(QCoreApplication.translate("FontDialog", u"Strikeout", None))
        self.underlineCheckBox.setText(QCoreApplication.translate("FontDialog", u"Underline", None))
        self.colorLabel.setText(QCoreApplication.translate("FontDialog", u"Color:", None))
        self.colorButton.setText(QCoreApplication.translate("FontDialog", u"Change Color...", None))
        self.previewGroup.setTitle(QCoreApplication.translate("FontDialog", u"Preview", None))
        self.previewTextEdit.setHtml(QCoreApplication.translate("FontDialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz 1234567890</p></body></html>", None))
    # retranslateUi

