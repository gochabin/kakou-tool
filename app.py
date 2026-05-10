import streamlit as st
import math

st.set_page_config(
    page_title="加工条件計算",
    layout="centered"
)

st.title("加工条件計算システム")

# ------------------------
# 定数
# ------------------------

machine_limit = {
    "Mazak500": 20000,
    "Mazak200": 20000,
    "FANUC": 20000,
    "OKUMA": 20000,
    "DMG MORI": 20000,
    "IWASHITA": 4000
}

tap_table = {
    "M2": (0.4, 1.6),
    "M3": (0.5, 2.5),
    "M4": (0.7, 3.3),
    "M5": (0.8, 4.2),
    "M6": (1.0, 5.0),
    "M8": (1.25, 6.8),
    "M10": (1.5, 8.5),
    "M12": (1.75, 10.2),
    "M14": (2.0, 12.0),
    "M16": (2.0, 14.0)
}

# ------------------------
# 共通
# ------------------------

def limitrpm(v, machine):
    return min(v, machine_limit[machine])

# ------------------------
# 基本設定
# ------------------------

machine = st.selectbox(
    "機械",
    list(machine_limit.keys())
)

material = st.selectbox(
    "材質",
    ["SS400", "S45C", "アルミ"]
)

tool_material = st.selectbox(
    "工具材質",
    ["ハイス", "超硬"]
)

holder = st.selectbox(
    "ホルダー",
    ["コレット", "ミーリングチャック"]
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["ドリル", "エンドミル", "タップ", "面取り"]
)

# =========================================================
# ドリル
# =========================================================

with tab1:

    st.subheader("ドリル条件")

    D = st.number_input(
        "工具径 φ(mm)",
        value=10.0
    )

    dep = st.number_input(
        "穴深さ(mm)",
        value=20.0
    )

    drill_mode = st.selectbox(
        "穴種類",
        ["通し穴", "止まり穴"]
    )

    if st.button("ドリル計算"):

        # ------------------------
        # 切削速度
        # ------------------------

        if tool_material == "超硬":

            if material == "アルミ":
                vc = 120

            elif material == "S45C":
                vc = 50

            else:
                vc = 70

        else:

            if material == "アルミ":
                vc = 60

            elif material == "S45C":
                vc = 20

            else:
                vc = 30

        raw = (1000 * vc) / (3.14 * D)

        rpm = round(limitrpm(raw, machine))

        if drill_mode == "止まり穴":
            rpm = round(rpm * 0.9)

        if holder == "コレット":
            rpm = round(rpm * 0.95)

        feed = round(rpm * 0.15)

        peck = round(
            D * (
                0.8 if drill_mode == "止まり穴"
                else 1.2
            ),
            1
        )

        st.text_area(
            "結果",
            value=
            f"主軸回転数 = {rpm}\n"
            f"送り速度 = {feed}\n"
            f"段切込み量(Q) = {peck}\n"
            f"穴深さ = {dep}",
            height=160
        )

        st.text_area(
            "計算根拠",
            value=
            f"■ 回転数計算\n"
            f"Vc = {vc}\n"
            f"工具径 = φ{D}\n"
            f"回転数 = (1000 × Vc) ÷ (π × D)\n"
            f"       = (1000 × {vc}) ÷ (3.14 × {D})\n"
            f"       = {round(raw)} rpm\n\n"

            f"■ 送り\n"
            f"送り = rpm × 0.15\n"
            f"     = {rpm} × 0.15\n"
            f"     = {feed}\n\n"

            f"■ peck\n"
            f"peck = D × 係数\n"
            f"     = {D} × "
            f"{0.8 if drill_mode=='止まり穴' else 1.2}\n"
            f"     = {peck}",
            height=260
        )

        st.subheader("RPM変更 → F再計算")

        new_rpm = st.number_input(
            "変更後RPM",
            value=int(rpm),
            key="drill_rpm"
        )

        new_feed = round(new_rpm * 0.15)

        st.info(
            f"S{new_rpm} → F{new_feed}"
        )

# =========================================================
# エンドミル
# =========================================================

