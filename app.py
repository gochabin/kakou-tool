import streamlit as st
import math

st.set_page_config(
    page_title="加工条件計算",
    layout="centered"
)

# ----------------------------
# 定数
# ----------------------------
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

# ----------------------------
# 共通
# ----------------------------
def limitrpm(machine, rpm):
    return min(rpm, machine_limit.get(machine, 10000))

st.title("加工条件計算システム")

# ----------------------------
# 上部設定
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    machine = st.selectbox(
        "機械",
        list(machine_limit.keys())
    )

    material = st.selectbox(
        "材質",
        ["SS400", "S45C", "アルミ"]
    )

with col2:
    tool_material = st.selectbox(
        "工具材質",
        ["超硬", "ハイス"]
    )

    holder = st.selectbox(
        "ホルダー",
        ["コレット", "ミーリングチャック"]
    )

# ----------------------------
# タブ
# ----------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["ドリル", "エンドミル", "タップ", "面取り"]
)

# ==================================================
# ドリル
# ==================================================
with tab1:

    st.subheader("ドリル条件")

    D = st.number_input(
        "工具径 φ(mm)",
        value=10.0,
        step=0.1
    )

    depth = st.number_input(
        "穴深さ(mm)",
        value=20.0,
        step=0.1
    )

    drill_mode = st.selectbox(
        "穴種類",
        ["通し穴", "止まり穴"]
    )

    if st.button("ドリル計算"):

        if tool_material == "超硬":
            base = 40000 if material == "アルミ" else 20000
        else:
            base = 18000 if material == "アルミ" else 8000

        raw = base / (D * 3.14)

        if drill_mode == "止まり穴":
            raw *= 0.9

        rpm = round(
            limitrpm(machine, raw)
            * (0.95 if holder == "コレット" else 1)
        )

        feed = round(rpm * 0.15)

        peck = round(
            D * (0.8 if drill_mode == "止まり穴" else 1.2),
            1
        )

        st.success(
            f"""
主軸回転数 = {rpm} rpm

送り速度 = {feed} mm/min

段切込み(Q) = {peck}

穴深さ = {depth}
"""
        )

        with st.expander("計算根拠"):

            st.text(
f"""■ 回転数計算
基準値 = {base}
工具径 = φ{D}

計算式
= 基準値 ÷ (工具径 × π)
= {base} ÷ ({D} × 3.14)
= {round(raw)} rpm

■ 送り計算
送り = 回転数 × 0.15
= {rpm} × 0.15
= {feed} mm/min

■ 段切込み(peck)
peck = 工具径 × 係数
= {D} × {"0.8" if drill_mode=="止まり穴" else "1.2"}
= {peck}
"""
            )

# ==================================================
# エンドミル
# ==================================================
with tab2:

    st.subheader("エンドミル条件")

    D = st.number_input(
        "工具径 φ(mm)",
        value=10.0,
        step=0.1,
        key="em_d"
    )

    flutes = st.number_input(
        "刃数",
        value=4,
        step=1
    )

    em_mode = st.selectbox(
        "工程種類",
        ["側面荒取り", "溝加工", "座ぐり", "ポケット荒取り", "仕上げ輪郭"]
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

        raw = (base / 10) * D * mf * material_rate

        rpm = int(limitrpm(machine, raw))

        feed = round(
            (feed_base / 10)
            * D
            * (flutes / 4)
            * mf
            * material_rate
        )

        z = round(D * 0.3 * mf, 1)
        xy = round(D * 0.4 * mf, 1)

        st.success(
            f"""
主軸回転数 = {rpm} rpm

送り速度 = {feed} mm/min

最大Z切込み = {z}

横切込み量 = {xy}
"""
        )

        with st.expander("計算根拠"):

            st.text(
f"""■ 回転数計算
工具材質ベース = {base}
工程係数 = {mf}
材質係数 = {material_rate}

回転数
= ({base} ÷ 10) × {D} × {mf} × {material_rate}
= {round(raw)} rpm

■ 送り計算
送りベース = {feed_base}

送り
= ({feed_base} ÷ 10)
× {D}
× ({flutes} ÷ 4)
× {mf}
× {material_rate}

= {feed} mm/min

■ 切込み
Z切込み = {z}
横切込み = {xy}
"""
            )

# ==================================================
# タップ
# ==================================================
with tab3:

    st.subheader("タップ条件")

    tap = st.selectbox(
        "タップサイズ",
        list(tap_table.keys())
    )

    if st.button("タップ計算"):

        pitch, under = tap_table[tap]

        rpm = limitrpm(machine, 300)

        feed = round(rpm * pitch)

        st.success(
            f"""
主軸回転数 = {rpm} rpm

同期送り = {feed} mm/min

ピッチ = {pitch}

下穴径 = {under}
"""
        )

        with st.expander("計算根拠"):

            st.text(
f"""■ タップ計算

ピッチ = {pitch}

回転数 = {rpm}

同期送り
= 回転数 × ピッチ
= {rpm} × {pitch}
= {feed} mm/min

下穴径 = {under}
"""
            )

# ==================================================
# 面取り
# ==================================================
with tab4:

    st.subheader("面取り条件")

    c = st.number_input(
        "C寸法(mm)",
        value=1.0,
        step=0.1
    )

    tool = st.number_input(
        "面取り工具径(mm)",
        value=8.0,
        step=0.1
    )

    if st.button("面取り計算"):

        contact = round(c * 2, 2)

        raw = (2000 / 10) * contact

        rpm = round(limitrpm(machine, raw))

        feed = round(rpm * 0.12)

        z_down = round(c, 2)
        move_xy = round(c, 2)

        st.success(
            f"""
主軸回転数 = {rpm} rpm

送り速度 = {feed} mm/min

Z下げ量 = {z_down}

XY移動量 = {move_xy}

実接触径 = {contact}
"""
        )

        with st.expander("計算根拠"):

            st.text(
f"""■ 面取り計算

C寸法 = {c}

実接触径
= C寸法 × 2
= {contact}

回転数
= (2000 ÷ 10) × {contact}
= {round(raw)} rpm

送り
= {rpm} × 0.12
= {feed} mm/min

■ 加工イメージ

Z方向に {z_down} 下げる
XY方向に {move_xy} 移動
"""
            )
