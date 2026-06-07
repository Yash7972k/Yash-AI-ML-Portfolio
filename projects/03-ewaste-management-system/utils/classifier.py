import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import os

PRIORITY_RULES = {
    "Mobile Phone": "High",
    "Laptop": "High",
    "Battery": "High",
    "Desktop Computer": "Medium",
    "Printer": "Medium",
    "Television": "Medium",
    "Air Conditioner": "Low",
    "Refrigerator": "Low",
    "Washing Machine": "Low",
    "Other": "Low",
}

HAZARD_LEVEL = {
    "Mobile Phone": "High",
    "Laptop": "High",
    "Battery": "Critical",
    "Desktop Computer": "Medium",
    "Printer": "Medium",
    "Television": "Medium",
    "Air Conditioner": "Low",
    "Refrigerator": "Low",
    "Washing Machine": "Low",
    "Other": "Low",
}

RECYCLING_TIPS = {
    "Mobile Phone": "Contains lithium batteries and rare earth metals. Must be handled by certified recyclers.",
    "Laptop": "Contains lead, mercury, and cadmium. Separate battery before recycling.",
    "Battery": "Highly toxic. Never dispose in regular trash. Drop at certified collection point immediately.",
    "Desktop Computer": "Contains circuit boards with gold and copper. Shred and separate components.",
    "Printer": "Remove ink cartridges separately. Contains plastic and metal parts.",
    "Television": "Old CRT TVs contain lead. LED TVs have recyclable panels.",
    "Air Conditioner": "Refrigerant must be extracted by certified technician before recycling.",
    "Refrigerator": "Contains refrigerants and compressor oil. Requires special handling.",
    "Washing Machine": "Mostly metal — high recycling value. Drain water before pickup.",
    "Other": "Sort by material type (plastic, metal, glass) before recycling.",
}

def classify_item(item_type, quantity, condition):
    priority = PRIORITY_RULES.get(item_type, "Low")
    if quantity > 5:
        priority = "High"
    if condition == "Broken/Non-functional":
        priority = "High"
    hazard = HAZARD_LEVEL.get(item_type, "Low")
    tip = RECYCLING_TIPS.get(item_type, "Follow standard e-waste disposal guidelines.")
    return {
        "priority": priority,
        "hazard_level": hazard,
        "recycling_tip": tip
    }
