from dataclasses import dataclass, field
from PySide6.QtCore import QSize
from typing import List, Dict, Tuple, OrderedDict, Union
from qt_material import list_themes


@dataclass(frozen=True)
class Cfg:
    menu_page_items: List[Dict[str, str]]
    icon_dir: str = "./assets/"
    dflt_th_xml: str = "dark_teal.xml"

    btn_size: QSize = QSize(48, 48)
    icon_size: QSize = QSize(32, 32)
    opt_icon_size: QSize = QSize(48, 48)
    lbl_size: QSize = QSize(144, 48)
    srch_le_min_size: QSize = QSize(200, 48)
    win_min_size: QSize = QSize(1280, 800)

    anime_dur: int = 150
    vis_dly: int = 80

    stg_grp_list: OrderedDict[str, List[Tuple[str, str, Union[List[str], bool]]]] = (
        field(
            default_factory=lambda: OrderedDict(
                [("个性化", [("主题", "主题.png", list_themes())])]
            )
        )
    )
