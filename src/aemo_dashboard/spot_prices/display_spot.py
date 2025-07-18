import pandas as pd
import panel as pn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import matplotx
import numpy as np
import os
import sys

from ..shared.config import config
from ..shared.logging_config import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger(__name__)

pn.extension()
file_path = str(config.spot_hist_file)
font_size = 10
logger.info("Display spot dashboard starting...")

# Function to open the parquet file with robust error handling
def open_parquet_file(path):
    logger.info(f"path {path}")
    
    # Try multiple approaches to load the parquet file
    for attempt, method in enumerate([
        # Method 1: Standard pandas read_parquet
        lambda: pd.read_parquet(path),
        # Method 2: Read with specific engine
        lambda: pd.read_parquet(path, engine='pyarrow'),
        # Method 3: Try with fastparquet engine if available
        lambda: pd.read_parquet(path, engine='fastparquet'),
        # Method 4: Last resort, try reading from backup pickle if it exists
        lambda: pd.read_pickle(path.replace('.parquet', '_backup.pkl')) if os.path.exists(path.replace('.parquet', '_backup.pkl')) else None
    ]):
        try:
            logger.info(f"Attempt {attempt+1} to open parquet file")
            result = method()
            if result is not None:
                logger.info(f"Successfully loaded data using method {attempt+1}")
                # Ensure the index is properly set as datetime if it isn't already
                if not isinstance(result.index, pd.DatetimeIndex):
                    if 'SETTLEMENTDATE' in result.columns:
                        result = result.set_index('SETTLEMENTDATE')
                    else:
                        # Try to convert index to datetime if it's not already
                        try:
                            result.index = pd.to_datetime(result.index)
                        except:
                            pass
                return result
        except Exception as e:
            logger.info(f"Method {attempt+1} failed with error: {str(e)}")
            continue
    
    # If all methods fail, raise a more descriptive error
    raise ValueError(f"Failed to load parquet file {path}. The file may not exist or be corrupted. Make sure you've run the conversion script first.")

# itk teal style for data frame doesn't print the borders properly in vscode but does in jupyter
styles = [
    dict(selector="caption",
         props=[("text-align", "left"),
                ("font-size", "150%"),
                ("color", 'white'),
                ("background-color", "teal"),  # Teal background for caption
                ("caption-side", "top")]),
    dict(selector="",
         props=[("color", "#f8f8f2"),  # Light text color
                ("background-color", "#282a36"),  # Dark background
                ("border-bottom", "1px dotted #6272a4")]),  # Dracula accent color
    dict(selector="th",
         props=[("background-color", "#44475a"),  # Slightly darker background for headers
                ("border-bottom", "1px dotted #6272a4"),
                ("font-size", "14px"),
                ("color", "#f8f8f2")]),  # Light text color
    dict(selector="tr",
         props=[("background-color", "#282a36"),  # Dark background for rows
                ("border-bottom", "1px dotted #6272a4"),
                ("color", "#f8f8f2")]),  # Light text color
    dict(selector="td",
         props=[("font-size", "14px")]),
    dict(selector="th.col_heading",
         props=[("color", "black"),
                ("font-size", "110%"),
                ("background-color", "#00DCDC")]),  # #00DCDC background for column headings
    dict(selector="tr:last-child",
         props=[("color", "#f8f8f2"),
                ("border-bottom", "5px solid #6272a4")]),  # Accent color for the last row
    dict(selector=".row_heading",
         props=[("background-color", "#282a36"),  # Same background as the rest of the table
                ("border-bottom", "1px dotted #6272a4"),
                ("color", "#f8f8f2"),  # Light text color for row headings
                ("font-size", "14px")]),
    dict(selector="thead th:first-child",
         props=[("background-color", "#00DCDC"),  # #00DCDC background for the index cell of the column headings row
                ("color", "black")])  # Dark text color for the index cell of the column headings row
]

def display_table(prices):
    display = prices.copy()
    display.index = display.index.strftime('%H:%M')

    display.loc["Last hour average"] = display.tail(12).mean()
    display.loc["Last 24 hr average"] = display.tail(24*12).mean()
    display.rename_axis(None, inplace=True)
    display.rename_axis(None, axis=1, inplace=True)
    return (display.tail(7)
        .style
        .format('{:,.0f}')
        .set_caption("5 minute spot $/MWh " + prices.index[-1].strftime("%d %b %H:%M"))
        .set_table_styles(styles)
        .apply(lambda x: ['font-weight: bold' if x.name in display.tail(3).index else '' for _ in x], axis=1)
        .apply(lambda x: ['color: #e0e0e0' if x.name not in display.tail(3).index else '' for _ in x], axis=1))

