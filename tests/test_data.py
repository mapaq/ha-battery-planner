"""Test data"""

short_price_series_with_1_cycle = {
    "import": [3.0, 2.0, 4.0, 4.0],
    "export": [1.0, 1.0, 3.0, 1.0],
    "yield": 1.0,
    "powers": [0, -1000, 1000, 0],
}

short_price_series_with_one_cycle_battery_charged_1 = {
    "import": [3.0, 2.0, 4.0, 4.0],
    "export": [1.0, 1.0, 3.0, 1.0],
    "yield": 2.0,
    "powers": [0, 0, 1000, 0],
    "battery_energy": 1000,
    "average_charge_cost": 1.0,
}

short_price_series_with_one_cycle_battery_charged_2 = {
    "import": [5.0, 2.0, 4.0, 4.0],
    "export": [4.0, 1.0, 3.0, 1.0],
    "yield": 4.0,  # 4.0 - 1.0 - 2.0 + 3.0
    "powers": [1000, -1000, 1000, 0],
    "battery_energy": 1000,
    "average_charge_cost": 1.0,
}

short_price_series_with_one_cycle_battery_charged_3 = {
    "import": [5.0, 2.0, 6.0, 4.0],
    "export": [4.0, 1.0, 5.0, 1.0],
    "yield": 1.0,  # 5.0 - 4.0
    "powers": [0, 0, 1000, 0],
    "battery_energy": 1000,
    "average_charge_cost": 4.0,
}

short_price_series_with_one_cycle_battery_charged_4 = {
    "import": [5.0, 2.0, 6.0, 4.0],
    "export": [4.0, 1.0, 5.0, 1.0],
    "yield": 4.0,  # - 3.0 + 4.0 - 2.0 + 5.0
    "powers": [1000, -1000, 1000, 0],
    "battery_energy": 1000,
    "average_charge_cost": 3.0,
}

short_price_series_with_2_cycles = {
    "import": [3.0, 2.0, 4.0, 1.0, 5.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0],
    "yield": 4.0,
    "powers": [0, -1000, 1000, -1000, 1000],
}

short_price_series_with_consecutive_charge = {
    "import": [3.0, 2.0, 1.0, 3.0, 5.0, 6.0, 2.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0, 5.0, 1.0],
    "yield": 6.0,
    "powers": [0, -1000, -1000, 0, 1000, 1000, 0],
}

short_price_series_with_consecutive_charge_battery_two_kw_three_kwh = {
    "import": [3.0, 2.0, 1.0, 3.0, 5.0, 6.0, 2.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0, 5.0, 1.0],
    "yield": 10.0,
    "powers": [0, -1000, -2000, 0, 1000, 2000, 0],
}

