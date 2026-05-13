import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Kitchen PNL Dashboard",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    return pd.read_excel("Kittchen PNL Data.xlsx")

raw_df = load_data()

# Set first row as header
raw_df.columns = raw_df.iloc[0]

# Remove first row
df = raw_df[1:].reset_index(drop=True)

# Clean column names
df.columns = df.columns.str.strip()


# Main Title
st.markdown(
    """
    <h1 style='text-align: center; font-size: 48px; font-weight: bold;'>
         Kitchen PNL Dashboard
    </h1>

    <p style='text-align: center;
              font-size: 22px;
              font-weight: bold;
              color: #555555;'>
        Interactive Profit & Loss Analysis Dashboard
    </p>
    """,
    unsafe_allow_html=True
)
# FILTERS

left_space, center_container, right_space = st.columns([1, 6, 1])

with center_container:

    filter1, filter2, filter3, filter4,filter5 = st.columns(5)
    
    with filter1:
        month_filter = st.multiselect(
        "Select Month",
        options=df["MONTH"].unique(),
        placeholder="Choose Month"
    )
    with filter2:
        status_filter = st.multiselect(
            "Select Status",
            options=df["STATUS"].unique(),
            placeholder="Choose Status"
        )

    with filter3:
        store_filter = st.multiselect(
            "Select Store",
            options=df["STORE"].unique(),
            placeholder="Choose Stores"
        )

    with filter4:
        city_filter = st.multiselect(
            "Select City",
            options=df["CITY"].unique(),
            placeholder="Choose City"
        )

    with filter5:
        revenue_filter = st.multiselect(
            "Revenue Cohort",
            options=df["REVENUE COHORT"].unique(),
            placeholder="Choose Revenue"
        )




# APPLY FILTERS
filtered_df = df.copy()

if store_filter:
    filtered_df = filtered_df[
        filtered_df["STORE"].isin(store_filter)
    ]

if city_filter:
    filtered_df = filtered_df[
        filtered_df["CITY"].isin(city_filter)
    ]

if revenue_filter:
   filtered_df = filtered_df[
       filtered_df["REVENUE COHORT"].isin(revenue_filter)
    ]
if status_filter:
    filtered_df = filtered_df[
        filtered_df["STATUS"].isin(status_filter)
    ]

if month_filter:
    filtered_df=filtered_df[
        filtered_df["MONTH"].isin(month_filter)
    ]

# Convert numeric columns
filtered_df["NET REVENUE"] = pd.to_numeric(filtered_df["NET REVENUE"])
filtered_df["GROSS MARGIN"] = pd.to_numeric(filtered_df["GROSS MARGIN"])
filtered_df["KITCHEN EBITDA"] = pd.to_numeric(filtered_df["KITCHEN EBITDA"])
filtered_df["VARIANCE"] = pd.to_numeric(filtered_df["VARIANCE"])

# TABS
tab1, tab2 = st.tabs(["Kitchen Level PNL", "Variance Analysis"])


# TAB 1

with tab1:

    # KPI Calculations
    total_revenue = filtered_df["NET REVENUE"].sum()
    total_gm = filtered_df["GROSS MARGIN"].sum()
    total_ebitda = filtered_df["KITCHEN EBITDA"].sum()
    total_stores = filtered_df["STORE"].nunique()

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"₹ {total_revenue/1000000:.1f}M")
    col2.metric("Gross Margin", f"₹ {total_gm/1000000:.1f}M")
    col3.metric("Kitchen EBITDA", f"₹ {total_ebitda/1000000:.1f}M")
    col4.metric("Store Count", total_stores)


    # Top Stores
    top_stores = (
        filtered_df.groupby("STORE")["NET REVENUE"]
        .sum()
        .reset_index()
        .sort_values(by="NET REVENUE", ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        top_stores,
        x="STORE",
        y="NET REVENUE",
        title="Top 10 Stores by Revenue",
        color_discrete_sequence=["#08E4D9"]
    )
    fig2.update_layout(
    title_x=0.5
)
 
    # Monthly Revenue
    monthly_revenue = (
        filtered_df.groupby("MONTH")["NET REVENUE"]
        .sum()
        .reset_index()
    )

    fig3 = px.line(
        monthly_revenue,
        x="MONTH",
        y="NET REVENUE",
        title="Monthly Revenue Trend",
        markers=True,
        color_discrete_sequence=["#059669"]
    )
    fig3.update_layout(
    title_x=0.5
)
    
    # Side by Side Charts
    chart1, chart2 = st.columns(2)

    with chart1:
        st.plotly_chart(fig2, use_container_width=True)

    with chart2:
        st.plotly_chart(fig3, use_container_width=True)

# Table
    st.subheader("Kitchen PNL Data")
    st.dataframe(filtered_df)

    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "Download Filtered Data",
        csv,
        "kitchen_pnl.csv",
        "text/csv"
    )

