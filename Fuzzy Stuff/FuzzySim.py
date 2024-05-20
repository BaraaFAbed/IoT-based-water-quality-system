from fuzzylogic import *

# Create input variables and define their membership functions
ph = Domain("PH", 0, 14, 3)
ph["Acidic"] = trapezoid(0, 0, 4, 6)
ph["Neutral"] = trapezoid(5, 6, 8, 9)
ph["Basic"] = trapezoid(8, 10, 14, 14)

tds = Domain("TDS", 0, 2000, 3)
tds["Stale"] = trapezoid(0, 0, 50, 100)
tds["Normal"] = trapezoid(50, 75, 750, 1200)
tds["Salty"] = trapezoid(1000, 1200, 2000, 2000)

turbidity = Domain("Turbidity", 0, 5, 2)
turbidity["Clear"] = trapezoid(0, 0.3, 1, 1.5)
turbidity["Cloudy"] = trapezoid(1, 1.5, 5, 5)

orp = Domain("ORP", -1500, 1500, 2)
orp["Unsuitable"] = trapezoid(-1500, -1500, 0, 200)
orp["Suitable"] = trapezoid(0, 200, 1500, 1500)

# Create output variable and define its membership functions
drinkability = Domain("Drinkability", 0, 100, 3)
drinkability["Safe"] = triangle(0, 0, 33)
drinkability["Semi-safe"] = triangle(33, 49.5, 66)
drinkability["Dangerous"] = triangle(66, 100, 100)

# Create fuzzy rules
rules = [
    Rule(antecedent=(ph["Acidic"], tds["Stale"], turbidity["Clear"], orp["Unsuitable"]), consequent=drinkability["Dangerous"]),
    Rule(antecedent=(ph["Acidic"], tds["Stale"], turbidity["Clear"], orp["Suitable"]), consequent=drinkability["Dangerous"]),
    # Add more rules here based on your provided rules
]

# Create a fuzzy system
system = System(rules)

# Define input values
inputs = {"PH": 7, "TDS": 75, "Turbidity": 1.2, "ORP": 100}

# Perform fuzzy inference
output = system.compute(inputs)

# Defuzzify the result using the "Center of Area" method
defuzzified_output = output.center_of_area()

print("Drinkability:", defuzzified_output)