dracula_style = {
    "axes.facecolor": "#282a36",
    "axes.edgecolor": "#44475a",
    "axes.labelcolor": "#f8f8f2",
    "figure.facecolor": "#282a36",
    "grid.color": "#6272a4",
    "text.color": "#f8f8f2",
    "xtick.color": "#f8f8f2",
    "ytick.color": "#f8f8f2",
    "axes.prop_cycle": plt.cycler("color", ["#8be9fd", "#ff79c6", "#50fa7b", "#ffb86c", "#bd93f9", "#ff5555", "#f1fa8c"])
}

def get_data():
    data = open_parquet_file(file_path)
    logger.info("file opened")
    prices = data.pivot(columns='REGIONID', values='RRP')
    logger.info("REGIONID                NSW1")
    logger.info("SETTLEMENTDATE")
    logger.info(prices.tail(5))
    return prices

def pcht(prices):
    logger.info("pchart called")
    
    # Count consecutive valid points from the end for each column
    valid_counts = {}
    for col in prices.columns:
        series = prices[col]
        # Start from the end and count until we hit a NaN
        count = 0
        for i in range(len(series)-1, -1, -1):  # Go backwards through the series
            if pd.isna(series.iloc[i]):
                break
            count += 1
        valid_counts[col] = count
        logger.info(f"Column {col} has {count} consecutive valid points from the end")
    
    min_valid_points = min(valid_counts.values())
    logger.info(f"Using minimum valid points across all columns: {min_valid_points}")
    
    # Take last min(120, min_valid_points) rows
    rows_to_take = min(120, min_valid_points)
    
    # Calculate EWM only on the rows we'll use
    df1 = prices.tail(rows_to_take).ewm(alpha=0.22, adjust=False).mean()
    df = df1.copy()
    
    fig, ax = plt.subplots()
    fig.set_size_inches(4.5, 2.5)
    plt.rcParams.update(dracula_style)
    when = prices.index[-1].strftime("%d %b %H:%M")
    
    for col in df.columns:
        line, = ax.plot(df[col])
        last_value = df.at[df.index[-1], col]
        if pd.isna(last_value):
            line.set_label(f"{col}: N/A")
        else:
            line.set_label(f"{col}: ${last_value:.0f}")
    
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylabel("$/MWh")
    
    plt.title(f"Smoothed 5 minute prices as at {when} ({rows_to_take} points)", fontsize=10)
    
    ax.tick_params(axis='both', which='major', labelsize=7)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.axhline(0, color='white', linewidth=0.3)
    plt.figtext(0.97, 0.0, "©ITK", fontsize=7, horizontalalignment="right")
    ax.legend(fontsize=7)
    legend = ax.legend(fontsize=7, frameon=False)
    plt.close()
    return fig

# Function to update the plot
def update_plot(event=None):
    prices = get_data()
    fig = pcht(prices)
    mpl_pane.object = fig
    table_pane.object = display_table(prices)

def create_app():
    """Create the dashboard app"""
    logger.info("Creating spot price dashboard app...")
    
    # Create an initial plot
    prices = get_data()
    fig = pcht(prices)
    table = display_table(prices)
    mpl_pane = pn.pane.Matplotlib(fig, sizing_mode='stretch_both')
    table_pane = pn.pane.DataFrame(table, sizing_mode='stretch_both')

    # Layout for the Panel
    layout = pn.Column(table_pane, mpl_pane, max_width=450, max_height=630)
    
    return layout

def main():
    """Main function to run the dashboard"""
    logger.info("Starting spot price dashboard...")
    
    # Create the app factory function that sets up callbacks inside the server context
    def app_factory():
        app = create_app()
        # Set up periodic callback inside the server context
        pn.state.add_periodic_callback(update_plot, 270000)  # 270000ms = 4.5 minutes
        return app
    
    # Serve with specific port using the app factory
    pn.serve(app_factory, port=5007, show=True, autoreload=False)

if __name__ == "__main__":
    main()