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

        self.resize(1000, 700)  # 设置窗口的尺寸为宽度1000像素，高度700像素
        # 水平布局
        HLayout = QHBoxLayout()
        label_slider_spinbox_hlayout = QHBoxLayout()#label slider spinbox的单独水平布局
        check_box_layout = QHBoxLayout()  # 复选框单独用了一个水平布局
        # 垂直布局
        VLayout = QVBoxLayout()

        # 创建标签
        self.lab1 = QLabel()
        self.lab1.setPixmap(QPixmap("./images/python.jpg"))  # 设置标签显示的图片
        HLayout.addWidget(self.lab1)
        
        # 创建列表视图1
        self.list_view1 = QListView()
        self.list_view1.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置列表视图的右键菜单策略
        self.list_view1.customContextMenuRequested[QtCore.QPoint].connect(self.right_menu_show_list1)  # 连接列表视图1的右键菜单的槽函数

        # 创建列表视图2
        self.list_view2 = QListView()
        self.item_model = QStandardItemModel()
        self.list_view2.setModel(self.item_model)
        self.list_view2.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置列表视图的右键菜单策略
        self.list_view2.customContextMenuRequested[QtCore.QPoint].connect(self.right_menu_show_list2)  # 连接列表视图2的右键菜单的槽函数

        # 创建QSlider和QSpinBox
        self.slider = QSlider(Qt.Horizontal)  # 创建水平滚动条
        self.slider.setSingleStep(3)  # 设置步长
        self.slider.setValue(0)  # 设置滚动条默认值
        self.slider.setTickPosition(QSlider.TicksBelow)  # 设置刻度
        self.slider.setTickInterval(6)  # 设置刻度间隔
        self.slider.setMaximum(255)  # 滚动条最大值

        self.spinbox = QSpinBox()  # 创建spinbox
        self.spinbox.setMaximum(255)  # spinbox最大值
        
        self.spinbox.valueChanged['int'].connect(self.slider.setValue)  # 当SpinBox值变化时，设置滑动条的值
        self.slider.valueChanged['int'].connect(self.spinbox.setValue)  # 当滑动条的值变化时，设置SpinBox
        
        # 将QSlider和QSpinBox添加到水平布局
        label_slider_spinbox_hlayout.addWidget(QLabel("Scale"))  # 水平布局添加label
        label_slider_spinbox_hlayout.addWidget(self.slider)  # 水平布局添加slider
        label_slider_spinbox_hlayout.addWidget(self.spinbox)  # 水平布局添加spinbox

        
        # 创建按钮
        self.selectbtn = QPushButton("选择图片")
        self.btn1 = QPushButton("选择黑色背景")  # 将选择图片按钮添加到垂直布局中
        self.btn2 = QPushButton("选择白色背景")
        self.btn3 = QPushButton("选择透明背景")

        # 创建一个QGroupBox，用于包裹相关控件
        check_box = QGroupBox("是否输出背景")
        # 创建一个QCheckBox，并设置初始状态为未选中
        self.check_box = QCheckBox("&Yes")
        self.check_box.setChecked(False)
        # 将stateChanged信号连接到check_box_state槽函数，并传递self.check_box作为参数
        self.check_box.stateChanged.connect(lambda: self.check_box_state(self.check_box))


        check_box_layout.addWidget(self.check_box)
        check_box.setLayout(check_box_layout) # 将check_box_layout设置为check_box的布局

        #垂直布局添加
        VLayout.addLayout(label_slider_spinbox_hlayout)    # 将水平布局添加到垂直布局中
        VLayout.addWidget(self.selectbtn)       # 将选择图片按钮添加到垂直布局中
        VLayout.addWidget(self.list_view1)      # 将列表视图1添加到垂直布局中
        VLayout.addWidget(check_box)            # 将复选框添加到垂直布局中
        VLayout.addWidget(self.btn1)            # btn1复选框添加到垂直布局中
        VLayout.addWidget(self.btn2)            # btn2复选框添加到垂直布局中
        VLayout.addWidget(self.btn3)            # btn3复选框添加到垂直布局中
        VLayout.addWidget(self.list_view2)      # 将列表视图2添加到垂直布局中

        # 设置列表视图的右键菜单策略并连接右键菜单的槽函数
        bar = self.menuBar()  # 获取窗口的菜单栏对象

        self.list_view1.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置list_view1的上下文菜单策略为自定义，默认为默认菜单策略
        self.list_view1.customContextMenuRequested[QtCore.QPoint].connect(
            self.right_menu_show_list1)  # 连接自定义菜单请求信号与槽函数self.right_menu_show_list1

        self.status_bar = QStatusBar()  # 创建状态栏对象
        self.setStatusBar(self.status_bar)  # 将状态栏设置为窗口的状态栏
        HLayout.addLayout(VLayout)  # 将VLayout布局添加到HLayout布局中
        main_frame = QWidget()  # 创建一个QWidget作为主框架
        main_frame.setLayout(HLayout)  # 将HLayout布局设置为主框架的布局

        self.setWindowTitle("图像前景主体分割算法")
        self.selectbtn.clicked.connect(self.open_image)  # 连接选择图片按钮的槽函数
        self.list_view1.doubleClicked.connect(self.clicked_list_view1)  # 连接列表视图1双击项的槽函数
        self.list_view1.clicked.connect(self.clicked_list_view1)  # 连接列表视图1单击项的槽函数

        self.list_view2.doubleClicked.connect(self.clicked_list_view2)  # 连接列表视图2双击项的槽函数
        self.list_view2.clicked.connect(self.clicked_list_view2)  # 连接列表视图2单击项的槽函数

        self.btn1.clicked.connect(self.process_image_black)  # 连接选择黑色背景按钮的槽函数
        self.btn2.clicked.connect(self.process_image_white)  # 连接选择白色背景按钮的槽函数
        self.btn3.clicked.connect(self.process_image_none)  # 连接选择透明背景按钮的槽函数

        self.setCentralWidget(main_frame)  # 将main_frame设置为窗口的中央部件

    #列表视图1的右键菜单显示
    def right_menu_show_list1(self):
        rightMenu = QtWidgets.QMenu(self.list_view1)  # 创建右键菜单
        removeAction = QtWidgets.QAction(u"Delete", self,  # 创建一个“删除”操作，点击后调用self.remove_image方法
                                         triggered=self.remove_image)  # triggered 为右键菜单点击后的激活事件。这里slef.close调用的是系统自带的关闭事件。
        rightMenu.addAction(removeAction)  # 将“删除”操作添加到右键菜单
        rightMenu.exec_(QtGui.QCursor.pos())  # 在鼠标位置显示右键菜单


    # 列表视图2的右键菜单显示
    def right_menu_show_list2(self):
        rightMenu = QtWidgets.QMenu(self.list_view2)  # 创建右键菜单
        saveAction = QtWidgets.QAction(u"Save", self,  # 创建一个“删除”操作，点击后调用self.remove_image方法
                                       triggered=self.save_image)  # triggered 为右键菜单点击后的激活事件。这里slef.close调用的是系统自带的关闭事件。
        rightMenu.addAction(saveAction)  # 将“删除”操作添加到右键菜单
        rightMenu.exec_(QtGui.QCursor.pos())  # 在鼠标位置显示右键菜单

    def copy_files(self, img_name_list_view1, destination_path):
        # 遍历文件路径列表
        for file_path in img_name_list_view1:
            shutil.copy(file_path, destination_path)


