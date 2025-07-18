"""
Nem-dash Tab - Primary Dashboard View
Combines price section, renewable energy gauge, and 24-hour generation overview
"""

import panel as pn
from ..shared.logging_config import get_logger
from .price_components import create_price_section
from .renewable_gauge import create_renewable_gauge_component
from .generation_overview import create_generation_overview_component

# Custom CSS to remove chart borders
CUSTOM_CSS = """
.chart-no-border .bk-root {
    border: none !important;
    outline: none !important;
}

.chart-no-border .bk {
    border: none !important;
    outline: none !important;
}

.chart-no-border {
    border: none !important;
    outline: none !important;
}
"""

logger = get_logger(__name__)


def create_nem_dash_tab(dashboard_instance=None):
    """
    Create the complete Nem-dash tab layout
    
    Args:
        dashboard_instance: Reference to main dashboard for data sharing
        
    Returns:
        Panel component containing the complete Nem-dash layout
    """
    try:
        logger.info("Creating Nem-dash tab components")
        
        # Create individual components
        price_section = create_price_section()
        renewable_gauge = create_renewable_gauge_component(dashboard_instance)
        generation_overview = create_generation_overview_component(dashboard_instance)
        
        # Create the layout with new arrangement:
        # Top row: Generation chart (left) + Price section (right)
        # Bottom: Gauge (centered or left-aligned)
        layout = pn.Column(
            # Top row: Generation chart (left) + Price section (right)
            pn.Row(
                generation_overview,    # ~800px width, 400px height
                price_section,          # ~450px width
                sizing_mode='stretch_width',
                margin=(5, 5)
            ),
            # Bottom row: Renewable gauge
            pn.Row(
                renewable_gauge,        # ~400px width, 350px height
                sizing_mode='stretch_width',
                margin=(5, 5)
            ),
            sizing_mode='stretch_width',
            margin=(10, 10),
            name="Nem-dash",  # Tab name
            stylesheets=[CUSTOM_CSS]  # Apply custom CSS
        )
        
        logger.info("Nem-dash tab created successfully")
        return layout
        
    except Exception as e:
        logger.error(f"Error creating Nem-dash tab: {e}")
        # Return error fallback
        return pn.Column(
            pn.pane.HTML(
                f"<div style='padding:20px;text-align:center;'>"
                f"<h2>Error Loading Nem-dash</h2>"
                f"<p>Error: {e}</p>"
                f"<p>Please check the logs and try refreshing.</p>"
                f"</div>"
            ),
            name="Nem-dash",
            sizing_mode='stretch_width',
            height=600
        )


def create_nem_dash_tab_with_updates(dashboard_instance=None, auto_update=True):
    """
    Create Nem-dash tab with auto-update functionality
    
    Args:
        dashboard_instance: Reference to main dashboard for data sharing
        auto_update: Whether to enable auto-updates (default True)
        
    Returns:
        Panel component with auto-update capability
    """
    try:
        # Create the basic tab
        tab = create_nem_dash_tab(dashboard_instance)
        
        if auto_update:
            def update_all_components():
                """Update all components in the tab"""
                try:
                    logger.info("Updating Nem-dash tab components")
                    
                    # Get the current components
                    top_row = tab[0]  # Row with generation chart and price section
                    bottom_row = tab[1]  # Row with gauge
                    
                    # Update generation overview
                    new_overview = create_generation_overview_component(dashboard_instance)
                    top_row[0] = new_overview
                    
                    # Update price section
                    new_price_section = create_price_section()
                    top_row[1] = new_price_section
                    
                    # Update renewable gauge
                    new_gauge = create_renewable_gauge_component(dashboard_instance)
                    bottom_row[0] = new_gauge
                    
                    logger.info("Nem-dash tab components updated successfully")
                    
                except Exception as e:
                    logger.error(f"Error updating Nem-dash components: {e}")
            
            # Set up periodic updates (every 4.5 minutes = 270000ms)
            pn.state.add_periodic_callback(update_all_components, 270000)
            logger.info("Auto-update enabled for Nem-dash tab (4.5 minute intervals)")
        
        return tab
        
    except Exception as e:
        logger.error(f"Error creating Nem-dash tab with updates: {e}")
        return create_nem_dash_tab(dashboard_instance)


if __name__ == "__main__":
    # Test the complete Nem-dash tab
    pn.extension(['bokeh', 'plotly'])
    
    # Create test tab
    tab = create_nem_dash_tab()
    
    # Create a simple app to test
    template = pn.template.MaterialTemplate(
        title="Nem-dash Test",
        sidebar=[],
        main=[tab]
    )
    
    template.show(port=5555)