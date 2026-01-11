import os

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QListWidget, QListWidgetItem,
    QHBoxLayout
)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import Qt, QUrl



class ShortcutDialog:
    def __init__(self, parent):
        self.parent = parent
        self.shortcuts_file = "data/shortcuts.txt"

    def load_shortcuts(self):
        if not os.path.exists(self.shortcuts_file):
            return []
        try:
            with open(self.shortcuts_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                shortcuts = []
                for line in lines:
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        path, category, alias = parts
                        shortcuts.append((path, category, alias))
                return shortcuts
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"读取快捷入口失败：{e}")
            return []

    def save_shortcuts(self, shortcuts):
        try:
            with open(self.shortcuts_file, "w", encoding="utf-8") as f:
                for path, category, alias in shortcuts:
                    f.write(f"{path}|{category}|{alias}\n")
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"保存快捷入口失败：{e}")

    def add_shortcut(self):

        dialog = QDialog(self.parent)
        dialog.setWindowTitle("添加快捷入口")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.resize(500, 280)
        dialog.setMinimumSize(400, 220)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 8, 15, 15)
        layout.setSpacing(12)

        # 路径
        label_path = QLabel("请输入本地路径或网址：")
        line_edit_path = QLineEdit()
        line_edit_path.setPlaceholderText("例如：C:\\Projects 或 https://github.com")
        layout.addWidget(label_path)
        layout.addWidget(line_edit_path)

        # 分类
        label_category = QLabel("请选择或输入分类：")
        combo_box_category = QComboBox()
        existing_shortcuts = self.load_shortcuts()
        used_categories = sorted(set(cat for _, cat, _ in existing_shortcuts))
        if not used_categories:
            used_categories = []
        combo_box_category.addItems(used_categories)
        combo_box_category.setEditable(True)
        combo_box_category.setInsertPolicy(QComboBox.InsertAtTop)
        layout.addWidget(label_category)
        layout.addWidget(combo_box_category)

        # 别称
        label_alias = QLabel("重命名（可选）：")
        line_edit_alias = QLineEdit()
        line_edit_alias.setPlaceholderText("")
        layout.addWidget(label_alias)
        layout.addWidget(line_edit_alias)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(ok_button)
        btn_layout.addWidget(cancel_button)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        dialog.setLayout(layout)


        def handle_ok():
            path = line_edit_path.text().strip()
            if not path:
                QMessageBox.warning(self.parent, "警告", "请输入有效路径或网址！")
                return
            category = combo_box_category.currentText().strip() or "未分类"
            alias = line_edit_alias.text().strip() or path

            shortcuts = self.load_shortcuts()
            # 允许同路径不同分类，但禁止同路径+同分类重复
            if any(p == path and c == category for p, c, _ in shortcuts):
                QMessageBox.information(self.parent, "提示", f"该路径已在【{category}】分类中存在。")
                return

            shortcuts.append((path, category, alias))
            self.save_shortcuts(shortcuts)
            dialog.accept()

        ok_button.clicked.connect(handle_ok)
        cancel_button.clicked.connect(dialog.reject)

        layout.addWidget(label_path)
        layout.addWidget(line_edit_path)
        layout.addWidget(label_category)
        layout.addWidget(combo_box_category)
        layout.addWidget(label_alias)
        layout.addWidget(line_edit_alias)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        dialog.setLayout(layout)


        dialog.exec_()

    def open_shortcut(self, url_or_path):
        try:
            if url_or_path.startswith(("http://", "https://")):
                QDesktopServices.openUrl(QUrl(url_or_path))
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(url_or_path))
        except Exception as e:
            QMessageBox.critical(self.parent, "错误", f"无法打开：{e}")

    def manage_shortcuts(self):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("管理快捷入口")
        dialog.resize(650, 400)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        shortcuts = self.load_shortcuts()
        for path, category, alias in shortcuts:
            item = QListWidgetItem(f"[{category}] {alias} → {path}")
            item.setData(Qt.UserRole, (path, category, alias))
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        # 按钮
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("删除选中")
        close_btn = QPushButton("关闭")

        def delete_selected():
            current = list_widget.currentItem()
            if not current:
                QMessageBox.warning(self.parent, "提示", "请先选择一个快捷入口。")
                return
            path, category, alias = current.data(Qt.UserRole)
            reply = QMessageBox.question(
                self.parent, "确认删除",
                f"确定要删除以下快捷入口吗？\n\n分类：{category}\n名称：{alias}\n路径：{path}",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                all_shortcuts = self.load_shortcuts()
                # 精确匹配 (path, category)
                new_shortcuts = [
                    s for s in all_shortcuts
                    if not (s[0] == path and s[1] == category)
                ]
                self.save_shortcuts(new_shortcuts)
                row = list_widget.row(current)
                list_widget.takeItem(row)
                QMessageBox.information(self.parent, "成功", "快捷入口已删除。")

        delete_btn.clicked.connect(delete_selected)
        close_btn.clicked.connect(dialog.accept)

        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()