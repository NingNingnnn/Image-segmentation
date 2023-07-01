# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import shutil
import os
import json
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel

destination_path = "./input"  # 替换为目标文件所在的目录路径


class ListViewDemo(QMainWindow):
    def __init__(self, parent=None):
        super(ListViewDemo, self).__init__(parent)  # 调用父类的构造函数进行初始化
        #  self.imgName = []# 创建一个空的列表imgName，用于存储图片名称
        # self.imgName2 = []# 创建一个空的列表imgName2，用于读取指定路径图片名称

        self.resize(1000, 700)  # 设置窗口的尺寸为宽度1000像素，高度700像素
        # 水平布局
        HLayout = QHBoxLayout()
        horizontal_layout = QHBoxLayout()
        # 垂直布局
        VLayout = QVBoxLayout()

        # 创建标签
        self.lab1 = QLabel()
        self.lab1.setPixmap(QPixmap("./images/python.jpg"))  # 设置标签显示的图片
        HLayout.addWidget(self.lab1)
        # 创建列表视图1

        self.listView1 = QListView()
        self.listView1.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置列表视图的右键菜单策略
        self.listView1.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow)  # 连接右键菜单的槽函数

        # 创建列表视图2
        self.listView2 = QListView()
        self.item_model = QStandardItemModel()
        self.listView2.setModel(self.item_model)
        self.listView2.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置列表视图的右键菜单策略
        self.listView2.customContextMenuRequested[QtCore.QPoint].connect(self.rightMenuShow2)  # 连接右键菜单的槽函数

        # 创建QSlider和QSpinBox
        self.slider = QSlider(Qt.Horizontal)  # 创建水平滚动条
        self.slider.setSingleStep(3)  # 设置步长
        self.slider.setValue(0)  # 设置滚动条默认值
        self.slider.setTickPosition(QSlider.TicksBelow)  # 设置刻度
        self.slider.setTickInterval(6)  # 设置刻度间隔
        self.slider.setMaximum(255)  # 滚动条最大值

        self.spinbox = QSpinBox()  # 创建spinbox
        self.spinbox.setMaximum(255)  # spinbox最大值
        # 将QSlider和QSpinBox添加到水平布局

        horizontal_layout.addWidget(QLabel("Scale"))  # 水平布局添加label
        horizontal_layout.addWidget(self.slider)  # 水平布局添加slider
        horizontal_layout.addWidget(self.spinbox)  # 水平布局添加spinbox

        self.spinbox.valueChanged['int'].connect(self.slider.setValue)  # 当SpinBox值变化时，设置滑动条的值
        self.slider.valueChanged['int'].connect(self.spinbox.setValue)  # 当滑动条的值变化时，设置SpinBox的
        # 创建按钮

        self.selectbtn = QPushButton("选择图片")
        self.btnOK1 = QPushButton("选择黑色背景")  # 将选择图片按钮添加到垂直布局中
        self.btnOK2 = QPushButton("选择白色背景")
        self.btnOK3 = QPushButton("选择透明背景")

        groupBox = QGroupBox("是否输出背景")
        self.checkBox1 = QCheckBox("&Yes")
        self.checkBox1.setChecked(False)
        self.checkBox1.stateChanged.connect(lambda: self.btnstate(self.checkBox1))

        layout = QHBoxLayout()  # 复选框单独用了一个水平布局
        layout.addWidget(self.checkBox1)
        groupBox.setLayout(layout)

        VLayout.addLayout(horizontal_layout)  # 将水平布局添加到垂直布局中
        VLayout.addWidget(self.selectbtn)  # 将选择图片按钮添加到垂直布局中
        VLayout.addWidget(self.listView1)  # 将选择图片按钮添加到垂直布局中
        VLayout.addWidget(groupBox)
        VLayout.addWidget(self.btnOK1)
        VLayout.addWidget(self.btnOK2)
        VLayout.addWidget(self.btnOK3)

        VLayout.addWidget(self.listView2)  # 将选择图片按钮添加到垂直布局中

        # 设置列表视图的右键菜单策略并连接右键菜单的槽函数
        bar = self.menuBar()  # 获取窗口的菜单栏对象

        self.listView1.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置listView1的上下文菜单策略为自定义，默认为默认菜单策略
        self.listView1.customContextMenuRequested[QtCore.QPoint].connect(
            self.rightMenuShow)  # 连接自定义菜单请求信号与槽函数self.rightMenuShow

        self.statusBar = QStatusBar()  # 创建状态栏对象
        self.setStatusBar(self.statusBar)  # 将状态栏设置为窗口的状态栏
        HLayout.addLayout(VLayout)  # 将VLayout布局添加到HLayout布局中
        main_frame = QWidget()  # 创建一个QWidget作为主框架
        main_frame.setLayout(HLayout)  # 将HLayout布局设置为主框架的布局

        self.setWindowTitle("图像前景主体分割算法")
        self.selectbtn.clicked.connect(self.openimage)  # 连接选择图片按钮的槽函数
        self.listView1.doubleClicked.connect(self.clicked)  # 连接列表视图双击项的槽函数
        self.listView1.clicked.connect(self.clicked)  # 连接列表视图单击项的槽函数

        self.listView2.doubleClicked.connect(self.clicked2)  # 连接列表视图双击项的槽函数
        self.listView2.clicked.connect(self.clicked2)  # 连接列表视图单击项的槽函数

        self.btnOK1.clicked.connect(self.processimage1)  # 连接选择黑色背景按钮的槽函数
        self.btnOK2.clicked.connect(self.processimage2)  # 连接选择白色背景按钮的槽函数
        self.btnOK3.clicked.connect(self.processimage3)  # 连接选择透明背景按钮的槽函数

        self.setCentralWidget(main_frame)  # 将main_frame设置为窗口的中央部件

    def rightMenuShow(self):
        rightMenu = QtWidgets.QMenu(self.listView1)  # 创建右键菜单
        removeAction = QtWidgets.QAction(u"Delete", self,  # 创建一个“删除”操作，点击后调用self.removeimage方法
                                         triggered=self.removeimage)  # triggered 为右键菜单点击后的激活事件。这里slef.close调用的是系统自带的关闭事件。
        rightMenu.addAction(removeAction)  # 将“删除”操作添加到右键菜单
        rightMenu.exec_(QtGui.QCursor.pos())  # 在鼠标位置显示右键菜单

    def rightMenuShow2(self):
        rightMenu = QtWidgets.QMenu(self.listView2)  # 创建右键菜单
        saveAction = QtWidgets.QAction(u"Save", self,  # 创建一个“删除”操作，点击后调用self.removeimage方法
                                       triggered=self.saveimage)  # triggered 为右键菜单点击后的激活事件。这里slef.close调用的是系统自带的关闭事件。
        rightMenu.addAction(saveAction)  # 将“删除”操作添加到右键菜单
        rightMenu.exec_(QtGui.QCursor.pos())  # 在鼠标位置显示右键菜单

    def processTrigger(self, q):
        if (q.text() == "show"):
            self.statusBar.showMessage(q.text() + " 菜单选项被点击了", 5000)  # 在状态栏中显示“show 菜单选项被点击了”，持续显示5秒

    def copy_files(self, imgNameList, destination_path):
        # 遍历文件路径列表
        for file_path in imgNameList:
            shutil.copy(file_path, destination_path)
        #     print(f"已复制文件: {file_path} -> {destination_path}")
        #
        # print("所有文件复制完成！")

    def clicked(self, qModelIndex):
        # QMessageBox.information(self, "QListView1", "你选择了: "+ imgName[qModelIndex.row()])
        global path
        self.lab1.setPixmap(QPixmap(imgNameList[qModelIndex.row()]))  # 在lab1标签中显示选择的图片
        path = imgNameList[qModelIndex.row()]  # 将选择的图片路径存储到全局变量path中
        print(path)

    def clicked2(self, qModelIndex):
        # QMessageBox.information(self, "QListView1", "你选择了: "+ imgName[qModelIndex.row()])
        global path2
        self.lab1.setPixmap(QPixmap(imgName2[qModelIndex.row()]))  # 在lab1标签中显示选择的图片
        path2 = imgName2[qModelIndex.row()]  # 将选择的图片路径存储到全局变量path中

    def findimage(self):
        global imgName2
        # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        folder_path = "./output/"
        imgName2 = os.listdir(folder_path)  # 读取指定路径下文件的字符串，形成list
        imgName2 = [folder_path + x for x in imgName2]  # 为每个字符串添加路径前缀

        slm1 = QStringListModel()  # 创建一个QStringListModel对象
        slm1.setStringList(imgName2)  # 将选择的文件名列表设置为QStringListModel的数据
        self.listView2.setModel(slm1)  # 在listView2中显示选择的文件名列表

    def openimage(self):
        global imgNameList
        # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        imgNameList, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/",
                                                                      "所有文件 (*);;文本文件 (*.txt)")  # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        slm = QStringListModel()  # 创建一个QStringListModel对象
        slm.setStringList(imgNameList)  # 将选择的文件名列表设置为QStringListModel的数据
        self.listView1.setModel(slm)  # 在listView1中显示选择的文件名列表

    def removeimage(self):
        selected = self.listView1.selectedIndexes()  # 获取用户选择的列表项索引
        itemmodel = self.listView1.model()  # 获取listView1的模型对象
        for i in selected:
            itemmodel.removeRow(i.row())  # 移除选中的行

    def saveimage(self):
        selected_indexes = self.listView2.selectedIndexes()  # 获取用户选择的列表项索引
        item_model = self.listView2.model()  # 获取listView2的模型对象
        print(selected_indexes)
        # 弹出文件对话框，获取用户选择的目录路径
        save_directory = QFileDialog.getExistingDirectory(self, "选择保存路径", os.path.expanduser("~"))

        shutil.copy(path2, save_directory)

    def getjson(self, scale, color, back):
        with open("./data.json", 'r', encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
        print(type(load_dict))
        print(load_dict)

        load_dict['scale'] = scale
        load_dict['color'] = color
        load_dict['back'] = back
        with open("./data.json", 'w', encoding='utf-8') as f:
            json.dump(load_dict, f, ensure_ascii=False)

        print(type(load_dict))
        print(load_dict)

    def btnstate(self, btn):
        back = self.checkBox1.isChecked()
        print(back)
        if back:
            QMessageBox.information(self, "Tips", "输出背景", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.information(self, "Tips", "输出主体")

    def processimage1(self):
        os.system('python ./initial.py')
        self.copy_files(imgNameList, destination_path)  # 从用户指定路径复制到destination_path路径
        self.getjson(self.spinbox.value(), 'black', str(self.checkBox1.isChecked()).lower())  # 修改json
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.findimage()  # 调用findimage(self)函数
        QMessageBox.information(self, "Tips", "Done!")  # 显示一个消息框，内容为"完成！

    def processimage2(self):
        os.system('python ./initial.py')
        self.copy_files(imgNameList, destination_path)
        self.getjson(self.spinbox.value(), 'white', str(self.checkBox1.isChecked()).lower())
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.findimage()  # 调用findimage(self)函数

        QMessageBox.information(self, "Tips", "Done!")

    def processimage3(self):
        os.system('python ./initial.py')
        self.copy_files(imgNameList, destination_path)
        self.getjson(self.spinbox.value(), 'none', str(self.checkBox1.isChecked()).lower())
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.findimage()  # 调用findimage(self)函数
        QMessageBox.information(self, "Tips", "Done!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ListViewDemo()  # 创建ListViewDemo类的实例
    win.show()  # 显示窗口
    sys.exit(app.exec_())  # 运行应用程序，直到窗口被关闭

