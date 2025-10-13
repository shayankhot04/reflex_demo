import pandas as pd
import os
import reflex as rx
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import create_engine

# CSV file path
csv_file = "sample_superstore_render.csv"

# Render Postgres connection string
db_url = os.environ.get("DATABASE_URL")
# "postgresql://sales_sv1k_user:lWYDXUHqVTwMzzJemVcNw9uR3nNxlEQu@dpg-d3mdv5d6ubrc73enh4i0-a.oregon-postgres.render.com/sales_sv1k"

# Create SQLAlchemy engine
engine = create_engine(db_url)

# Read CSV with pandas
df = pd.read_csv(csv_file,encoding='ISO-8859-1')

# Optional: convert OrderDate to datetime
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')

# Optional: convert OrderDate to datetime
df = df.dropna()

# Import into Postgres
df.to_sql('sales', engine, if_exists='replace', index=False)

# print("CSV imported successfully!")

# reading from render postgres database
df_render = pd.read_sql("SELECT * FROM sales", engine)

# APP ------------------------

#-------------------------------------------- Form Template -----------------------------------------------------

df_render['Year'] = df_render['OrderDate'].dt.year


# ---------- Formatting function ----------------------------------------------------------------------------------
def format_number(n):
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return str(round(n, 2))

# ---------- Header Section --------------------------------------------------------------------------------------------
def header() -> rx.Component:
    return rx.box(
        rx.heading(
            "Executive Summary",
            size="7",        # large, prominent text
            color="Black",          # white font color
            font_weight="bold"
        ),
        padding="15px",                # remove default padding to use full height
        bg="light-grey",  # horizontal gradient
        border_radius="lg",         # smooth rounded corners
        width="100%",               # full width
        height="70px",             # increased header height
        display="flex",             # use flex to center content
        align_items="center",       # vertically center the text
        justify_content="center",   # horizontally center the text
        text_align="left"
    )
#---------------Section Title ------------------------------------------------------------------------------------------------
def section_title(text: str, font_size="2xl", color="gray.600",width ="100%") -> rx.Component:
    return rx.text(text,font_size="20px",width = "100%")

#----------------------------Table chart ----------------------------------------------------------------------------

def table_chart(
    dimensions: list,
    measures: dict,
    title: str = "",
    header_bg: str = "#0083b8",
    header_color: str = "white",
    header_size: str = "4"
) -> rx.Component:
    """
    dimensions = list of columns to group by (e.g. ["Region", "Category"])
    measures = dict of {column: agg_func} (e.g. {"Sales": "sum", "Profit": "mean", "OrderID": "nunique"})
    header_bg = column header background color
    header_color = column header text color
    header_size = column header text size (1-10)
    """

    # group and aggregate
    agg_df = df_render.groupby(dimensions).agg(measures).reset_index()

    # format numeric columns
    for col, func in measures.items():
        agg_df[col] = agg_df[col].apply(format_number)

    # Reflex Data Table
    return rx.box(
        rx.vstack(
            rx.text(title, size="4", weight="bold", padding_bottom="0.5rem"),
            rx.divider(width="100%",color ="grey"),
            rx.data_table(
                data=agg_df,
                pagination=True,
                search=True,
                sort=True,
                header_style={
                    "backgroundColor": header_bg,
                    "color": header_color,
                    "fontSize": header_size,  # 1-10 scale
                    "fontWeight": "bold"
                },
            )
        ),
        padding="1rem",
        border_radius="lg",
        box_shadow="md",
        bg="white",
    )


# ---------- Page Layout -------------------------------------------------------------------------------------------------------
@rx.page()
def index() -> rx.Component:
    return rx.vstack(
            header(),
            # Table with custom header styling
            table_chart(
            dimensions=["Category","SubCategory","ProductName"],
            measures={"Sales": "sum","OrderID": "nunique", "Quantity": "sum", "Profit": "sum"},
            title="Product Summary Table",
            header_bg="#0083b8",      # green background
            header_color="#ffffff",   # white text
            header_size="4"           # size from 1 to 10
            ),
            width = "100%",
            bg="linear-gradient(to bottom, #ffffff, #f2f2f2)",
            height = "100%"  

        )
        

# ---------- App Setup ----------
app = rx.App()
app.add_page(index)

