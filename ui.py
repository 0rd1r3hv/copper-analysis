from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from src.cfg import Cfg


class MainWinIniter:
    def setup_ui(self, main_win: QMainWindow):
        if not main_win.objectName():
            main_win.setObjectName("main_win")
        main_win.setMinimumSize(main_win.cfg.win_min_size)
        main_win.setWindowIcon(QIcon(f"{main_win.cfg.icon_dir}/徽标.png"))

        self._setup_cent(main_win)
        self._setup_sidebar_frm(main_win.cfg)
        self._setup_srch_hlo(main_win.cfg)
        self._setup_page_stk(main_win.cfg)
        self._finalize_lo(main_win)

    def _setup_cent(self, main_win: QMainWindow):
        self.cent = QWidget(main_win)
        self.cent.setObjectName("cent")
        self.cent.setMinimumSize(main_win.cfg.win_min_size)

        self.cent_glo = QGridLayout(self.cent)
        self.cent_glo.setObjectName("cent_glo")
        self.cent_glo.setSpacing(4)
        self.cent_glo.setContentsMargins(0, 0, 0, 0)

    def _setup_sidebar_frm(self, cfg: Cfg):
        self.sidebar_frm = QFrame()
        self.sidebar_frm.setObjectName("sidebar_frm")
        self.sidebar_frm.setStyleSheet("""QFrame#sidebar_frm {
            background-color: #2F4F4F;
            border: 2px solid #00CA9A; 
            border-radius: 12px; 
            border-left: 0px; 
            border-top-left-radius: 0px; 
            border-bottom-left-radius: 0px;
        }""")

        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.sidebar_frm.setSizePolicy(sizePolicy)

        self.sidebar_glo = QGridLayout(self.sidebar_frm)
        self.sidebar_glo.setSpacing(0)
        self.sidebar_glo.setObjectName("sidebar_glo")
        self.sidebar_glo.setContentsMargins(0, 0, 0, 0)

        self._setup_sidebar_icon(cfg)
        self._setup_sidebar_lbl(cfg)
        self._setup_sidebar_spcs()

        self.cent_glo.addWidget(self.sidebar_frm, 0, 0, 2, 1)

    def _setup_sidebar_icon(self, cfg: Cfg):
        buttons = [
            ("icon_lbl", f"{cfg.icon_dir}/密码学会.png", 0, 0),
            ("pnl_btn", f"{cfg.icon_dir}/展开面板.png", 1, 0),
            ("home_btn", f"{cfg.icon_dir}/主页.png", 2, 0),
            ("rsa_btn", f"{cfg.icon_dir}/RSA.png", 3, 0),
            ("crt_rsa_btn", f"{cfg.icon_dir}/CRT-RSA.png", 4, 0),
            ("var_btn", f"{cfg.icon_dir}/单变元.png", 5, 0),
            ("auto_btn", f"{cfg.icon_dir}/自动.png", 6, 0),
            ("usr_btn", f"{cfg.icon_dir}/用户.png", 8, 0),
            ("stg_btn", f"{cfg.icon_dir}/设置.png", 9, 0),
            ("about_btn", f"{cfg.icon_dir}/关于.png", 10, 0),
        ]

        for name, icon_path, row, col in buttons:
            widget = self._create_icon_btn(name, icon_path, cfg)
            widget.setFixedSize(cfg.btn_size)
            self.sidebar_glo.addWidget(widget, row, col, 1, 1)

        self.pnl_btn.setCheckable(True)

    def _create_icon_btn(self, name, icon, cfg):
        if name == "icon_lbl":
            widget = QLabel(self.cent)
            widget.setPixmap(
                QPixmap(icon).scaled(
                    cfg.icon_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
            widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            widget = QPushButton(self.cent)
            widget.setIcon(QIcon(icon))
            widget.setIconSize(cfg.icon_size)
            widget.setFlat(True)
        widget.setObjectName(name)
        setattr(self, name, widget)
        return widget

    def _setup_sidebar_lbl(self, cfg: Cfg):
        labels = [
            ("tit_lbl", 0, 1),
            ("home_lbl", 2, 1),
            ("rsa_lbl", 3, 1),
            ("crt_rsa_lbl", 4, 1),
            ("var_lbl", 5, 1),
            ("auto_lbl", 6, 1),
            ("usr_lbl", 8, 1),
            ("stg_lbl", 9, 1),
            ("about_lbl", 10, 1),
        ]

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        for name, row, col in labels:
            label = QLabel(self.cent)
            label.setObjectName(name)
            sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
            label.setSizePolicy(sizePolicy)
            label.setFixedSize(cfg.lbl_size)
            label.setStyleSheet("QLabel {font-size: 14pt;}")

            self.sidebar_glo.addWidget(label, row, col, 1, 1)
            setattr(self, name, label)

    def _setup_sidebar_spcs(self):
        spacers = [
            (
                "icon_vspc",
                7,
                0,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum,
            ),
            (
                "ext_vspc",
                7,
                1,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Expanding,
            ),
            (
                "pnl_btn_vspc",
                1,
                1,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Maximum,
                48,
            ),
        ]

        for name, row, col, h_policy, v_policy, *args in spacers:
            spacer = QSpacerItem(0, args[0] if args else 0, h_policy, v_policy)
            self.sidebar_glo.addItem(spacer, row, col, 1, 1)
            setattr(self, name, spacer)

        for row in range(self.sidebar_glo.rowCount()):
            item = self.sidebar_glo.itemAtPosition(row, 1)
            if w := item.widget():
                w.hide()

    def _setup_srch_hlo(self, cfg: Cfg):
        self.srch_hlo = QHBoxLayout()
        self.srch_hlo.setSpacing(0)
        self.srch_hlo.setContentsMargins(0, 0, 0, 0)
        self.srch_hlo.setObjectName("srch_hlo")

        self.srch_hspc = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.srch_hlo.addItem(self.srch_hspc)

        self.srch_le = QLineEdit(self.cent)
        self.srch_le.setObjectName("srch_le")
        self.srch_le.setMinimumSize(cfg.srch_le_min_size)
        self.srch_hlo.addWidget(self.srch_le)

        self.srch_btn = QPushButton(self.cent)
        self.srch_btn.setObjectName("srch_btn")
        self.srch_btn.setFixedSize(cfg.btn_size)
        self.srch_btn.setIconSize(cfg.icon_size)
        self.srch_btn.setFlat(False)
        self.srch_btn.setIcon(QIcon(f"{cfg.icon_dir}/搜索.png"))
        self.srch_hlo.addWidget(self.srch_btn)

        self.cent_glo.addLayout(self.srch_hlo, 0, 1, 1, 1)

    def _setup_page_stk(self, cfg: Cfg):
        self.page_stk = QStackedWidget(self.cent)
        self.page_stk.setObjectName("page_stk")

        pages = [
            "home_page",
            "rsa_page",
            "crt_rsa_page",
            "var_page",
            "auto_page",
            "usr_page",
            "stg_page",
            "about_page",
        ]

        for page in pages:
            widget = QWidget()
            widget.setObjectName(page)
            self.page_stk.addWidget(widget)
            setattr(self, page, widget)

        self._setup_home_page(cfg)
        self._setup_rsa_page(cfg)
        self._setup_crt_rsa_page(cfg)
        self._setup_var_page(cfg)
        self._setup_auto_page(cfg)
        self._setup_usr_page(cfg)
        self._setup_stg_page(cfg)
        self._setup_about_page(cfg)

        self.cent_glo.addWidget(self.page_stk, 1, 1, 1, 1)

    def _setup_home_page(self, cfg: Cfg):
        # 创建主布局
        home_vlo = QVBoxLayout(self.home_page)
        home_vlo.setSpacing(20)
        home_vlo.setContentsMargins(20, 20, 20, 20)

        # 上半部分：图标和标题
        upper_widget = QWidget()
        upper_widget.setMaximumHeight(self.home_page.height() // 2)
        upper_vlo = QVBoxLayout(upper_widget)
        upper_vlo.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_pixmap = QPixmap(f"{cfg.icon_dir}/徽标.png").scaled(
            192, 192, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel("自动化公钥密码系统 Coppersmith 格攻击工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold;")

        upper_vlo.addWidget(icon_label)
        upper_vlo.addWidget(title_label)

        # 下半部分：三个框架
        lower_widget = QWidget()
        lower_hlo = QHBoxLayout(lower_widget)
        lower_hlo.setSpacing(20)

        frames = [
            "针对 RSA 的攻击",
            "针对 CRT-RSA 的攻击",
            "单变元模方程攻击",
            "自动化通用攻击",
        ]
        for frame_title in frames:
            frame = QGroupBox(frame_title)
            frame.setStyleSheet("QGroupBox { border-color: #00CA9A; font-size: 14pt; }")
            frame_vlo = QVBoxLayout(frame)
            if frame_title == "针对 RSA 的攻击":
                text = """<p>已实现多种特定情形下已知上界最好的 d 泄露攻击。本工具提供五种攻击类型：</p>
<p>Takayasu, Kunihiro 对高位和低位泄露攻击的改进方案（无泄露等价 Boneh-Durfee 最优方案）；</p>
<p>Ernst 等人对高低位混合泄露的两种攻击方案；</p>
<p>Takayasu, Kunihiro 对 Ernst 等人混合泄露方案的等价替代。</p>
"""
            elif frame_title == "针对 CRT-RSA 的攻击":
                text = """<p>已实现多种特定情形下已知上界最优的 CRT-RSA d<sub>p</sub>, d<sub>q</sub> 部分泄露攻击方案。本工具所提供的六大功能包括：</p>
<p>Takayasu 等人提出的针对小 d<sub>p</sub>和小 d<sub>p</sub>,d<sub>q</sub> 的三种攻击方案；</p>
<p>May 等人针对 d<sub>p</sub>,d<sub>q</sub> 的纯低位泄露攻击；</p>
<p>May 等人针对小 e 情况下 d<sub>p</sub>,d<sub>q</sub> 的纯高位和纯低位泄露攻击。</p>"""
            elif frame_title == "单变元模方程攻击":
                text = """<p>本工具实现了以下单变元模多项式方程攻击类型：</p>
<p>Coppersmith 格基模 N 单变元方程的攻击方法；</p>
<p>Howgrave-Graham 对模 N 的未知因数的单变元方程的攻击；</p>
<p>May 等人对模未知因数的已知倍数的单变元线性方程的攻击。</p>"""
            else:
                text = """<p>本工具实现了 Meers, Nowakowski 提出的 Coppersmith 攻击的自动化构造算法。该种新型方法针对所给的一系列模方程和指定的单项式集合，自动分析并选择该单项式集合下的最优移位多项式供后续求解使用；对于形式较为复杂的多项式，该自动化方法的应用将使求解的进行变得极其便捷。</p>"""
            text_label = QLabel(text)
            text_label.setOpenExternalLinks(True)
            text_label.setMinimumWidth(192)
            text_label.setWordWrap(True)
            text_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            text_label.setStyleSheet("QLabel { font-size: 14pt; }")
            frame_vlo.addWidget(text_label)
            lower_hlo.addWidget(frame)

        # 将上下两部分添加到主布局
        home_vlo.addWidget(upper_widget)
        home_vlo.addWidget(lower_widget)

    def _setup_rsa_page(self, cfg: Cfg):
        self.rsa_hlo = QHBoxLayout(self.rsa_page)
        self.rsa_hlo.setObjectName("rsa_hlo")
        self.parma_cont = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.parma_cont.setSizePolicy(sizePolicy)
        self.parma_cont.setFixedWidth(640)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.parma_cont.setSizePolicy(sizePolicy)

        self.parma_vlo = QVBoxLayout(self.parma_cont)
        self.parma_vlo.setSpacing(4)
        self.parma_vlo.setContentsMargins(0, 0, 0, 0)

        # 添加新的水平组合
        atk_frm = QFrame()
        atk_frm.setMinimumHeight(64)
        atk_hlo = QHBoxLayout(atk_frm)
        atk_hlo.setContentsMargins(12, 0, 12, 0)
        atk_hlo.setSpacing(16)
        atk_hlo.setAlignment(Qt.AlignLeft)
        atk_lbl = QLabel("攻击方法")
        atk_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        atk_lbl.setMinimumWidth(120)
        atk_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
        atk_cb = QComboBox()
        atk_cb.setFixedWidth(120)
        atk_cb.setStyleSheet("QComboBox { background-color: #8A8A8A; }")
        atk_cb.setObjectName("atk_cb")
        atk_cb.setMinimumHeight(40)
        atk_cb.addItems(
            ["TK14 MSB", "TK14 LSB", "TK14 Mixed", "Ernst Mixed1", "Ernst Mixed2"]
        )  # 添加攻击方法选项
        setattr(self, "atk_cb", atk_cb)
        atk_hlo.addWidget(atk_lbl)
        atk_hlo.addWidget(atk_cb)
        self.parma_vlo.addWidget(atk_frm)

        params = ["N", "e", "d_len", "msb_len", "lsb_len", "m", "t", "d_msb", "d_lsb"]
        params_name = [
            "模数 N",
            "公钥 e",
            "私钥 d 长度",
            "MSB 长度",
            "LSB 长度",
            "m（可选）",
            "t（可选）",
            "私钥 MSB",
            "私钥 LSB",
        ]
        for param, name in zip(params, params_name):
            param_frm = QFrame()
            param_frm.setMinimumHeight(64)
            param_hlo = QHBoxLayout(param_frm)
            param_hlo.setContentsMargins(12, 0, 12, 0)
            param_hlo.setSpacing(16)
            param_lbl = QLabel(name)
            param_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            param_lbl.setMinimumWidth(120)
            param_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
            param_le = QLineEdit()
            param_le.setStyleSheet("QLineEdit { background-color: #8A8A8A; }")
            param_le.setObjectName(f"rsa_{param}_le")
            param_le.setMinimumHeight(40)
            setattr(self, f"{param}_le", param_le)
            param_hlo.addWidget(param_lbl)
            param_hlo.addWidget(param_le)
            self.parma_vlo.addWidget(param_frm)

        self.m_le.setPlaceholderText("（自动选取）")
        self.t_le.setPlaceholderText("（自动选取）")
        self.parma_vlo.addStretch(1)
        self.parma_vlo.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.atk_btn = QPushButton("开始攻击")
        self.atk_btn.setObjectName("atk_btn")
        self.atk_btn.setMinimumSize(cfg.btn_size)
        self.parma_vlo.addWidget(self.atk_btn)
        self.rsa_hlo.addWidget(self.parma_cont)
        self.rsa_text_display = QTextEdit()
        self.rsa_text_display.setStyleSheet("QTextEdit { font-size: 12pt; }")
        self.rsa_text_display.setObjectName("rsa_text_display")
        self.rsa_text_display.setReadOnly(True)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rsa_text_display.setSizePolicy(size_policy)

        self.rsa_hlo.addWidget(self.rsa_text_display)

    def _setup_crt_rsa_page(self, cfg: Cfg):
        self.crt_rsa_hlo = QHBoxLayout(self.crt_rsa_page)
        self.crt_rsa_hlo.setObjectName("crt_rsa_hlo")
        self.crt_parma_cont = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.crt_parma_cont.setSizePolicy(sizePolicy)
        self.crt_parma_cont.setFixedWidth(640)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.crt_parma_cont.setSizePolicy(sizePolicy)

        self.crt_parma_vlo = QVBoxLayout(self.crt_parma_cont)
        self.crt_parma_vlo.setSpacing(4)
        self.crt_parma_vlo.setContentsMargins(0, 0, 0, 0)

        # 添加新的水平组合
        crt_atk_frm = QFrame()
        crt_atk_frm.setMinimumHeight(64)
        crt_atk_hlo = QHBoxLayout(crt_atk_frm)
        crt_atk_hlo.setContentsMargins(12, 0, 12, 0)
        crt_atk_hlo.setSpacing(16)
        crt_atk_hlo.setAlignment(Qt.AlignLeft)
        crt_atk_lbl = QLabel("攻击方法")
        crt_atk_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        crt_atk_lbl.setMinimumWidth(120)
        crt_atk_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
        crt_atk_cb = QComboBox()
        crt_atk_cb.setFixedWidth(120)
        crt_atk_cb.setStyleSheet("QComboBox { background-color: #8A8A8A; }")
        crt_atk_cb.setObjectName("crt_atk_cb")
        crt_atk_cb.setMinimumHeight(40)
        crt_atk_cb.addItems(["MNS21"])
        setattr(self, "crt_atk_cb", crt_atk_cb)
        crt_atk_hlo.addWidget(crt_atk_lbl)
        crt_atk_hlo.addWidget(crt_atk_cb)
        self.crt_parma_vlo.addWidget(crt_atk_frm)

        crt_params = [
            "N",
            "e",
            "dp_len",
            "dq_len",
            "msb_len",
            "lsb_len",
            "dp_msb",
            "dq_msb",
            "dp_lsb",
            "dq_lsb",
        ]
        crt_params_name = [
            "模数 N",
            "公钥 e",
            "d<sub>p</sub> 长度",
            "d<sub>q</sub> 长度",
            "MSB 长度",
            "LSB 长度",
            "d<sub>p</sub> MSB",
            "d<sub>q</sub> MSB",
            "d<sub>p</sub> LSB",
            "d<sub>q</sub> LSB",
        ]
        for param, name in zip(crt_params, crt_params_name):
            param_frm = QFrame()
            param_frm.setMinimumHeight(64)
            param_hlo = QHBoxLayout(param_frm)
            param_hlo.setContentsMargins(12, 0, 12, 0)
            param_hlo.setSpacing(16)
            param_lbl = QLabel(name)
            param_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            param_lbl.setMinimumWidth(120)
            param_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
            param_le = QLineEdit()
            param_le.setStyleSheet("QLineEdit { background-color: #8A8A8A; }")
            param_le.setObjectName(f"crt_rsa_{param}_le")
            param_le.setMinimumHeight(40)
            setattr(self, f"crt_rsa_{param}_le", param_le)
            param_hlo.addWidget(param_lbl)
            param_hlo.addWidget(param_le)
            self.crt_parma_vlo.addWidget(param_frm)

        self.crt_parma_vlo.addStretch(1)
        self.crt_parma_vlo.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.crt_atk_btn = QPushButton("开始攻击")
        self.crt_atk_btn.setObjectName("crt_atk_btn")
        self.crt_atk_btn.setMinimumSize(cfg.btn_size)
        self.crt_parma_vlo.addWidget(self.crt_atk_btn)

        self.crt_rsa_hlo.addWidget(self.crt_parma_cont)
        self.crt_rsa_text_display = QTextEdit()
        self.crt_rsa_text_display.setStyleSheet("QTextEdit { font-size: 12pt; }")
        self.crt_rsa_text_display.setObjectName("crt_rsa_text_display")
        # self.crt_rsa_text_display.setReadOnly(True)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.crt_rsa_text_display.setSizePolicy(size_policy)

        self.crt_rsa_hlo.addWidget(self.crt_rsa_text_display)

    def _setup_var_page(self, cfg: Cfg):
        self.var_hlo = QHBoxLayout(self.var_page)
        self.var_hlo.setObjectName("var_hlo")
        self.var_parma_cont = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.var_parma_cont.setSizePolicy(sizePolicy)
        self.var_parma_cont.setFixedWidth(640)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred
        )
        self.var_parma_cont.setSizePolicy(sizePolicy)

        self.var_parma_vlo = QVBoxLayout(self.var_parma_cont)
        self.var_parma_vlo.setSpacing(4)
        self.var_parma_vlo.setContentsMargins(0, 0, 0, 0)

        var_atk_frm = QFrame()
        var_atk_frm.setMinimumHeight(64)
        var_atk_hlo = QHBoxLayout(var_atk_frm)
        var_atk_hlo.setContentsMargins(12, 0, 12, 0)
        var_atk_hlo.setSpacing(16)
        var_atk_hlo.setAlignment(Qt.AlignLeft)
        var_atk_lbl = QLabel("攻击方法")
        var_atk_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        var_atk_lbl.setMinimumWidth(120)
        var_atk_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
        var_atk_cb = QComboBox()
        var_atk_cb.setFixedWidth(120)
        var_atk_cb.setStyleSheet("QComboBox { background-color: #8A8A8A; }")
        var_atk_cb.setObjectName("var_atk_cb")
        var_atk_cb.setMinimumHeight(40)
        var_atk_cb.addItems(["MNS22"])
        setattr(self, "var_atk_cb", var_atk_cb)
        var_atk_hlo.addWidget(var_atk_lbl)
        var_atk_hlo.addWidget(var_atk_cb)
        self.var_parma_vlo.addWidget(var_atk_frm)

        # 添加参数输入框
        var = ["N", "k", "p_len", "msb_len", "lsb_len", "kp_msb", "kp_lsb", "mod_eq"]
        var_params = [
            "模数 N",
            "倍数 k",
            "因数 p 长度",
            "kp MSB 长度",
            "kp LSB 长度",
            "kp MSB",
            "kp LSB",
            "模方程",
        ]
        for param, name in zip(var, var_params):
            param_frm = QFrame()
            param_frm.setMinimumHeight(64)
            param_hlo = QHBoxLayout(param_frm)
            param_hlo.setContentsMargins(12, 0, 12, 0)
            param_hlo.setSpacing(16)
            param_lbl = QLabel(name)
            param_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            param_lbl.setMinimumWidth(120)
            param_lbl.setStyleSheet("QLabel {font-size: 14pt;}")
            param_le = QLineEdit()
            param_le.setStyleSheet("QLineEdit { background-color: #8A8A8A; }")
            param_le.setObjectName(f"var_{param.lower().replace(' ', '_')}_le")
            param_le.setMinimumHeight(40)
            setattr(self, f"var_{param.lower().replace(' ', '_')}_le", param_le)
            param_hlo.addWidget(param_lbl)
            param_hlo.addWidget(param_le)
            self.var_parma_vlo.addWidget(param_frm)

        self.var_parma_vlo.addStretch(1)
        self.var_parma_vlo.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )
        self.var_atk_btn = QPushButton("开始攻击")
        self.var_atk_btn.setObjectName("var_atk_btn")
        self.var_atk_btn.setMinimumSize(cfg.btn_size)
        self.var_parma_vlo.addWidget(self.var_atk_btn)

        self.var_hlo.addWidget(self.var_parma_cont)
        self.var_text_display = QTextEdit()
        self.var_text_display.setStyleSheet("QTextEdit { font-size: 12pt; }")
        self.var_text_display.setObjectName("var_text_display")
        # self.var_text_display.setReadOnly(True)

        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.var_text_display.setSizePolicy(size_policy)

        self.var_hlo.addWidget(self.var_text_display)

    def _setup_auto_page(self, cfg: Cfg):
        pass

    def _setup_usr_page(self, cfg: Cfg):
        pass

    def _setup_stg_page(self, cfg: Cfg):
        self.stg_scroll_area = QScrollArea(self.stg_page)
        self.stg_scroll_area.setWidgetResizable(True)
        self.stg_scroll_cont = QWidget()
        self.stg_vlo = QVBoxLayout(self.stg_scroll_cont)
        self.stg_vlo.setSpacing(12)
        self.stg_vlo.setContentsMargins(12, 12, 12, 12)
        self.opt_hspc = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        for grp_name, opt_list in cfg.stg_grp_list.items():
            gb = self._create_gb(grp_name)
            grp_vlo = QVBoxLayout(gb)
            grp_vlo.setSpacing(12)
            grp_vlo.setContentsMargins(0, 12, 0, 12)

            for opt_name, opt_icon, opt in opt_list:
                opt_frm = self._create_opt_frm(opt_name, opt_icon, opt, cfg)
                grp_vlo.addWidget(opt_frm)

            self.stg_vlo.addWidget(gb)

        self.stg_vlo.addStretch(1)
        self.stg_scroll_area.setWidget(self.stg_scroll_cont)

        stg_page_layout = QVBoxLayout(self.stg_page)
        stg_page_layout.setContentsMargins(0, 0, 0, 0)
        stg_page_layout.addWidget(self.stg_scroll_area)

    def _create_gb(self, grp_name):
        gb = QGroupBox(grp_name)
        gb.setObjectName(f"{grp_name}_gb")
        gb.setStyleSheet("QGroupBox{border:0px;}")
        return gb

    def _create_opt_frm(self, opt_name, opt_icon, opt, cfg):
        opt_frm = QFrame()
        opt_frm.setObjectName(f"{opt_name}_frm")
        opt_hlo = QHBoxLayout(opt_frm)
        opt_hlo.setSpacing(12)
        opt_hlo.setContentsMargins(12, 12, 12, 12)

        icon_opt_lbl = self._create_icon_opt_lbl(opt_name, opt_icon, cfg)
        opt_hlo.addWidget(icon_opt_lbl)

        opt_lbl = QLabel()
        opt_lbl.setObjectName(f"{opt_name}_lbl")
        opt_lbl.setText(opt_name)
        setattr(self, f"{opt_name}_lbl", opt_lbl)
        opt_hlo.addWidget(opt_lbl)

        if isinstance(opt, list):
            opt_cb = QComboBox()
            opt_cb.addItems(opt)
            setattr(self, f"{opt_name}_cb", opt_cb)
            opt_hlo.addItem(self.opt_hspc)
            opt_hlo.addWidget(opt_cb)

        return opt_frm

    def _create_icon_opt_lbl(self, opt_name, opt_icon, cfg):
        icon_opt_lbl = QLabel()
        icon_opt_lbl.setObjectName(f"icon_{opt_name}_lbl")
        icon_opt_lbl.setPixmap(
            QPixmap(f"{cfg.icon_dir}/{opt_icon}").scaled(
                cfg.opt_icon_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        icon_opt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setattr(self, f"icon_{opt_name}_lbl", icon_opt_lbl)
        return icon_opt_lbl

    def _setup_about_page(self, cfg: Cfg):
        about_vlo = QVBoxLayout(self.about_page)
        about_vlo.setContentsMargins(20, 20, 20, 20)
        about_upper_hlo = QHBoxLayout()
        about_upper_hlo.setAlignment(Qt.AlignTop)
        about_upper_hlo.setSpacing(20)
        about_upper_hlo.setContentsMargins(20, 20, 20, 20)
        about_vlo.addLayout(about_upper_hlo)
        about_lower_hlo = QHBoxLayout()
        about_lower_hlo.setAlignment(Qt.AlignBottom)
        about_vlo.addLayout(about_lower_hlo)
        intro_gb = QGroupBox("关于本工具")
        intro_lbl = QLabel(
            """<p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>铜钥（CSyde）</b>自动化公钥密码系统 Coppersmith 格攻击工具由 <a href="https://www.sagemath.org/">SageMath</a> 数学引擎驱动，基于 <a href="https://doc.qt.io/qtforpython-6/">PySide6</a> 可视化框架实现图形交互，根据底层组件声明而遵循 GPL v3 开源协议许可证。</p>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;我们整合重现了数十年来相关作品中提出的多种攻击方案，并将<b>创新性优化</b>改进集成其中，实现了对 RSA、CRT-RSA、单变元攻击和自动化 Coppersmith 方法的全面支持和高效执行。在极大提高原有方案执行效率并提升实际攻击上界的同时，我们还提供了对复杂多项式方程的移位多项式的自动化构造，以便密码和安全从业者便捷地进行 RSA 及其变体密码系统中密钥参数的选取以及相关秘密参数泄露对系统安全性影响的评估，使用者不必耗费大量精力研究各具体攻击方案的实现和性能调优即可开展多种情形下的最优攻击。</p>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;本软件同样面向密码或网安专业的学生和初学者等，对于公钥密码的知识普及、安全评估、分析研究将会产生良好的推进作用。</p>"""
        )
        intro_lbl.setStyleSheet("QLabel { font-size: 16pt; }")
        intro_lbl.setWordWrap(True)
        intro_gb_layout = QVBoxLayout(intro_gb)
        intro_gb_layout.addWidget(intro_lbl)
        about_upper_hlo.addWidget(intro_gb)

        inno_gb = QGroupBox("我们的创新")
        inno_lbl = QLabel(
            """<p>1. 对于含有 p+q 相关变元的攻击，我们将变元上界<b>至少缩小 4 个比特</b>，进而<b>提升了攻击的实际上界</b>。</p>
            <p>2. 求解变元大小逼近攻击上界的方程时，我们提出格基递推方法的一种扩展，在维度为 50 至 130 时，<b>将后续的格基约化时间缩减了 30% 至 80%</b>。</p>
            <p>3. 针对实际攻击维度极高的瓶颈，我们利用攻击界相同的低维格基，成功缩减了格维度的渐进复杂度。</p>
            <p>4. 通过实现特殊攻击的格基矩阵的三角化，我们<b>将这类格基的约化用时缩减了 50% 至 70%</b>。</p>
            <p>5. 在求根算法上，我们挖掘算法并行性，给出了新的多进程版本，并实现了一种更加实用的多项式筛选方法。</p>
            <p>6. 对于复杂多项式方程的移位多项式的构造，通过实现<b>自动化 Coppersmith 方法</b>来解决手动选择困难的问题。</p>
            """
        )
        inno_lbl.setStyleSheet("QLabel { font-size: 16pt; }")
        inno_lbl.setWordWrap(True)
        inno_gb_layout = QVBoxLayout(inno_gb)
        inno_gb_layout.addWidget(inno_lbl)
        about_upper_hlo.addWidget(inno_gb)

        left_vlo = QVBoxLayout()
        left_lower = QWidget()
        left_lower.setMaximumHeight(320)
        left_vlo.addWidget(left_lower)
        about_lower_hlo.addLayout(left_vlo)

        right_vlo = QVBoxLayout()
        right_lower = QWidget()
        right_vlo.addWidget(right_lower)
        about_lower_hlo.addLayout(right_vlo)

        names = [
            "樊宸华(0rd1r3hv)",
            "张九洲(observer-297)",
            "任宇涵(Kh05ifr4nD)",
            "C1phr34k from XDU",
        ]

        left_vlo.setSpacing(4)
        left_vlo.setContentsMargins(20, 20, 20, 20)
        left_vlo.setStretch(0, 1)
        for name in names:
            frame = QFrame()
            frame.setMaximumWidth(384)
            frame.setMaximumHeight(96)
            frame.setStyleSheet("QFrame { border: 1px solid #00CA9A; }")
            frame_hlo = QHBoxLayout(frame)

            icon_label = QLabel()
            if name == "樊宸华(0rd1r3hv)":
                icon_label.setPixmap(
                    QPixmap(f"{cfg.icon_dir}/fch.jpg").scaled(
                        64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
            elif name == "张九洲(observer-297)":
                icon_label.setPixmap(
                    QPixmap(f"{cfg.icon_dir}/zjz.jpg").scaled(
                        64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
            elif name == "任宇涵(Kh05ifr4nD)":
                icon_label.setPixmap(
                    QPixmap(f"{cfg.icon_dir}/ryh.png").scaled(
                        64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
            elif name == "C1phr34k from XDU":
                icon_label.setPixmap(
                    QPixmap(f"{cfg.icon_dir}/xdu.png").scaled(
                        64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )

            icon_label.setStyleSheet("QLabel { border: none; }")

            text_label = QLabel(name)
            text_label.setStyleSheet("QLabel { border: none; font-size: 20pt; }")

            frame_hlo.addWidget(icon_label)
            frame_hlo.addWidget(text_label)
            frame_hlo.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

            left_vlo.addWidget(frame)

        # 在右下角添加图标和标签
        right_hlo = QHBoxLayout(right_lower)
        right_hlo.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        icon_label = QLabel()
        icon_label.setPixmap(
            QPixmap(f"{cfg.icon_dir}/密码学会.png").scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        icon_label.setStyleSheet("QLabel { border: none; }")

        text_label = QLabel("铜钥 CSyde v0.4.1")
        text_label.setStyleSheet("QLabel { border: none; font-size: 24pt; }")

        right_hlo.addWidget(icon_label)
        right_hlo.addWidget(text_label)

    def _finalize_lo(self, main_win: QMainWindow):
        main_win.setCentralWidget(self.cent)
        self.retranslateUi(main_win)
        QMetaObject.connectSlotsByName(main_win)

    def retranslateUi(self, main_win: QMainWindow):
        main_win.setWindowTitle(QCoreApplication.translate("CSyde", "铜钥 CSyde", None))
        self.rsa_lbl.setText(QCoreApplication.translate("main_win", "RSA 攻击", None))
        self.crt_rsa_lbl.setText(
            QCoreApplication.translate("main_win", "CRT-RSA 攻击", None)
        )
        self.var_lbl.setText(QCoreApplication.translate("main_win", "单变元攻击", None))
        self.auto_lbl.setText(QCoreApplication.translate("main_win", "自动化", None))
        self.usr_lbl.setText(QCoreApplication.translate("main_win", "用户", None))
        self.tit_lbl.setText(QCoreApplication.translate("main_win", "铜钥", None))

        self.stg_lbl.setText(QCoreApplication.translate("main_win", "设置", None))
        self.home_lbl.setText(QCoreApplication.translate("main_win", "主页", None))
        self.about_lbl.setText(QCoreApplication.translate("main_win", "关于", None))
        self.srch_le.setPlaceholderText(
            QCoreApplication.translate("Search…", "搜索……", None)
        )
        self.usr_btn.setText("")
        self.stg_btn.setText("")
        self.about_btn.setText("")
        self.home_btn.setText("")
        self.pnl_btn.setText("")
        self.srch_btn.setText("")