# TAB 2 ---- Dashboard 2

with tab2:

    # Variance %
    filtered_df["Variance %"] = (
        filtered_df["VARIANCE"] / filtered_df["NET REVENUE"]
    ) * 100

    # Variance Buckets
    filtered_df["Variance Bucket"] = pd.cut(
        filtered_df["Variance %"],
        bins=[-1, 0.5, 1, 2, 5],
        labels=["<0.5%", "0.5%-1%", "1%-2%", ">2%"]
    )

    # Variance Filter
    variance_filter = st.multiselect(
        "Select Variance Bucket",
        options=filtered_df["Variance Bucket"].unique(),
        default=filtered_df["Variance Bucket"].unique()
    )

    # Filtered Variance Data
    variance_df = filtered_df[
        filtered_df["Variance Bucket"].isin(variance_filter)
    ]

    # ==========================
    # VARIANCE KPI CARDS
    # ==========================

    avg_variance = variance_df["Variance %"].mean()

    max_variance = variance_df["Variance %"].max()

    variance_store_count = variance_df["STORE"].nunique()

    high_variance_count = variance_df[
        variance_df["Variance %"] > 1.2
    ]["STORE"].nunique()

    # KPI Cards
    vcol1, vcol2, vcol3, vcol4 = st.columns(4)

    vcol1.metric(
        "Average Variance %",
        f"{avg_variance:.2f}%"
    )

    vcol2.metric(
        "Maximum Variance %",
        f"{max_variance:.2f}%"
    )

    vcol3.metric(
        "Kitchen Count",
        variance_store_count
    )

    vcol4.metric(
        "High Variance Stores",
        high_variance_count
    )

    # ==========================
    # VARIANCE SUMMARY CHART
    # ==========================

    variance_summary = (
        variance_df.groupby("REVENUE COHORT")["Variance %"]
        .mean()
        .reset_index()
    )

    fig4 = px.bar(
        variance_summary,
        x="REVENUE COHORT",
        y="Variance %",
        title="Average Variance by Revenue Cohort",
        color_discrete_sequence=["#88BED6"]
    )

    fig4.update_layout(
        title_x=0.5
    )
    
    # Revenue vs Variance Scatter Plot

    fig5 = px.scatter(
        variance_df,
        x="NET REVENUE",
        y="Variance %",
        hover_name="STORE",
        color="CITY",
        title="Revenue vs Variance Analysis",
        color_discrete_sequence=["#83EBE2"]
    )

    fig5.update_layout(
        title_x=0.5
    )

    vchart1, vchart2 = st.columns(2)

    with vchart1:
        st.plotly_chart(fig4, use_container_width=True)

    with vchart2:
        st.plotly_chart(fig5, use_container_width=True)
    



   

    # ==========================
    # STORE COUNT SUMMARY
    # ==========================

    st.subheader("Kitchen Store Count Summary")

    store_summary = pd.pivot_table(
        variance_df,
        values="STORE",
        index="REVENUE COHORT",
        columns="MONTH",
        aggfunc="count"
    )

    st.dataframe(store_summary)

    # Warning Message
    st.warning(
        "Higher variance percentages may indicate operational inefficiencies or increased food wastage."
    )