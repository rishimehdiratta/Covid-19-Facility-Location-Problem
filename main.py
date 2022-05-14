import pandas as pd
import pulp as pl
import math
import random

def covid_model():
    data = pd.read_csv(r"C:\Users\Rishi Mehdiratta\Desktop\Book2.csv")

    countries = list(data.loc[0:8, "Centroid"])
    coordinate_country = list(data.loc[0:8, "Coordinates_c"])
    coordinate_country_dict = {}
    for c in countries:
        coordinate_country_dict.update({c: coordinate_country[countries.index(c)]})
    print(coordinate_country_dict)

    facilities = list(data.loc[0:23, "facility"])
    coordinate_facility = list(data.loc[0:23, "Coordinates_f"])
    coordinate_facility_dict = {}
    for f in facilities:
        coordinate_facility_dict.update({f: coordinate_facility[facilities.index(f)]})
    print(coordinate_facility_dict)

    country_demand = list(data.loc[0:8, "Demand"])
    country_demand_dict = {}
    for c in countries:
        country_demand_dict.update({c: country_demand[countries.index(c)]})
    for c in countries:
        country_demand_dict[c] =  1.2 * country_demand_dict[c]
    coordinate_facility = list(data.loc[0:22, "Coordinates_f"])

    facility_capacity = list(data.loc[0:23, "Capacity"])
    capacity_dict = {}
    for f in facilities:
        capacity_dict.update({f: facility_capacity[facilities.index(f)]})
    print(capacity_dict)

    temp_facility = facilities[14:23]
    existing_facility = facilities[0:15]
    print(existing_facility)

    distance = {}
    for country in countries:
        for facility in facilities:
            distance.update({(country, facility): math.dist(eval(coordinate_country_dict[country]),
                                                            eval(coordinate_facility_dict[facility]))})
    print(distance)

    temporary_cost = 500000
    bigM = random.randrange(2000000)
    dCost = 5

    # dv-1
    temp_building = {}
    for t in temp_facility:
        temp_building.update({t: pl.LpVariable("temporary_" + str(t), cat="Binary")})
    print(temp_building)

    # dv-2
    Number_of_patients = {}
    for c in countries:
        for f in facilities:
            Number_of_patients.update(
                {(c, f): pl.LpVariable("Num_" + str(c) + "_" + str(f), cat="Continuous", lowBound=0)})
    print(Number_of_patients)

    # dv-3
    extra_capacity = {}
    for t in temp_facility:
        extra_capacity.update({t: pl.LpVariable("Z_" + str(t), cat="Continuous", lowBound=0)})
    print(extra_capacity)


    prob = pl.LpProblem("Covid-19-Facility-Location-Problem", pl.LpMinimize)

    aux_sum1 = 0
    for c in countries:
        for f in facilities:
            aux_sum1 += (dCost * Number_of_patients[c, f] * distance[c, f])
    aux_sum2 = 0
    for t in temp_facility:
        aux_sum2 += temp_building[t]
    aux_sum3 = aux_sum2 * temporary_cost
    aux_sum4 = 0
    for t in temp_facility:
        aux_sum4 += extra_capacity[t]
    aux_sum11 = bigM * aux_sum4
    aux_sum = aux_sum1 + aux_sum3 + aux_sum11
    prob += aux_sum



    #printing problem
    print(prob)
    # constraint1
    # satisfy demand of every patients of countries
    for c in countries:
        aux_sum5 = 0
        for f in facilities:
            aux_sum5 += Number_of_patients[c, f]
        prob += aux_sum5 == country_demand_dict[c]

    # constraint2
    # total patients coming to existing facilities should not exceed the capacity

    for e in existing_facility:
        aux_sum6 = 0
        for c in countries:
            aux_sum6 += Number_of_patients[c, e]
        prob += aux_sum6 <= capacity_dict[e]

    # constraint3
    # capacity of temp facility cannot be exceeded.Extra capacity can be added

    for t in temp_facility:
        aux_sum7 = 0
        for c in countries:
            aux_sum7 += Number_of_patients[c, t]
        prob += aux_sum7 <= capacity_dict[t] * temp_building[t] + extra_capacity[t]

    #print(prob)
    prob.writeLP("Covid_19_Problem.lp")
    prob.solve()

    print("______________________________________________________________________________________________________________")

    print(f"Cost of building temporary facility = {aux_sum3.value()}")
    print(f"Allocation cost of allocating patients to existing facility = {aux_sum1.value()}")
    print("___________________________plan for temporary facility_________________________________")
    for t in temp_facility:
        if (temp_building[t].value() > 0.0):
            print(f"build temporary {t}")
    print("___________________________Covid-19 Patients Assignment Plan____________________________")
    for f in facilities:
        sum = 0
        for c in countries:
            if Number_of_patients[c, f].value() > 0.0:
                print(f"{Number_of_patients[c, f].value()} patients from {c} are assigned to {f}")
                sum += Number_of_patients[c, f].value()
        print("")
        print(f"{sum} TOTAL PATIENTS FROM {c} ARE ASSIGNED TO {f}")
        print("__________________________________________________________________________")

covid_model()

