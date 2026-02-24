"""
Component Registry for Visual Builder.

Defines the available components for the drag-and-drop screen builder.
Each component has properties that can be bound to data fields.
"""

import json


COMPONENT_SCHEMA = {
    "leaderboard": {
        "name": "Leaderboard",
        "icon": "leaderboard",
        "category": "Data Display",
        "description": "Ranked list with gold/silver/bronze badges for top performers",
        "properties": {
            "title": {
                "type": "text",
                "label": "Title",
                "default": "Top Performers",
                "description": "Heading text for the leaderboard"
            },
            "dataSource": {
                "type": "data-binding",
                "label": "Data Source",
                "bindingType": "array",
                "description": "Array data field for the rankings"
            },
            "maxItems": {
                "type": "number",
                "label": "Max Items",
                "default": 5,
                "min": 1,
                "max": 20,
                "description": "Maximum number of items to display"
            },
            "showBadges": {
                "type": "boolean",
                "label": "Show Rank Badges",
                "default": True,
                "description": "Show rank number badges"
            },
            "valueFormat": {
                "type": "select",
                "label": "Value Format",
                "options": ["currency", "number", "percentage"],
                "default": "currency",
                "description": "How to format the value"
            }
        }
    },
    "stat-card": {
        "name": "Stat Card",
        "icon": "analytics",
        "category": "Metrics",
        "description": "Single metric display with label and value",
        "properties": {
            "label": {
                "type": "text",
                "label": "Label",
                "default": "Metric",
                "description": "Label text above the value"
            },
            "value": {
                "type": "data-binding",
                "label": "Value",
                "bindingType": "scalar",
                "description": "Data field for the metric value"
            },
            "subtext": {
                "type": "text",
                "label": "Sub Text",
                "default": "",
                "description": "Optional text below the value"
            },
            "variant": {
                "type": "select",
                "label": "Style",
                "options": ["default", "primary", "accent", "success"],
                "default": "default",
                "description": "Color style variant"
            }
        }
    },
    "metrics-grid": {
        "name": "Metrics Grid",
        "icon": "grid_view",
        "category": "Layout",
        "description": "Grid container for multiple stat cards",
        "properties": {
            "columns": {
                "type": "number",
                "label": "Columns",
                "default": 4,
                "min": 1,
                "max": 6,
                "description": "Number of columns in the grid"
            },
            "gap": {
                "type": "text",
                "label": "Gap",
                "default": "1rem",
                "description": "Space between grid items"
            }
        }
    },
    "ticker": {
        "name": "News Ticker",
        "icon": "subtitles",
        "category": "Animation",
        "description": "Scrolling text ticker for announcements",
        "properties": {
            "items": {
                "type": "data-binding",
                "label": "Items",
                "bindingType": "array",
                "description": "Array of text items to scroll"
            },
            "speed": {
                "type": "number",
                "label": "Speed (px/s)",
                "default": 50,
                "min": 10,
                "max": 200,
                "description": "Scroll speed in pixels per second"
            },
            "direction": {
                "type": "select",
                "label": "Direction",
                "options": ["left", "right"],
                "default": "left",
                "description": "Scroll direction"
            }
        }
    }
}


def get_component_registry():
    """Get the full component registry."""
    return COMPONENT_SCHEMA


def get_component_registry_json():
    """Get the component registry as a JSON string."""
    return json.dumps(COMPONENT_SCHEMA)


def get_component(component_type):
    """Get a specific component schema by type."""
    return COMPONENT_SCHEMA.get(component_type)


def get_component_categories():
    """Get unique categories from the registry."""
    categories = set()
    for component in COMPONENT_SCHEMA.values():
        categories.add(component.get('category', 'Other'))
    return sorted(list(categories))
