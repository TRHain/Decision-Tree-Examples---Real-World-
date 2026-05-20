import urllib.parse

def yes_no(question):
    while True:
        answer = input(question + " (yes/no): ").strip().lower()
        if answer in ["yes", "y"]:
            return True
        elif answer in ["no", "n"]:
            return False
        else:
            print("Please enter yes or no.")

def get_float(question):
    while True:
        try:
            return float(input(question + ": ").strip())
        except ValueError:
            print("Please enter a number.")

def get_address(question):
    while True:
        address = input(question + ": ").strip()
        if address:
            return address
        print("Address cannot be empty.")

def make_map_links(start, destination):
    encoded_start = urllib.parse.quote(start)
    encoded_destination = urllib.parse.quote(destination)

    google_maps = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={encoded_start}"
        f"&destination={encoded_destination}"
    )

    transit_maps = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={encoded_start}"
        f"&destination={encoded_destination}"
        f"&travelmode=transit"
    )

    walking_maps = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={encoded_start}"
        f"&destination={encoded_destination}"
        f"&travelmode=walking"
    )

    biking_maps = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={encoded_start}"
        f"&destination={encoded_destination}"
        f"&travelmode=bicycling"
    )

    uber_link = (
        f"https://m.uber.com/ul/?action=setPickup"
        f"&pickup[formatted_address]={encoded_start}"
        f"&dropoff[formatted_address]={encoded_destination}"
    )

    return {
        "Google Maps": google_maps,
        "Transit / Bus / Subway": transit_maps,
        "Walking": walking_maps,
        "Biking": biking_maps,
        "Uber": uber_link
    }

def choose_transport(data):
    reasons = []

    # 1. Safety first
    if data["weather_bad"]:
        reasons.append("Weather is bad, so walking and biking become less safe.")
        if data["has_car"]:
            return "Drive", reasons
        if data["uber_available"] and data["budget"] >= data["estimated_uber_cost"]:
            return "Uber", reasons
        if data["bus_available"] or data["subway_available"]:
            return "Transit", reasons
        return "Delay trip or find a ride", reasons

    # 2. Accessibility / physical limits
    if data["mobility_issue"]:
        reasons.append("Mobility or comfort is a concern, so low-effort travel matters.")
        if data["has_car"]:
            return "Drive", reasons
        if data["uber_available"] and data["budget"] >= data["estimated_uber_cost"]:
            return "Uber", reasons
        if data["bus_available"] or data["subway_available"]:
            return "Transit", reasons
        return "Find a ride", reasons

    # 3. Heavy items
    if data["carrying_heavy_items"]:
        reasons.append("You are carrying heavy items, so walking or biking is a pain.")
        if data["has_car"]:
            return "Drive", reasons
        if data["uber_available"] and data["budget"] >= data["estimated_uber_cost"]:
            return "Uber", reasons
        if data["bus_available"] or data["subway_available"]:
            return "Transit", reasons

    # 4. Running late
    if data["running_late"]:
        reasons.append("You are running late, so speed matters more than cost.")
        if data["has_car"]:
            return "Drive", reasons
        if data["uber_available"] and data["budget"] >= data["estimated_uber_cost"]:
            return "Uber", reasons
        if data["subway_available"]:
            return "Subway", reasons
        if data["bus_available"]:
            return "Bus", reasons

    # 5. Distance
    if data["distance_miles"] <= 1:
        reasons.append("The trip is very short.")
        return "Walk", reasons

    if data["distance_miles"] <= 5:
        reasons.append("The trip is a reasonable bike distance.")
        if data["has_bike"]:
            return "Bike", reasons
        if data["bus_available"] or data["subway_available"]:
            return "Transit", reasons
        if data["has_car"]:
            return "Drive", reasons

    # 6. Budget
    if data["budget"] < data["estimated_uber_cost"]:
        reasons.append("Uber is over budget, so cheaper options come first.")
        if data["subway_available"]:
            return "Subway", reasons
        if data["bus_available"]:
            return "Bus", reasons
        if data["has_car"]:
            return "Drive", reasons

    # 7. Default best option
    reasons.append("No major blockers found, so convenience wins.")
    if data["subway_available"]:
        return "Subway", reasons
    if data["bus_available"]:
        return "Bus", reasons
    if data["uber_available"]:
        return "Uber", reasons
    if data["has_car"]:
        return "Drive", reasons
    if data["has_bike"]:
        return "Bike", reasons

    return "Walk", reasons

def main():
    print("\nTransportation Decision Tree")
    print("----------------------------")

    start = get_address("Enter your starting address")
    destination = get_address("Enter your destination address")

    print("\nTrip Details")
    distance_miles = get_float("Estimated distance in miles")
    budget = get_float("Maximum amount you want to spend")
    estimated_uber_cost = get_float("Estimated Uber cost")

    print("\nConditions")
    weather_bad = yes_no("Is the weather bad?")
    running_late = yes_no("Are you running late?")
    carrying_heavy_items = yes_no("Are you carrying heavy items?")
    mobility_issue = yes_no("Do you have any mobility, pain, or comfort concerns?")

    print("\nAvailable Options")
    has_car = yes_no("Do you have access to a car?")
    has_bike = yes_no("Do you have access to a bike?")
    bus_available = yes_no("Is a bus route available?")
    subway_available = yes_no("Is a subway/train route available?")
    uber_available = yes_no("Is Uber available?")

    data = {
        "start": start,
        "destination": destination,
        "distance_miles": distance_miles,
        "budget": budget,
        "estimated_uber_cost": estimated_uber_cost,
        "weather_bad": weather_bad,
        "running_late": running_late,
        "carrying_heavy_items": carrying_heavy_items,
        "mobility_issue": mobility_issue,
        "has_car": has_car,
        "has_bike": has_bike,
        "bus_available": bus_available,
        "subway_available": subway_available,
        "uber_available": uber_available
    }

    recommendation, reasons = choose_transport(data)
    links = make_map_links(start, destination)

    print("\nRecommendation")
    print("--------------")
    print(f"Best option: {recommendation}")

    print("\nWhy:")
    for reason in reasons:
        print(f"- {reason}")

    print("\nMap / Route Links")
    print("-----------------")
    for name, link in links.items():
        print(f"{name}: {link}")

    print("\nWhy order matters:")
    print("The program checks safety first, then physical needs, then heavy items, then time, then distance, then budget.")
    print("That matters because you should not recommend biking just because it is cheap if the weather is dangerous or the user is carrying a bunch of gear.")

if __name__ == "__main__":
    main()