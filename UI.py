import sys
from functools import partial

from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, \
    QLineEdit, QTableView, QGridLayout, QDateEdit, QMessageBox, QDialog, QDialogButtonBox, QDateTimeEdit
from PyQt5.QtCore import Qt, QRegularExpression, QDate, QTimer, QDateTime
import pymysql
import pandas as pd
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_floor = None
        self.timer = None
        self.input_boxes_value = None
        self.refresh()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.floor_layout = QVBoxLayout()
        main_layout.addLayout(self.floor_layout)

        self.rooms_layout = QGridLayout()
        main_layout.addLayout(self.rooms_layout)
        self.check_in_layout = QVBoxLayout()
        main_layout.addLayout(self.check_in_layout)

        self.get_data()
        self.floor_layout_design()
        self.check_in_design()

    def refresh(self):
        def update_time():
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")  # 获取当前时间
            self.setWindowTitle(f"名宿前台 {current_time}")  # 更新窗口标题显示当前时间
            self.rooms_layout_design(self.current_floor)

        self.timer = QTimer(self)
        self.timer.timeout.connect(update_time)  # 每次定时器触发时调用 update_time 方法
        self.timer.start(1000)

    def data2sql(self, room, flag, data=None):
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='12345678', db=f'前台数据')
        cursor = conn.cursor()
        if flag == 1:  # 入住
            # print(self.rooms_info[self.rooms_info['room_number'] == room['room_number']])
            guest_details = [i.text() for i in self.input_boxes_value]
            new_status = 'occupation' if room['status'] != 'occupation' else 'unoccupied'
            cursor.execute(
                "UPDATE rooms SET status = %s, name=%s,phone=%s,checkin=%s,checkout=%s WHERE room_number = %s",
                (new_status, guest_details[0], guest_details[1], guest_details[2], guest_details[3],
                 room['room_number'])
            )

        elif flag == 2:  # 退房
            new_status = 'occupation' if room['status'] != 'occupation' else 'unoccupied'
            cursor.execute(
                "UPDATE rooms SET status = %s, name=%s,phone=%s,checkin=%s,checkout=%s WHERE room_number = %s",
                (new_status, None, None, None, None,
                 room['room_number'])
            )
        elif flag == 3:
            cursor.execute(
                "UPDATE rooms SET  checkout=%s WHERE room_number = %s",
                (data,
                 room['room_number'])
            )
        conn.commit()
        cursor.close()
        conn.close()
        self.get_data()
        self.rooms_layout_design(room['floor_number'])

    def get_data(self):
        conn = pymysql.connect(host='localhost', port=3306, user='root', password='12345678', db=f'前台数据')
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"select * from rooms")
        self.rooms_info = pd.DataFrame(cursor.fetchall())
        cursor.close()
        conn.close()

    def floor_layout_design(self):
        for f in self.rooms_info.iloc[:, 1].unique():
            button_show_data = QPushButton(f'F {f}')
            button_show_data.setFixedSize(150, 50)  # 设置按钮的固定大小
            button_show_data.clicked.connect(lambda checked, floor=f: self.rooms_layout_design(floor))
            self.floor_layout.addWidget(button_show_data)

    def clear_layout(self, layout):
        """
        清空布局中所有控件和子布局
        """
        while layout.count():
            item = layout.takeAt(0)  # 移除第一个布局项
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()  # 删除当前控件
                else:
                    sublayout = item.layout()  # 获取子布局
                    if sublayout is not None:
                        self.clear_layout(sublayout)  # 递归清理子布局

    def rooms_layout_design(self, floor):
        self.clear_layout(self.rooms_layout)
        self.current_floor = floor
        current_floor_rooms = self.rooms_info[self.rooms_info['floor_number'] == floor]
        row, col = 0, 0

        for _, room in current_floor_rooms.iterrows():
            if col == 3:  # 每层最多3个房间，换行
                col = 0
                row += 1

            # 创建房间按钮和房间信息标签的布局
            room_layout = QVBoxLayout()

            # 创建房间按钮
            room_button = QPushButton(f"{room['room_number']}", self)
            room_button.setFixedSize(120, 60)

            room_button.clicked.connect(partial(self.Check_in_out_relet, room))
            if room['status'] == 'occupation':

                current_date = QDateTime.currentDateTime()
                checkout_date = QDateTime(room['checkout'].year, room['checkout'].month, room['checkout'].day,room['checkout'].hour,room['checkout'].minute)
                if checkout_date < current_date:
                    room_button.setStyleSheet("background-color: red; color: white;")
                else:
                    room_button.setStyleSheet("background-color: blue; color: white;")
            else:
                room_button.setStyleSheet("background-color: green; color: white;")
            # 创建房间信息标签，显示电费和水费
            if room['status'] == 'unoccupied':
                room_info_label = QLabel(f'''水费: {room['water_fee']}￥  电费: {room['electricity_fee']} 
                                             ''', self)
            else:
                room_info_label = QLabel(f'''水费: {room['water_fee']}￥  电费: {room['electricity_fee']} 
预计离开日期: {room['checkout']}''', self)
            room_info_label.setAlignment(Qt.AlignCenter)

            # 将按钮和信息标签添加到房间布局中
            room_layout.addWidget(room_button)
            room_layout.addWidget(room_info_label)

            self.rooms_layout.addLayout(room_layout, row, col)
            col += 1

    def Check_in_out_relet(self, room):
        # 获取当前房间状态
        current_status = room['status']
        if current_status == 'unoccupied':
            word = '办理入住？'
        else:
            word = '办理退房？'
        room_name = room['room_number']
        # 弹出对话框，询问是否入住或退房

        if current_status == 'unoccupied':
            reply = QMessageBox.question(self, f'{room_name} - {word}',
                                         f'{word}?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                if current_status == 'unoccupied':
                    def validate_phone_number(phone_number):
                        """验证电话号码是否为11位数字"""
                        if len(phone_number) == 11 and phone_number.isdigit():
                            return True
                        else:
                            QMessageBox.warning(self, "无效的电话号码", "请输入有效的11位电话号码！")
                            return False

                    guest_details = [i.text() for i in self.input_boxes_value]
                    phone_number = guest_details[1]  # 假设电话号码在第二个输入框
                    if validate_phone_number(phone_number):
                        self.data2sql(room, 1)
                        QMessageBox.information(self, f'{room_name} 成功入住', '房间已成功入住', QMessageBox.Ok)

        else:

            # 创建一个QMessageBox
            reply = QMessageBox(self)
            reply.setIcon(QMessageBox.Question)
            reply.setWindowTitle(f'{room_name} - 退房还是续租')  # 设置标题
            reply.setText('退房还是续租？')  # 设置问题文本
            # 创建自定义按钮
            button1 = reply.addButton('退房', QMessageBox.YesRole)
            button2 = reply.addButton('续租', QMessageBox.NoRole)

            # 显示对话框
            reply.exec_()


            if reply.clickedButton() == button1:
                # 退房操作
                self.data2sql(room, 2)  # 传入房间和状态进行更新
                QMessageBox.information(self, f'{room_name} 成功退房', '房间已成功退房', QMessageBox.Ok)
            elif reply.clickedButton() == button2:
                # 续租操作
                def relet_room(room):
                    # 创建自定义日期选择对话框
                    dialog = QDialog(self)
                    dialog.setWindowTitle('选择续租日期')

                    # 创建日期选择控件
                    date_edit = QDateTimeEdit(dialog)
                    date_edit.setDisplayFormat("yyyy-MM-dd HH:mm")  # 设置日期格式
                    date_edit.setDate(QDate.currentDate())  # 默认日期为当前日期
                    date_edit.setMinimumDate(QDate.currentDate())  # 最早选择当前日期
                    date_edit.setCalendarPopup(True)  # 弹出日历选择

                    # 创建按钮
                    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal,
                                                  dialog)

                    # 设置布局
                    layout = QVBoxLayout(dialog)
                    layout.addWidget(date_edit)
                    layout.addWidget(button_box)

                    # 连接按钮事件
                    button_box.accepted.connect(dialog.accept)
                    button_box.rejected.connect(dialog.reject)

                    # 弹出对话框并等待用户选择
                    if dialog.exec_() == QDialog.Accepted:
                        # 获取用户选择的日期

                        new_checkout_date = date_edit.dateTime().toString("yyyy-MM-dd HH:mm")
                        self.data2sql(room, 3, new_checkout_date)  # 传入房间和新日期进行续租
                        QMessageBox.information(self, f'{room["room_number"]} 续租成功',
                                                f'房间已续租至 {new_checkout_date}', QMessageBox.Ok)

                relet_room(room)

    def check_in_design(self):
        # 输入框列表
        self.input_boxes_value = []

        # 姓名输入框
        name_box = QLineEdit(self)
        name_box.setPlaceholderText('姓名')
        name_box.setValidator(QRegularExpressionValidator(QRegularExpression("^[A-Za-z\u4e00-\u9fa5]+$")))  # 允许中文和字母
        name_box.setFixedSize(150, 20)
        self.input_boxes_value.append(name_box)

        # 创建姓名布局
        name_layout = QHBoxLayout()
        name_info_label = QLabel('姓名')
        name_info_label.setAlignment(Qt.AlignCenter)
        name_layout.addWidget(name_info_label)
        name_layout.addWidget(name_box)
        self.check_in_layout.addLayout(name_layout)

        # 电话输入框
        phone_box = QLineEdit(self)
        phone_box.setPlaceholderText('电话')
        phone_box.setValidator(QRegularExpressionValidator(QRegularExpression("^\d{11}$")))

        phone_box.setFixedSize(150, 20)
        self.input_boxes_value.append(phone_box)

        # 创建电话布局
        photo_layout = QHBoxLayout()
        photo_info_label = QLabel('电话')
        photo_info_label.setAlignment(Qt.AlignCenter)
        photo_layout.addWidget(photo_info_label)
        photo_layout.addWidget(phone_box)
        self.check_in_layout.addLayout(photo_layout)

        # 创建入住日期输入框
        dialog = QDialog(self)
        check_in_box = QDateTimeEdit(dialog)
        check_in_box.setDisplayFormat("yyyy-MM-dd HH:mm")  # 设置日期格式
        check_in_box.setDate(QDate.currentDate())  # 默认日期为当前日期
        check_in_box.setMinimumDate(QDate.currentDate())  # 最早选择当前日期
        check_in_box.setCalendarPopup(True)  # 弹出日历选择
        check_in_box.setFixedSize(150, 20)
        self.input_boxes_value.append(check_in_box)

        # 创建入住日期布局
        check_in_layout = QHBoxLayout()
        check_in_info_label = QLabel('入住日期')
        check_in_info_label.setAlignment(Qt.AlignCenter)
        check_in_layout.addWidget(check_in_info_label)
        check_in_layout.addWidget(check_in_box)
        self.check_in_layout.addLayout(check_in_layout)

        # 创建预计离开日期输入框
        dialog = QDialog(self)
        check_out_box = QDateTimeEdit(dialog)
        check_out_box.setDisplayFormat("yyyy-MM-dd HH:mm")  # 设置日期格式
        check_out_box.setDate(QDate.currentDate())  # 默认日期为当前日期
        check_out_box.setMinimumDate(QDate.currentDate())  # 最早选择当前日期
        check_out_box.setCalendarPopup(True)  # 弹出日历选择
        check_out_box.setFixedSize(150, 20)
        self.input_boxes_value.append(check_out_box)

        # 创建预计离开日期布局
        check_out_layout = QHBoxLayout()
        check_out_info_label = QLabel('预计离开日期')
        check_out_info_label.setAlignment(Qt.AlignCenter)
        check_out_layout.addWidget(check_out_info_label)
        check_out_layout.addWidget(check_out_box)
        self.check_in_layout.addLayout(check_out_layout)

        # 将所有输入框添加到列表
        self.input_boxes_value = [name_box, phone_box, check_in_box, check_out_box]


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