short_price_series_with_low_prices = {
    "import": [15, 16, 14, 16, 17, 13, 15],
    "export": [10, 9, 8, 11, 12, 7, 10],
    "yield": -27,
    "powers": [0, 0, -1000, 0, 0, -1000, 0],
    "low_price_threshold": 20,
    "battery": {
        "capacity": 2000,
        "max_charge_power": 1000,
        "max_discharge_power": 1000,
        "upper_soc_limit": 100,
        "lower_soc_limit": 0,
        "soc": 0,
    },
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
    "yield": round(-97.58 + 110.24 - 71.98 + 94.33 - 93.67 + 125.28, 2),  # = 66.62
    "powers": [
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

short_price_series_with_3_cycles_start_at_04 = {
    "start_hour": 4,
    "import": [
        97.58,
        165.69,
        186.5,
        183.57,
        80.1,
        71.98,  # 1
        97.79,
        166.61,  # 1
        93.67,  # 2
        94.09,
        205.3,  # 2
    ],
    "export": [
        39.1,
        93.59,
        110.24,
        107.9,
        25.12,
        18.62,  # 1
        39.27,
        94.33,  # 1
        35.98,  # 2
        36.31,
        125.28,  # 2
    ],
    "yield": round(-71.98 + 94.33 - 93.67 + 125.28, 2),
    "powers": [
        0,
        -1000,  # 1
        0,
        1000,  # 1
        -1000,  # 2
        0,
        1000,  # 2
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
    "powers": [
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
    "powers": [
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

long_price_series_start_on_hour_21 = {
    "battery": {
        "capacity": 7700,
        "max_charge_power": 4000,
        "max_discharge_power": 4000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 10,
    },
    "start_hour": 21,
    "yield": round(
        (
            104.9 * -2160
            + 100.26 * -4000
            + 157.74 * 2160
            + 184.05 * 4000
            + 127.61 * -4000
            + 127.81 * -2160
            + 240.9 * 4000
            + 212.9 * 2160
        )
        / 1000,
        2,
    ),  # 1086.25
    "import": [
        96.85,
        97.49,
        97.86,
        99.54,
        100.51,
        106.5,
        121.86,
        283.54,
        256.89,
        131.78,
        127.38,
        122.61,
        121.34,
        114.08,
        118.55,
        119.6,
        119.86,
        136.09,
        288.03,
        369.04,
        324.96,
        277.64,  # start
        104.9,  # 2
        100.26,  # 1
        229.76,
        224.86,
        232.15,
        234.44,
        234.98,
        250.25,
        278.93,  # 2
        311.81,  # 1
        278.08,
        233.40,
        129.1,
        128.69,
        127.61,  # 3
        127.81,  # 4
        130.9,
        152.28,
        236.74,
        258.24,
        317.76,
        382.88,  # 3
        347.88,  # 4
        245.79,
        131.18,
        126.13,
    ],
    "export": [
        12.08,
        12.59,
        12.89,
        14.23,
        15.01,
        19.8,
        32.09,
        161.43,
        140.11,
        40.02,
        36.5,
        32.69,
        31.67,
        25.86,
        29.44,
        30.28,
        30.49,
        43.47,
        165.02,
        229.83,
        194.57,
        156.71,  # start
        18.52,  # 2
        14.81,  # 1
        118.41,
        114.49,
        120.32,
        122.15,
        122.58,
        134.8,
        157.74,  # 2
        184.05,  # 1
        157.06,
        121.32,
        37.88,
        37.55,
        36.69,  # 3
        36.85,  # 4
        39.32,
        56.42,
        123.99,
        141.19,
        188.81,
        240.9,  # 3
        212.9,  # 4
        131.23,
        39.54,
        35.5,
    ],
    "powers": [
        0,  # start
        -2160,  # 2
        -4000,  # 1
        0,
        0,
        0,
        0,
        0,
        0,
        2160,  # 2
        4000,  # 1
        0,
        0,
        0,
        0,
        -4000,  # 3
        -2160,  # 4
        0,
        0,
        0,
        0,
        0,
        4000,  # 3
        2160,  # 4
        0,
        0,
        0,
    ],
}

long_price_series_start_hour_18_soc_90 = {
    "battery": {
        "capacity": 7700,
        "max_charge_power": 4000,
        "max_discharge_power": 4000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 90,
        "cycle_cost": 83,
    },
    "start_hour": 18,
    "yield": round(
        (
            2160 * 174.29
            + 4000 * 214.54
            - 2160 * 40.8
            - 4000 * 36.77
            + 4000 * 281.38
            + 2160 * 245.73
        )
        / 1000,
        2,
    ),
    "import": [
        38.66,
        36.66,
        36.35,
        36.26,
        36.46,
        38.81,
        51.65,
        211.35,
        205.39,
        170.61,
        143.55,
        122.79,
        120.91,
        88.9,
        74.61,
        66.66,
        89.14,
        171.3,
        216.61,
        266.92,
        162.05,
        48.21,
        40.8,  # 2
        36.77,  # 1
        50.39,
        45.7,
        44.12,
        43.55,
        51.39,
        156.36,
        185.59,
        216.66,
        200.29,
        166.85,
        151.3,
        140.31,
        129.32,
        123.09,
        125.55,
        136.96,
        149.14,
        178.16,
        270.35,
        350.48,
        305.91,
        55.54,
        35.01,
        31.99,
    ],
    "export": [
        31.93,
        30.33,
        30.08,
        30.01,
        30.17,
        32.05,
        42.32,
        170.08,
        165.31,
        137.49,
        115.84,
        99.23,
        97.73,
        72.12,
        60.69,
        54.33,
        72.31,
        138.04,
        174.29,  # 0.2
        214.54,  # 0.1
        130.64,
        39.57,
        33.64,
        30.42,
        41.31,
        37.56,
        36.3,
        35.84,
        42.11,
        126.09,
        149.47,
        174.33,
        161.23,
        134.48,
        122.04,
        113.25,
        104.46,
        99.47,
        101.44,
        110.57,
        120.31,
        143.53,
        217.28,
        281.38,  # 1
        245.73,  # 2
        45.43,
        29.01,
        26.59,
    ],
    "powers": [
        2160,
        4000,
        0,
        0,
        -2160,
        -4000,
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
        0,
        4000,
        2160,
        0,
        0,
        0,
    ],
}

long_price_series_start_hour_21_soc_10 = {
    "battery": {
        "capacity": 7700,
        "max_charge_power": 4000,
        "max_discharge_power": 4000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 10,
        "cycle_cost": 83,
    },
    "start_hour": 21,
    "yield": round(
        (-2160 * 40.8 - 4000 * 36.77 + 4000 * 281.38 + 2160 * 245.73) / 1000,
        2,
    ),
    "import": [
        38.66,
        36.66,
        36.35,
        36.26,
        36.46,
        38.81,
        51.65,
        211.35,
        205.39,
        170.61,
        143.55,
        122.79,
        120.91,
        88.9,
        74.61,
        66.66,
        89.14,
        171.3,
        216.61,
        266.92,
        162.05,
        48.21,
        40.8,  # 2
        36.77,  # 1
        50.39,
        45.7,
        44.12,
        43.55,
        51.39,
        156.36,
        185.59,
        216.66,
        200.29,
        166.85,
        151.3,
        140.31,
        129.32,
        123.09,
        125.55,
        136.96,
        149.14,
        178.16,
        270.35,
        350.48,
        305.91,
        55.54,
        35.01,
        31.99,
    ],
    "export": [
        31.93,
        30.33,
        30.08,
        30.01,
        30.17,
        32.05,
        42.32,
        170.08,
        165.31,
        137.49,
        115.84,
        99.23,
        97.73,
        72.12,
        60.69,
        54.33,
        72.31,
        138.04,
        174.29,
        214.54,
        130.64,
        39.57,
        33.64,
        30.42,
        41.31,
        37.56,
        36.3,
        35.84,
        42.11,
        126.09,
        149.47,
        174.33,
        161.23,
        134.48,
        122.04,
        113.25,
        104.46,
        99.47,
        101.44,
        110.57,
        120.31,
        143.53,
        217.28,
        281.38,  # 1
        245.73,  # 2
        45.43,
        29.01,
        26.59,
    ],
    "powers": [
        0,
        -2160,
        -4000,
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
        0,
        4000,
        2160,
        0,
        0,
        0,
    ],
}

long_price_series_start_hour_17_soc_80 = {
    "battery": {
        "capacity": 7700,
        "max_charge_power": 3500,
        "max_discharge_power": 7000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 80,
        "cycle_cost": 83,
    },
    "price_margin": 10,
    "start_hour": 17,
    "yield": round(
        (
            225.61 * 5390
            - 26.64 * 2660
            - 24.76 * 3500
            + 124.26 * 6160
            - 23.59 * 3500
            - 23.91 * 2660
            + 164.1 * 6160
        )
        / 1000,
        2,
    ),
    "import": [
        157.3,
        154.08,
        146.32,
        131.46,
        144.28,
        140.2,
        167.8,
        174.97,
        165.19,
        149.38,
        132.25,
        111.88,
        96.65,
        64.62,
        67.46,
        125.65,
        144.51,
        174.6,
        211.5,
        280.76,
        226.11,
        188.16,
        170.06,
        162.61,
        34.35,
        33.19,
        32.31,
        31.0,
        26.64,  # charge rest
        24.76,  # charge max
        135.82,
        150.6,
        154.08,
        138.55,
        120.56,
        75.44,
        48.24,
        23.59,  # charge max
        23.91,  # charge rest
        34.11,
        91.0,
        175.81,
        203.88,
        171.65,
        40.01,
        37.2,
        35.74,
        35.21,
    ],
    "export": [
        126.84,
        124.26,
        118.06,
        106.17,
        116.42,
        113.16,
        135.24,
        140.98,
        133.15,
        120.5,
        106.8,
        90.5,
        78.32,
        52.7,
        54.97,
        101.52,
        116.61,
        140.68,
        170.2,
        225.61,  # discharge full
        181.89,
        151.53,
        137.05,
        131.09,
        28.48,
        27.55,
        26.85,
        25.8,
        22.31,
        20.81,
        109.66,
        121.48,
        124.26,  # discharge full
        111.84,
        97.45,
        61.35,
        39.59,
        19.87,
        20.13,
        28.29,
        73.8,
        141.65,
        164.1,  # discahrge full
        138.32,
        33.01,
        30.76,
        29.59,
        29.17,
    ],
    "powers": [
        0,
        0,
        5390,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -2660,
        -3500,
        0,
        0,
        6160,
        0,
        0,
        0,
        0,
        -3500,
        -2660,
        0,
        0,
        0,
        6160,
        0,
        0,
        0,
        0,
        0,
    ],
}

long_price_series_start_hour_15_soc_80 = {
    "battery": {
        "capacity": 10000,
        "max_charge_power": 4000,
        "max_discharge_power": 8000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 80,
        "cycle_cost": 83,
    },
    "price_margin": 10,
    "start_hour": 15,
    "charge_plan": [
        {"Index": 0, "Import": 18.38, "Export": 15.7, "Power": 0},
        {"Index": 1, "Import": 17.66, "Export": 15.13, "Power": 0},
        {"Index": 2, "Import": 17.5, "Export": 15.0, "Power": 0},
        {"Index": 3, "Import": 17.49, "Export": 14.99, "Power": 0},
        {"Index": 4, "Import": 17.51, "Export": 15.01, "Power": 0},
        {"Index": 5, "Import": 18.38, "Export": 15.7, "Power": 0},
        {"Index": 6, "Import": 20.26, "Export": 17.21, "Power": 0},
        {"Index": 7, "Import": 23.41, "Export": 19.73, "Power": 0},
        {"Index": 8, "Import": 24.84, "Export": 20.87, "Power": 0},
        {"Index": 9, "Import": 22.2, "Export": 18.76, "Power": 0},
        {"Index": 10, "Import": 20.84, "Export": 17.67, "Power": 0},
        {"Index": 11, "Import": 20.21, "Export": 17.17, "Power": 0},
        {"Index": 12, "Import": 20.1, "Export": 17.08, "Power": 0},
        {"Index": 13, "Import": 19.59, "Export": 16.67, "Power": 0},
        {"Index": 14, "Import": 19.46, "Export": 16.57, "Power": 0},
        {"Index": 15, "Import": 19.84, "Export": 16.87, "Power": 0},
        {"Index": 16, "Import": 20.24, "Export": 17.19, "Power": 0},
        {"Index": 17, "Import": 20.59, "Export": 17.47, "Power": 0},
        {"Index": 18, "Import": 20.59, "Export": 17.47, "Power": 0},
        {"Index": 19, "Import": 20.31, "Export": 17.25, "Power": 0},
        {"Index": 20, "Import": 19.62, "Export": 16.7, "Power": 0},
        {"Index": 21, "Import": 18.27, "Export": 15.62, "Power": 0},
        {"Index": 22, "Import": 17.49, "Export": 14.99, "Power": 0},
        {"Index": 23, "Import": 16.6, "Export": 14.28, "Power": 0},
        {"Index": 24, "Import": 15.16, "Export": 13.13, "Power": 0},
        {"Index": 25, "Import": 15.05, "Export": 13.04, "Power": -1000},
        {"Index": 26, "Import": 15.31, "Export": 13.25, "Power": 0},
        {"Index": 27, "Import": 15.76, "Export": 13.61, "Power": 0},
        {"Index": 28, "Import": 16.4, "Export": 14.12, "Power": 0},
        {"Index": 29, "Import": 17.49, "Export": 14.99, "Power": 0},
        {"Index": 30, "Import": 18.91, "Export": 16.13, "Power": 0},
        {"Index": 31, "Import": 218.0, "Export": 175.4, "Power": 8000},
        {"Index": 32, "Import": 214.69, "Export": 172.75, "Power": 0},
        {"Index": 33, "Import": 177.01, "Export": 142.61, "Power": 0},
        {"Index": 34, "Import": 162.24, "Export": 130.79, "Power": 0},
        {"Index": 35, "Import": 149.59, "Export": 120.67, "Power": 0},
        {"Index": 36, "Import": 141.9, "Export": 114.52, "Power": 0},
        {"Index": 37, "Import": 130.49, "Export": 105.39, "Power": 0},
        {"Index": 38, "Import": 123.0, "Export": 99.4, "Power": 0},
        {"Index": 39, "Import": 126.53, "Export": 102.22, "Power": 0},
        {"Index": 40, "Import": 144.4, "Export": 116.52, "Power": 0},
        {"Index": 41, "Import": 19.05, "Export": 16.24, "Power": 0},
        {"Index": 42, "Import": 19.06, "Export": 16.25, "Power": 0},
        {"Index": 43, "Import": 18.99, "Export": 16.19, "Power": 0},
        {"Index": 44, "Import": 18.36, "Export": 15.69, "Power": 0},
        {"Index": 45, "Import": 17.59, "Export": 15.07, "Power": 0},
        {"Index": 46, "Import": 17.5, "Export": 15.0, "Power": 0},
        {"Index": 47, "Import": 17.18, "Export": 14.74, "Power": 0},
    ],
}

long_price_series_start_hour_14_soc_90 = {
    "battery": {
        "capacity": 10000,
        "max_charge_power": 4000,
        "max_discharge_power": 8000,
        "upper_soc_limit": 90,
        "lower_soc_limit": 10,
        "soc": 90,
        "cycle_cost": 83,
    },
    "average_charge_cost": 0.2,
    "price_margin": 10,
    "start_hour": 14,
    "charge_plan": [
        {"Index": 0, "Import": 76.36, "Export": 62.08, "Power": 0},
        {"Index": 1, "Import": 72.39, "Export": 58.9, "Power": 0},
        {"Index": 2, "Import": 68.12, "Export": 55.49, "Power": 0},
        {"Index": 3, "Import": 69.45, "Export": 56.55, "Power": 0},
        {"Index": 4, "Import": 76.0, "Export": 61.79, "Power": 0},
        {"Index": 5, "Import": 90.39, "Export": 73.3, "Power": 0},
        {"Index": 6, "Import": 142.53, "Export": 115.02, "Power": 0},
        {"Index": 7, "Import": 205.37, "Export": 165.29, "Power": 0},
        {"Index": 8, "Import": 209.58, "Export": 168.66, "Power": 0},
        {"Index": 9, "Import": 177.03, "Export": 142.62, "Power": 0},
        {"Index": 10, "Import": 158.19, "Export": 127.54, "Power": 0},
        {"Index": 11, "Import": 143.32, "Export": 115.65, "Power": 0},
        {"Index": 12, "Import": 139.47, "Export": 112.57, "Power": 0},
        {"Index": 13, "Import": 142.94, "Export": 115.34, "Power": 0},
        {"Index": 14, "Import": 155.42, "Export": 125.33, "Power": 0},
        {"Index": 15, "Import": 162.06, "Export": 130.64, "Power": 0},
        {"Index": 16, "Import": 177.55, "Export": 143.03, "Power": 0},
        {"Index": 17, "Import": 211.49, "Export": 170.18, "Power": 0},
        {"Index": 18, "Import": 228.81, "Export": 184.04, "Power": 8000},
        {"Index": 19, "Import": 160.9, "Export": 129.71, "Power": 0},
        {"Index": 20, "Import": 141.3, "Export": 114.03, "Power": 0},
        {"Index": 21, "Import": 135.56, "Export": 109.44, "Power": 0},
        {"Index": 22, "Import": 108.32, "Export": 87.65, "Power": 0},
        {"Index": 23, "Import": 86.71, "Export": 70.36, "Power": 0},
        {"Index": 24, "Import": 75.7, "Export": 61.55, "Power": 0},
        {"Index": 25, "Import": 72.01, "Export": 58.6, "Power": 0},
        {"Index": 26, "Import": 69.95, "Export": 56.95, "Power": 0},
        {"Index": 27, "Import": 68.95, "Export": 56.15, "Power": 0},
        {"Index": 28, "Import": 71.52, "Export": 58.21, "Power": 0},
        {"Index": 29, "Import": 83.9, "Export": 68.11, "Power": 0},
        {"Index": 30, "Import": 127.08, "Export": 102.66, "Power": 0},
        {"Index": 31, "Import": 142.81, "Export": 115.24, "Power": 0},
        {"Index": 32, "Import": 166.05, "Export": 133.83, "Power": 0},
        {"Index": 33, "Import": 149.8, "Export": 120.83, "Power": 0},
        {"Index": 34, "Import": 138.13, "Export": 111.5, "Power": 0},
        {"Index": 35, "Import": 132.49, "Export": 106.98, "Power": 0},
        {"Index": 36, "Import": 127.9, "Export": 103.31, "Power": 0},
        {"Index": 37, "Import": 128.45, "Export": 103.75, "Power": 0},
        {"Index": 38, "Import": 134.99, "Export": 108.98, "Power": 0},
        {"Index": 39, "Import": 134.86, "Export": 108.88, "Power": 0},
        {"Index": 40, "Import": 138.2, "Export": 111.55, "Power": 0},
        {"Index": 41, "Import": 141.44, "Export": 114.14, "Power": 0},
        {"Index": 42, "Import": 131.98, "Export": 106.58, "Power": 0},
        {"Index": 43, "Import": 123.41, "Export": 99.72, "Power": 0},
        {"Index": 44, "Import": 103.9, "Export": 84.11, "Power": 0},
        {"Index": 45, "Import": 91.97, "Export": 74.57, "Power": 0},
        {"Index": 46, "Import": 75.69, "Export": 61.54, "Power": 0},
        {"Index": 47, "Import": 62.25, "Export": 50.79, "Power": 0},
    ],
}
