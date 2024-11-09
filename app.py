import sys
import io
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QTimer,
)
from sage.all import Integer
from PySide6.QtGui import QIcon, QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
import src.tlp17
from ui import 主窗UI
from qt_material import apply_stylesheet
from src.cfg import 配置
from src import ernst05
from src import mns21
from src import tk14
import src.mns22
from src.mn23 import automated


class 主窗(QMainWindow):
    def __init__(self, cfg: 配置):
        super().__init__()
        self.cfg = cfg
        self.ui = 主窗UI()
        self.ui.初始化(self, cfg)
        self.setStyleSheet("font-size: 14pt;")

        self.tx_redirector = te_stdout重定向(self.ui.rsa_te)
        self.crt_tx_redirector = te_stdout重定向(self.ui.crt_te)
        self.var_tx_redirector = te_stdout重定向(self.ui.var_te)
        self.auto_tx_redirector = te_stdout重定向(self.ui.auto_te)

        self._init_ui()
        self.连信()

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

    def 连信(self):
        self.ui.pnl_btn.toggled["bool"].connect(self.tgl_pnl)
        self.换页()
        self.连rsa_btn()
        self.连crt_btn()
        self.连var_btn()
        self.连auto_btn()
        self.连rsa_atk_btn()
        self.连crt_atk_btn()
        self.连var_atk_btn()
        self.连auto_atk_btn()
        self.ui.主题_cb.currentTextChanged.connect(self.chg_th)

    def 连rsa_btn(self):
        self.ui.rsa_btn.clicked.connect(self.tx_redirector.redirect_stdout)

    def 连crt_btn(self):
        self.ui.crt_btn.clicked.connect(self.crt_tx_redirector.redirect_stdout)

    def 连var_btn(self):
        self.ui.var_btn.clicked.connect(self.var_tx_redirector.redirect_stdout)

    def 连auto_btn(self):
        self.ui.auto_btn.clicked.connect(self.auto_tx_redirector.redirect_stdout)

    def 连rsa_atk_btn(self):
        def rsa攻击():
            def tk14msb():
                rst = tk14.msb_1(
                    Integer(self.ui.N_le.text()),
                    Integer(self.ui.e_le.text()),
                    (Integer(self.ui.d_msb_le.text()),),
                    (
                        Integer(self.ui.d_len_le.text()),
                        Integer(self.ui.msb_len_le.text()),
                    ),
                    (None,),
                )

                print(
                    f"""攻击成功！私钥 d =
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def tk14lsb():
                rst = tk14.lsb(
                    Integer(self.ui.N_le.text()),
                    Integer(self.ui.e_le.text()),
                    (Integer(self.ui.d_lsb_le.text()),),
                    (
                        Integer(self.ui.d_len_le.text()),
                        Integer(self.ui.lsb_len_le.text()),
                    ),
                    (None,),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def tk14mixed():
                rst = tk14.mixed(
                    Integer(self.ui.N_le.text()),
                    Integer(self.ui.e_le.text()),
                    (
                        Integer(self.ui.d_msb_le.text()),
                        Integer(self.ui.d_lsb_le.text()),
                    ),
                    (
                        Integer(self.ui.d_len_le.text()),
                        Integer(self.ui.msb_len_le.text()),
                        Integer(self.ui.lsb_len_le.text()),
                    ),
                    (None, None),
                    test=False,
                    brute=False,
                    triangluarize=True,
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def ernstmixed1():
                rst = ernst05.mixed_1(
                    Integer(self.ui.N_le.text()),
                    Integer(self.ui.e_le.text()),
                    (
                        Integer(self.ui.d_msb_le.text()),
                        Integer(self.ui.d_lsb_le.text()),
                    ),
                    (
                        Integer(self.ui.d_len_le.text()),
                        Integer(self.ui.msb_len_le.text()),
                        Integer(self.ui.lsb_len_le.text()),
                    ),
                    (None, None),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def ernstmixed2():
                rst = ernst05.mixed_2(
                    Integer(self.ui.N_le.text()),
                    Integer(self.ui.e_le.text()),
                    (
                        Integer(self.ui.d_msb_le.text()),
                        Integer(self.ui.d_lsb_le.text()),
                    ),
                    (
                        Integer(self.ui.d_len_le.text()),
                        Integer(self.ui.msb_len_le.text()),
                        Integer(self.ui.lsb_len_le.text()),
                    ),
                    (None, None),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            方法 = self.ui.atk_cb.currentIndex()
            攻击函数 = [
                tk14msb,
                tk14lsb,
                tk14mixed,
                ernstmixed1,
                ernstmixed2,
            ]

            攻击函数[方法]()

        self.ui.rsa_atk_btn.clicked.connect(rsa攻击)

    def 连crt_atk_btn(self):
        def crt攻击():
            def mns21lsb():
                rst = mns21.dp_dq_with_lsb(
                    Integer(self.ui.crt_N_le.text()),
                    Integer(self.ui.crt_e_le.text()),
                    (
                        Integer(self.ui.crt_dp_lsb_le.text()),
                        Integer(self.ui.crt_dq_lsb_le.text()),
                    ),
                    (
                        Integer(self.ui.crt_dp_len_le.text()),
                        Integer(self.ui.crt_dq_len_le.text()),
                        Integer(self.ui.crt_lsb_len_le.text()),
                    ),
                    (None, None),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def mns22msb():
                rst = src.mns22.small_e_dp_dq_with_msb(
                    Integer(self.ui.crt_N_le.text()),
                    Integer(self.ui.crt_e_le.text()),
                    (Integer(self.ui.crt_dp_msb_le.text()), Integer(self.ui.crt_dq_msb_le.text())),
                    (
                        Integer(self.ui.crt_dp_len_le.text()),
                        Integer(self.ui.crt_dq_len_le.text()),
                        Integer(self.ui.crt_msb_len_le.text()),
                        Integer(self.ui.crt_msb_len_le.text())
                    ),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def mns22lsb():
                rst = src.mns22.small_e_dp_dq_with_lsb(
                    Integer(self.ui.crt_N_le.text()),
                    Integer(self.ui.crt_e_le.text()),
                    (Integer(self.ui.crt_dp_lsb_le.text()), Integer(self.ui.crt_dq_lsb_le.text())),
                    (
                        Integer(self.ui.crt_dp_len_le.text()),
                        Integer(self.ui.crt_dq_len_le.text()),
                        Integer(self.ui.crt_lsb_len_le.text()),
                    ),
                    (None,),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def tlp17small_e():
                rst = src.tlp17.small_e(
                    Integer(self.ui.crt_N_le.text()),
                    Integer(self.ui.crt_e_le.text()),
                    (
                        Integer(self.ui.crt_p_len_le.text()),
                        Integer(self.ui.crt_dq_len_le.text()),
                    ),
                    (None,),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            def tlp17large_e():
                rst = src.tlp17.large_e(
                    Integer(self.ui.crt_N_le.text()),
                    Integer(self.ui.crt_e_le.text()),
                    (
                        Integer(self.ui.crt_p_len_le.text()),
                        Integer(self.ui.crt_dq_len_le.text()),
                    ),
                    (None,),
                )
                print(
                    f"""攻击成功！私钥 d = 
{rst}"""
                    if rst is not None
                    else "攻击失败！"
                )

            方法 = self.ui.crt_atk_cb.currentIndex()
            攻击函数 = [mns21lsb, mns22msb, mns22lsb, tlp17small_e, tlp17large_e]

            攻击函数[方法]()

        self.ui.crt_atk_btn.clicked.connect(crt攻击)

    def 连var_atk_btn(self):
        def var攻击():
            def mns22():
                rst = src.mns22.mixed_kp(
                    Integer(self.ui.var_N_le.text()),
                    Integer(self.ui.var_e_le.text()),
                    (
                        Integer(self.ui.var_kp_msb_le.text()),
                        Integer(self.ui.var_kp_lsb_le.text()),
                    ),
                    (
                        Integer(self.ui.var_kp_len_le.text()),
                        Integer(self.ui.msb_len_le.text()),
                        Integer(self.ui.lsb_len_le.text()),
                    ),
                    (None, None),
                )
                print(f"攻击成功！私钥 d = {rst}")

            方法 = self.ui.var_atk_cb.currentIndex()
            攻击函数 = [mns22]

            攻击函数[方法]()

        self.ui.var_atk_btn.clicked.connect(var攻击)

    def 连auto_atk_btn(self):
        def auto攻击():
            automated(
                Integer(self.ui.auto_M_le.text()),
                Integer(self.ui.auto_m_le.text()),
                Integer(self.ui.auto_var_le.text()),
                Integer(self.ui.auto_mono_set_le.text()),
                Integer(self.ui.auto_eq_le.text()),
            )

        self.ui.auto_atk_btn.clicked.connect(auto攻击)

    def 换页(self):
        btn_list = [
            (self.ui.home_btn, 0),
            (self.ui.rsa_btn, 1),
            (self.ui.crt_btn, 2),
            (self.ui.var_btn, 3),
            (self.ui.auto_btn, 4),
            (self.ui.usr_btn, 5),
            (self.ui.stg_btn, 6),
            (self.ui.about_btn, 7),
        ]
        for btn, i in btn_list:
            btn.clicked.connect(lambda _, idx=i: self.ui.page_stk.setCurrentIndex(idx))

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


class te_stdout重定向(io.StringIO):
    def __init__(self, te):
        super().__init__()
        self.te = te

    def write(self, string):
        QApplication.processEvents()  # 激活事件循环
        cursor = self.te.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(string)
        self.te.setTextCursor(cursor)
        self.te.ensureCursorVisible()

    def redirect_stdout(self):
        sys.stdout = self

    def restore_stdout(self):
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    cfg = 配置(
        [{"name": "主页", "icon": "主页.png"}, {"name": "RSA", "icon": "RSA.png"}]
    )
    app = QApplication(sys.argv)
    win = 主窗(cfg)
    win.show()
    sys.exit(app.exec())
