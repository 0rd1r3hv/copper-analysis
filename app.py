import sys
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QTimer,
)
from sage.all import *
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from ui import MainWinIniter
from qt_material import apply_stylesheet
from src.cfg import Cfg
from src.ernst05 import mixed_1, mixed_2


class MainWin(QMainWindow):
    def __init__(self, cfg: Cfg):
        super().__init__()
        self.cfg = cfg
        self.ui = MainWinIniter()
        self.ui.setup_ui(self)

        self._init_ui()
        self.cnct_sgl()

    def _init_ui(self):
        self.setup_anime()
        self.chg_th(self.cfg.dflt_th_xml)

    def setup_anime(self):
        self.sidebar_anime_grp = QParallelAnimationGroup()
        self._create_sidebar_animes()
        self.sidebar_anime_grp.addAnimation(self.min_anime)
        self.sidebar_anime_grp.addAnimation(self.max_anime)

    def _create_sidebar_animes(self):
        self.min_anime = self._create_anime(b"minimumWidth")
        self.max_anime = self._create_anime(b"maximumWidth")

    def _create_anime(self, property_name):
        anime = QPropertyAnimation(self.ui.sidebar_frm, property_name)
        anime.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anime.setDuration(self.cfg.anime_dur)
        return anime

    def cnct_sgl(self):
        self.ui.pnl_btn.toggled["bool"].connect(self.tgl_pnl)
        self._cnct_page_btn()
        self._cnct_atk_btn()
        self.ui.主题_cb.currentTextChanged.connect(self.chg_th)

    def _cnct_atk_btn(self):
        self.ui.atk_btn.clicked.connect(self._exec_atk)

    def _exec_atk(self):
        攻击方法序列 = self.ui.atk_cb.currentIndex()
        攻击函数 = [
            self._attack_function_1,
            self._attack_function_2,
            self.ernst05,
        ]

        if 0 <= 攻击方法序列 < len(攻击函数):
            攻击函数[攻击方法序列]()
        else:
            print("无效的攻击选项")

    def _attack_function_1(self):
        print("执行攻击函数1")

    def _attack_function_2(self):
        print("执行攻击函数2")

    def ernst05(self):
        mixed_1(
            Integer(self.ui.N_le.text()),
            Integer(self.ui.e_le.text()),
            (Integer(self.ui.d_msb_le.text()), Integer(self.ui.d_lsb_le.text())),
            (
                Integer(self.ui.d_len_le.text()),
                Integer(self.ui.msb_len_le.text()),
                Integer(self.ui.lsb_len_le.text()),
            ),
        )

    def _cnct_page_btn(self):
        btn_list = [
            (self.ui.home_btn, 0),
            (self.ui.rsa_btn, 1),
            (self.ui.crt_rsa_btn, 2),
            (self.ui.usr_btn, 3),
            (self.ui.stg_btn, 4),
            (self.ui.about_btn, 5),
        ]
        for btn, idx in btn_list:
            btn.clicked.connect(
                lambda _, idx=idx: self.ui.page_stk.setCurrentIndex(idx)
            )

    def chg_th(self, th):
        apply_stylesheet(self, theme=th)

    def tgl_pnl(self, ext):
        self._anime_sidebar(ext)
        self._tgl_pnl_btn_icon(ext)

    def _anime_sidebar(self, ext):
        start_w = self.ui.sidebar_frm.width()
        end_w = 196 if ext else 52

        self._set_anime_values(self.min_anime, start_w, end_w)
        self._set_anime_values(self.max_anime, start_w, end_w)

        self.sidebar_anime_grp.start()
        QTimer.singleShot(self.cfg.vis_dly, lambda: self._tgl_lbl_vis(ext))

    def _set_anime_values(self, anime, start, end):
        anime.setStartValue(start)
        anime.setEndValue(end)

    def _tgl_pnl_btn_icon(self, ext):
        icon_name = "收起面板.png" if ext else "展开面板.png"
        self.ui.pnl_btn.setIcon(QIcon(f"{self.cfg.icon_dir}/{icon_name}"))

    def _tgl_lbl_vis(self, ext):
        for r in range(self.ui.sidebar_glo.rowCount()):
            item = self.ui.sidebar_glo.itemAtPosition(r, 1)
            if isinstance(item.widget(), QLabel):
                item.widget().setVisible(ext)


if __name__ == "__main__":
    cfg = Cfg(
        [{"name": "主页", "icon": "主页.png"}, {"name": "RSA", "icon": "RSA.png"}]
    )
    app = QApplication(sys.argv)
    win = MainWin(cfg)
    win.show()
    sys.exit(app.exec())
