# CO2 savings per kg of e-waste recycled (in kg CO2)
CO2_SAVINGS = {
    "Mobile Phone": 70,
    "Laptop": 300,
    "Desktop Computer": 500,
    "Television": 200,
    "Refrigerator": 150,
    "Washing Machine": 120,
    "Air Conditioner": 180,
    "Printer": 90,
    "Battery": 50,
    "Other": 80,
}

# Average weight per item in kg
ITEM_WEIGHTS = {
    "Mobile Phone": 0.2,
    "Laptop": 2.5,
    "Desktop Computer": 10.0,
    "Television": 15.0,
    "Refrigerator": 60.0,
    "Washing Machine": 70.0,
    "Air Conditioner": 35.0,
    "Printer": 5.0,
    "Battery": 0.5,
    "Other": 2.0,
}

# Recycling value in USD per item
RECYCLE_VALUE = {
    "Mobile Phone": 15,
    "Laptop": 45,
    "Desktop Computer": 30,
    "Television": 20,
    "Refrigerator": 25,
    "Washing Machine": 20,
    "Air Conditioner": 35,
    "Printer": 10,
    "Battery": 5,
    "Other": 8,
}

def calculate_impact(item_type, quantity):
    weight = ITEM_WEIGHTS.get(item_type, 2.0) * quantity
    co2 = CO2_SAVINGS.get(item_type, 80) * weight / 100
    value = RECYCLE_VALUE.get(item_type, 8) * quantity
    trees = round(co2 / 21, 2)  # 1 tree absorbs ~21kg CO2/year
    return {
        "weight_kg": round(weight, 2),
        "co2_saved_kg": round(co2, 2),
        "recycle_value_usd": round(value, 2),
        "trees_equivalent": trees
    }
