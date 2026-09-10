import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 頁面基本設定
# ------------------------------------------------------------
st.set_page_config(
    page_title="理財小工具",
    page_icon="💰",
    layout="centered",
)

st.sidebar.title("💰 理財小工具")
page = st.sidebar.radio(
    "選擇功能",
    ["個人複利試算器", "基礎匯率換算器"],
)

# ==============================================================
# 功能一：個人複利試算器
# ==============================================================
def compound_interest_calculator():
    st.title("📈 個人複利試算器")
    st.write("輸入本金、年化報酬率與投資年限，計算複利成長趨勢。")

    col1, col2 = st.columns(2)
    with col1:
        principal = st.number_input(
            "本金（元）", min_value=0.0, value=100000.0, step=1000.0, format="%.2f"
        )
        annual_rate = st.number_input(
            "年化報酬率（%）", min_value=-100.0, value=7.0, step=0.1, format="%.2f"
        )
    with col2:
        years = st.number_input(
            "投資年限（年）", min_value=1, value=20, step=1
        )
        monthly_contribution = st.number_input(
            "每月定期投入金額（元，選填）", min_value=0.0, value=0.0, step=500.0, format="%.2f"
        )

    compounding = st.selectbox(
        "複利計算頻率",
        ["每年複利", "每月複利"],
        index=0,
    )

    if st.button("開始試算", type="primary"):
        rate = annual_rate / 100

        years_list = list(range(0, int(years) + 1))
        values = []

        if compounding == "每年複利":
            # 每年計息一次，若有每月定期投入，換算成每年一次性投入的近似值
            annual_contribution = monthly_contribution * 12
            balance = principal
            values.append(balance)
            for _ in years_list[1:]:
                balance = balance * (1 + rate) + annual_contribution
                values.append(balance)
        else:
            # 每月複利
            monthly_rate = rate / 12
            balance = principal
            monthly_balances = [balance]
            total_months = int(years) * 12
            for m in range(1, total_months + 1):
                balance = balance * (1 + monthly_rate) + monthly_contribution
                monthly_balances.append(balance)
            # 取每年年末的數值繪圖
            values = [monthly_balances[m] for m in range(0, total_months + 1, 12)]

        df = pd.DataFrame(
            {"年度": years_list, "資產總額": values}
        ).set_index("年度")

        final_value = values[-1]
        total_invested = principal + monthly_contribution * 12 * years
        total_profit = final_value - total_invested

        st.subheader("試算結果")
        m1, m2, m3 = st.columns(3)
        m1.metric("最終資產總額", f"{final_value:,.0f} 元")
        m2.metric("累計投入本金", f"{total_invested:,.0f} 元")
        m3.metric("累計獲利", f"{total_profit:,.0f} 元")

        st.line_chart(df)

        with st.expander("查看每年明細"):
            st.dataframe(
                df.style.format({"資產總額": "{:,.0f}"}),
                use_container_width=True,
            )

        st.caption(
            "※ 本試算結果僅供參考，實際投資報酬會受市場波動、費用及稅負等因素影響。"
        )


# ==============================================================
# 功能二：基礎匯率換算器
# ==============================================================
# 簡易匯率表（相對於 1 USD 的匯率），使用者可自行調整
DEFAULT_RATES = {
    "USD": 1.0,
    "TWD": 32.0,
    "JPY": 150.0,
    "EUR": 0.92,
    "CNY": 7.2,
    "HKD": 7.8,
    "GBP": 0.79,
    "AUD": 1.5,
    "KRW": 1350.0,
}


def currency_converter():
    st.title("💱 基礎匯率換算器")
    st.write("輸入金額並選擇幣別，即可換算成另一種幣別（可自行調整匯率）。")

    st.info(
        "以下匯率為預設參考值，非即時匯率。若需要精確數字，請自行輸入最新匯率。",
        icon="ℹ️",
    )

    currencies = list(DEFAULT_RATES.keys())

    col1, col2 = st.columns(2)
    with col1:
        from_currency = st.selectbox("從（來源幣別）", currencies, index=currencies.index("TWD"))
        amount = st.number_input("金額", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
    with col2:
        to_currency = st.selectbox("到（目標幣別）", currencies, index=currencies.index("USD"))

    st.markdown("---")
    st.subheader("自訂匯率（相對於 1 USD）")
    st.caption("可依需求修改下列匯率數值，換算會即時套用。")

    rate_cols = st.columns(3)
    custom_rates = {}
    for i, cur in enumerate(currencies):
        with rate_cols[i % 3]:
            custom_rates[cur] = st.number_input(
                f"{cur} / USD",
                min_value=0.0,
                value=DEFAULT_RATES[cur],
                step=0.01,
                format="%.4f",
                key=f"rate_{cur}",
            )

    if st.button("換算", type="primary"):
        if custom_rates[from_currency] == 0:
            st.error("來源幣別匯率不可為 0。")
        else:
            # 先換成 USD，再換成目標幣別
            amount_in_usd = amount / custom_rates[from_currency]
            result = amount_in_usd * custom_rates[to_currency]

            st.success(
                f"{amount:,.2f} {from_currency} ＝ **{result:,.4f} {to_currency}**"
            )

            implied_rate = custom_rates[to_currency] / custom_rates[from_currency]
            st.caption(f"換算匯率：1 {from_currency} ≈ {implied_rate:,.6f} {to_currency}")


# ==============================================================
# 主程式路由
# ==============================================================
if page == "個人複利試算器":
    compound_interest_calculator()
else:
    currency_converter()