#列表视图1的点击事件
    def clicked_list_view1(self, qModelIndex):
        global path_selected_of_list_view1                                    #存储选择的图片路径到全局变量
        self.lab1.setPixmap(QPixmap(img_name_list_view1[qModelIndex.row()]))  # 在lab1标签中显示选择的图片
        path_selected_of_list_view1 = img_name_list_view1[qModelIndex.row()]  # 将选择的图片路径存储到全局变量path_selected_of_list_view1中


    # 列表视图2的点击事件
    def clicked_list_view2(self, qModelIndex):
        # QMessageBox.information(self, "Qlist_view1", "你选择了: "+ imgName[qModelIndex.row()])
        global path_selected_of_list_view2                                    #存储选择的图片路径到全局变量
        self.lab1.setPixmap(QPixmap(img_name_list_view2[qModelIndex.row()]))  # 在lab1标签中显示选择的图片
        path_selected_of_list_view2 = img_name_list_view2[qModelIndex.row()]  # 将选择的图片路径存储到全局变量path_selected_of_list_view2中


    def open_image(self):
        global img_name_list_view1       #存储列表视图1中的图片名称
        # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        img_name_list_view1, imgType = QtWidgets.QFileDialog.getOpenFileNames(self, "多文件选择", "/",
                                                                      "所有文件 (*);;文本文件 (*.txt)")  # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        slm = QStringListModel()  # 创建一个QStringListModel对象
        slm.setStringList(img_name_list_view1)  # 将选择的文件名列表设置为QStringListModel的数据
        self.list_view1.setModel(slm)  # 在list_view1中显示选择的文件名列表

    def find_image(self):
        global img_name_list_view2      #存储列表视图2中的图片名称
        # 打开文件对话框，选择多个文件，限定文件类型为所有文件或文本文件
        folder_path = "./output/"
        img_name_list_view2 = os.listdir(folder_path)  # 读取指定路径下文件的字符串，形成list
        img_name_list_view2 = [folder_path + x for x in img_name_list_view2]  # 为每个字符串添加路径前缀

        slm1 = QStringListModel()  # 创建一个QStringListModel对象
        slm1.setStringList(img_name_list_view2)  # 将选择的文件名列表设置为QStringListModel的数据
        self.list_view2.setModel(slm1)  # 在list_view2中显示选择的文件名列表

    def remove_image(self):
        selected = self.list_view1.selectedIndexes()  # 获取用户选择的列表项索引
        itemmodel = self.list_view1.model()  # 获取list_view1的模型对象
        for i in selected:
            itemmodel.removeRow(i.row())  # 移除选中的行

    def save_image(self):
        # 弹出文件对话框，获取用户选择的目录路径
        save_directory = QFileDialog.getExistingDirectory(self, "选择保存路径", os.path.expanduser("~"))
        shutil.copy(path_selected_of_list_view2, save_directory)#列表视图2中选中的路径复制到save_directory

    def set_json(self, scale, color, back):
        with open("./data.json", 'r', encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
        load_dict['scale'] = scale
        load_dict['color'] = color
        load_dict['back'] = back
        with open("./data.json", 'w', encoding='utf-8') as f:
            json.dump(load_dict, f, ensure_ascii=False)

    def check_box_state(self, btn):
        # 判断复选框的状态
        back = self.check_box.isChecked()
        # 根据复选框的状态，显示相应的提示信息框
        if back:
            QMessageBox.information(self, "提示", "输出背景", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        else:
            QMessageBox.information(self, "提示", "输出主体")

    def process_image_black(self):
        os.system('python ./initial.py')
        self.copy_files(img_name_list_view1, destination_path)  # 从用户指定路径复制到destination_path路径
        self.set_json(self.spinbox.value(), 'black', str(self.check_box.isChecked()).lower())  # 修改json
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.find_image()  # 调用find_image(self)函数,显示输出图片
        QMessageBox.information(self, "Tips", "Done!")  # 显示一个消息框，内容为"完成！

    def process_image_white(self):
        os.system('python ./initial.py')
        self.copy_files(img_name_list_view1, destination_path)
        self.set_json(self.spinbox.value(), 'white', str(self.check_box.isChecked()).lower())
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.find_image()
        QMessageBox.information(self, "Tips", "Done!")

    def process_image_none(self):
        os.system('python ./initial.py')
        self.copy_files(img_name_list_view1, destination_path)
        self.set_json(self.spinbox.value(), 'none', str(self.check_box.isChecked()).lower())
        os.system('python ./test.py')
        os.system('python ./mask.py')
        os.system('python ./output.py')
        self.find_image()
        QMessageBox.information(self, "Tips", "Done!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ListViewDemo()  # 创建ListViewDemo类的实例
    win.show()  # 显示窗口
    sys.exit(app.exec_())  # 运行应用程序，直到窗口被关闭