with tab2:

    st.subheader("エンドミル条件")

    D = st.number_input(
        "工具径 φ(mm)",
        value=10.0,
        key="em_d"
    )

    flutes = st.number_input(
        "刃数",
        value=4
    )

    em_mode = st.selectbox(
        "工程種類",
        [
            "側面荒取り",
            "溝加工",
            "座ぐり",
            "ポケット荒取り",
            "仕上げ輪郭"
        ]
    )

    if st.button("エンドミル計算"):

        mf = {
            "側面荒取り": 1.0,
            "溝加工": 0.7,
            "座ぐり": 0.8,
            "ポケット荒取り": 0.75,
            "仕上げ輪郭": 0.9
        }[em_mode]

        if tool_material == "超硬":
            base = 2500
            feed_base = 300
        else:
            base = 1200
            feed_base = 180

        if material == "アルミ":
            material_rate = 1.5

        elif material == "S45C":
            material_rate = 0.8

        else:
            material_rate = 1.0

        raw = (
            (base / 10)
            * D
            * mf
            * material_rate
        )

        rpm = round(
            limitrpm(raw, machine)
        )

        feed = round(
            (feed_base / 10)
            * D
            * (flutes / 4)
            * mf
            * material_rate
        )

        z = round(D * 0.3 * mf, 1)

        xy = round(D * 0.4 * mf, 1)

        st.text_area(
            "結果",
            value=
            f"主軸回転数 = {rpm}\n"
            f"送り速度 = {feed}\n"
            f"最大Z切込み = {z}\n"
            f"横切込み量 = {xy}",
            height=160
        )

        st.text_area(
            "計算根拠",
            value=
            f"■ 回転数\n"
            f"ベース = {base}\n"
            f"工程係数 = {mf}\n"
            f"材質係数 = {material_rate}\n\n"

            f"回転数 = ({base}÷10)×{D}×{mf}×{material_rate}\n"
            f"       = {round(raw)}\n\n"

            f"■ 送り\n"
            f"送り = ({feed_base}÷10)×{D}×({flutes}÷4)"
            f"×{mf}×{material_rate}\n"
            f"     = {feed}",
            height=260
        )

        st.subheader("RPM変更 → F再計算")

        new_rpm = st.number_input(
            "変更後RPM",
            value=int(rpm),
            key="em_rpm"
        )

        new_feed = round(
            feed * (new_rpm / rpm)
        )

        st.info(
            f"S{new_rpm} → F{new_feed}"
        )

# =========================================================
# タップ
# =========================================================

with tab3:

    st.subheader("タップ条件")

    tap = st.selectbox(
        "タップサイズ",
        list(tap_table.keys())
    )

    if st.button("タップ計算"):

        pitch, under = tap_table[tap]

        rpm = limitrpm(300, machine)

        feed = round(rpm * pitch)

        st.text_area(
            "結果",
            value=
            f"主軸回転数 = {rpm}\n"
            f"同期送り = {feed}\n"
            f"ピッチ = {pitch}\n"
            f"下穴径 = {under}",
            height=180
        )

        st.text_area(
            "計算根拠",
            value=
            f"送り = 回転数 × ピッチ\n"
            f"     = {rpm} × {pitch}\n"
            f"     = {feed}",
            height=180
        )

        st.subheader("RPM変更 → F再計算")

        new_rpm = st.number_input(
            "変更後RPM",
            value=int(rpm),
            key="tap_rpm"
        )

        new_feed = round(
            new_rpm * pitch
        )

        st.info(
            f"S{new_rpm} → F{new_feed}"
        )

# =========================================================
# 面取り
# =========================================================

with tab4:

    st.subheader("面取り条件")

    tool = st.number_input(
        "面取り工具径 φ(mm)",
        value=10.0
    )

    hole = st.number_input(
        "穴径 φ(mm)",
        value=10.0
    )

    c = st.number_input(
        "面取り C寸法",
        value=1.0
    )

    if st.button("面取り計算"):

        finish_dia = round(
            hole + (c * 2),
            3
        )

        z_down = round(c, 3)

        xy_escape = round(c, 3)

        raw = (2000 / 10) * tool

        rpm = round(
            limitrpm(raw, machine)
        )

        feed = round(rpm * 0.12)

        st.text_area(
            "結果",
            value=
            f"主軸回転数 = {rpm}\n"
            f"送り速度 = {feed}\n\n"

            f"■ 穴面取り\n"
            f"穴径 = φ{hole}\n"
            f"面取り = C{c}\n"
            f"完成径 = φ{finish_dia}\n"
            f"必要Z下げ量 = {z_down}\n\n"

            f"■ 外周面取り\n"
            f"Z下げ量 = {z_down}\n"
            f"XY逃がし量 = {xy_escape}",
            height=280
        )

        st.subheader("RPM変更 → F再計算")

        new_rpm = st.number_input(
            "変更後RPM",
            value=int(rpm),
            key="ch_rpm"
        )

        new_feed = round(
            new_rpm * 0.12
        )

        st.info(
            f"S{new_rpm} → F{new_feed}"
        )
