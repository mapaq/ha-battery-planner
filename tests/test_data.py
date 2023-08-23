"""Test data"""

short_price_series_with_1_cycle = {
    "import": [3.0, 2.0, 4.0, 4.0],
    "export": [1.0, 1.0, 3.0, 1.0],
    "yield": 1.0,
    "plan": [0, -1000, 1000, 0],
}

short_price_series_with_one_cycle_battery_charged_1 = {
    "import": [3.0, 2.0, 4.0, 4.0],
    "export": [1.0, 1.0, 3.0, 1.0],
    "yield": [2.0],
    "plan": [0, 0, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [1.0],
}

short_price_series_with_one_cycle_battery_charged_2 = {
    "import": [5.0, 2.0, 4.0, 4.0],
    "export": [4.0, 1.0, 3.0, 1.0],
    "yield": [4.0],
    "plan": [1000, -1000, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [1.0],
}

short_price_series_with_one_cycle_battery_charged_3 = {
    "import": [5.0, 2.0, 6.0, 4.0],
    "export": [4.0, 1.0, 5.0, 1.0],
    "yield": [1.0],
    "plan": [0, 0, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [4.0],
}

short_price_series_with_2_cycles = {
    "import": [3.0, 2.0, 4.0, 1.0, 5.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0],
    "yield": 4.0,
    "plan": [0, -1000, 1000, -1000, 1000],
}

short_price_series_with_consecutive_charge = {
    "import": [3.0, 2.0, 1.0, 3.0, 5.0, 6.0, 2.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0, 5.0, 1.0],
    "yield": 6.0,
    "plan": [0, -1000, -1000, 0, 1000, 1000, 0],
}

short_price_series_with_3_cycles = {
    "import": [
        97.58,  # 1
        165.69,
        186.5,  # 1  110.24 - 97.58 = 12.66
        183.57,
        80.1,
        71.98,  # 2
        97.79,
        166.61,  # 2  94.33 - 71.98 = 22.35
        93.67,  # 3
        94.09,
        205.3,  # 3  125.28 - 93.67 = 31.61
    ],
    "export": [
        39.1,  # 1
        93.59,
        110.24,  # 1
        107.9,
        25.12,
        18.62,  # 2
        39.27,
        94.33,  # 2
        35.98,  # 3
        36.31,
        125.28,  # 3
    ],
    "yield": 66.62,  # 12.66 + 22.35 + 31.61 = 66.62
    "plan": [
        -1000,  # 1
        0,
        1000,  # 1
        0,
        0,
        -1000,  # 2
        0,
        1000,  # 2
        -1000,  # 3
        0,
        1000,  # 3
    ],
}

long_price_series_with_3_cycles = {
    "import": [
        194.22,
        153.04,
        145.39,
        162.59,
        167.08,
        191.09,
        212.21,
        223.19,
        206.66,
        194.24,
        179.6,
        158.94,
        141.24,
        114.38,
        101.75,
        97.58,  # 1
        107.04,
        142.01,
        165.69,
        186.5,  # 1
        183.57,
        175.55,
        160.64,
        101.36,
        78.12,
        80.1,
        71.98,  # 2
        75.42,
        77.71,
        78.49,
        88.99,
        97.79,
        166.61,  # 2
        150.12,
        126.56,
        111.45,
        106.1,
        99.21,
        93.67,  # 3
        94.09,
        105.29,
        120.04,
        173.78,
        190.46,
        204.99,
        205.3,  # 3
        182.8,
        141.91,
    ],
    "export": [
        116.42,
        83.47,
        77.35,
        91.11,
        94.7,
        113.91,
        130.81,
        139.59,
        126.37,
        116.43,
        104.72,
        88.19,
        74.03,
        52.54,
        42.44,
        39.1,  # 1
        46.67,
        74.65,
        93.59,
        110.24,  # 1
        107.9,
        101.48,
        89.55,
        42.13,
        23.54,
        25.12,
        18.62,  # 2
        21.38,
        23.21,
        23.83,
        32.23,
        39.27,
        94.33,  # 2
        81.14,
        62.29,
        50.2,
        45.92,
        40.41,
        35.98,  # 3
        36.31,
        45.27,
        57.07,
        100.06,
        113.41,
        125.03,
        125.28,  # 3
        107.28,
        74.57,
    ],
    "yield": 66.62,
    "plan": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1000,  # 1
        0,
        0,
        0,
        1000,  # 1
        0,
        0,
        0,
        0,
        0,
        0,
        -1000,  # 2
        0,
        0,
        0,
        0,
        0,
        1000,  # 2
        0,
        0,
        0,
        0,
        0,
        -1000,  # 3
        0,
        0,
        0,
        0,
        0,
        0,
        1000,  # 3
        0,
        0,
    ],
}

long_price_series_with_3_cycles_2 = {
    "import": [
        32.5,
        33.14,
        33.33,
        34.11,
        34.95,
        31.24,  # charge 1
        33,
        37.06,
        40.99,
        42.64,  # discharge 1
        40.85,
        37.88,
        26.39,
        19.12,  # charge 2
        19.74,
        27.73,
        43.04,
        46.02,
        46.27,
        46.3,
        45.08,
        44.36,
        42.9,
        38.42,
        40.36,
        39.08,
        38.55,
        38.44,
        39.01,
        41.26,
        44.49,
        53.61,
        167.31,  # discharge 2
        149.55,
        109.03,
        96.45,  # charge 3
        110.96,
        109.34,
        114.29,
        124.38,
        136.49,
        164.16,
        196.15,
        273.65,  # discharge 3
        53.82,
        50.01,
        44.6,
        41.74,
    ],
    "export": [
        27,
        27.51,
        27.66,
        28.29,
        28.96,
        25.99,  # charge 1
        27.4,
        30.65,
        33.79,
        35.11,  # discharge 1
        33.68,
        31.3,
        22.11,
        16.3,  # charge 2
        16.79,
        23.18,
        35.43,
        37.82,
        38.02,
        38.04,
        37.06,
        36.49,
        35.32,
        31.74,
        33.29,
        32.26,
        31.84,
        31.75,
        32.21,
        34.01,
        36.59,
        43.89,
        134.85,  # discharge 2
        120.64,
        88.22,
        78.16,  # charge 3
        89.77,
        88.47,
        92.43,
        100.5,
        110.19,
        132.33,
        157.92,
        219.92,  # discharge 3
        44.06,
        41.01,
        36.68,
        34.39,
    ],
    "yield": (-31.24 + 35.11 - 19.12 + 134.85 - 96.45 + 219.92),
    "plan": [
        0,
        0,
        0,
        0,
        0,
        -1000,  # charge 1
        0,
        0,
        0,
        1000,  # discharge 1
        0,
        0,
        0,
        -1000,  # charge 2
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1000,  # discharge 2
        0,
        0,
        -1000,  # charge 3
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1000,  # discharge 3
        0,
        0,
        0,
        0,
    ],
}

# Import:
# Today
# 40.1, 39.75, 37.94, 37.62, 37.22, 35.64, 40.08, 228.89, 205.09, 176.04, 161.26, 154.21, 150.16, 140.94, 136.14, 152.29, 158.24, 177.89, 207.46, 243.5, 48.51, 42.69, 38.04, 28.2
# Tomorrow
# 20.84, 20.77, 20.26, 20.88, 23.01, 27.94, 35.64, 176.88, 211.34, 152.57, 54.4, 45.54, 44.98, 44.7, 45.02, 45.04, 45.6, 181.45, 210.73, 239.91, 227.95, 203.76, 54.47, 43.66
# Export:
# Today
# 33.08, 32.8, 31.35, 31.1, 30.78, 29.51, 33.06, 184.11, 165.07, 141.83, 130.01, 124.37, 121.13, 113.75, 109.91, 122.83, 127.59, 143.31, 166.97, 195.8, 39.81, 35.15, 31.43, 23.56
# Tomorrow
# 17.67, 17.62, 17.21, 17.7, 19.41, 23.35, 29.51, 142.5, 170.07, 123.06, 44.52, 37.43, 36.98, 36.76, 37.02, 37.03, 37.48, 146.16, 169.58, 192.93, 183.36, 164.01, 44.58, 35.93

# TODO: Dessa verkar bli fel! Den laddar inte ur (eller laddar) två timmar jämte varandra, local min/max kan inte vara ett krav såklart! Den näst bästa timmen kan komma precis före eller efter den bästa.
# Import:
# Today
# 38.89, 38.38, 38.15, 38.11, 38.25, 36.66, 37.77, 39.33, 42.49, 45.05, 45.98, 46.33, 45.53, 37.27, 38.16, 46.15, 46.79, 54.8, 180.69, 205.16, 221.49, 47.23, 46.23, 44.86
# Tomorrow
# 43.45, 41.58, 41.24, 40.95, 41.31, 44.45, 47.05, 251.96, 217.51, 185.24, 169.09, 158.5, 59.57, 55.2, 54.38, 54.86, 54.77, 58.76, 188.02, 63.99, 62.59, 56.05, 47.23, 45.21
# Export:
# Today
# 32.11, 31.7, 31.52, 31.49, 31.6, 30.33, 31.22, 32.46, 34.99, 37.04, 37.78, 38.06, 37.42, 30.82, 31.53, 37.92, 38.43, 44.84, 145.55, 165.13, 178.19, 38.78, 37.98, 36.89
# Tomorrow
# 35.76, 34.26, 33.99, 33.76, 34.05, 36.56, 38.64, 202.57, 175.01, 149.19, 136.27, 127.8, 48.66, 45.16, 44.5, 44.89, 44.82, 48.01, 151.42, 52.19, 51.07, 45.84, 38.78, 37.17
