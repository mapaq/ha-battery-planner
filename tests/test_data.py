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
    "yield": [4.0],  # 4.0 - 1.0 - 2.0 + 3.0
    "plan": [1000, -1000, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [1.0],
}

short_price_series_with_one_cycle_battery_charged_3 = {
    "import": [5.0, 2.0, 6.0, 4.0],
    "export": [4.0, 1.0, 5.0, 1.0],
    "yield": [1.0],  # 5.0 - 4.0
    "plan": [0, 0, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [4.0],
}

short_price_series_with_one_cycle_battery_charged_4 = {
    "import": [5.0, 2.0, 6.0, 4.0],
    "export": [4.0, 1.0, 5.0, 1.0],
    "yield": [4.0],  # 4.0 - 2.0 + 5.0 - 3.0
    "plan": [1000, -1000, 1000, 0],
    "battery_energy": [1000],
    "average_charge_cost": [3.0],
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

short_price_series_with_consecutive_charge_battery_two_kw_three_kwh = {
    "import": [3.0, 2.0, 1.0, 3.0, 5.0, 6.0, 2.0],
    "export": [1.0, 1.0, 3.0, 2.0, 4.0, 5.0, 1.0],
    "yield": 10.0,
    "plan": [0, -1000, -2000, 0, 1000, 2000, 0],
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
    "plan": [
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
    "plan": [
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
        "degradation_cost": 83,
    },
    "start_hour": 18,
    "yield": round(
        (
            2160 * 174.29
            + 4000 * 214.54
            - 2160 * 123.8
            - 4000 * 119.77
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
        40.8,
        36.77,
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
        281.38,
        245.73,
        45.43,
        29.01,
        26.59,
    ],
    "plan": [
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
        "degradation_cost": 83,
    },
    "start_hour": 21,
    "yield": round(
        (-2160 * 123.8 - 4000 * 119.77 + 4000 * 281.38 + 2160 * 245.73) / 1000,
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
        40.8,
        36.77,
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
        281.38,
        245.73,
        45.43,
        29.01,
        26.59,
    ],
    "plan": [
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

"""
2023-09-07T18:00:00: {'Index': 18, 'Hour': '2023-09-07T18:00:00', 'Import price': 299.61, 'Export price': 174.29, 'Power': 2160}
2023-09-07T19:00:00: {'Index': 19, 'Hour': '2023-09-07T19:00:00', 'Import price': 349.92, 'Export price': 214.54, 'Power': 4000}
2023-09-07T20:00:00: {'Index': 20, 'Hour': '2023-09-07T20:00:00', 'Import price': 245.05, 'Export price': 130.64, 'Power': 0}
2023-09-07T21:00:00: {'Index': 21, 'Hour': '2023-09-07T21:00:00', 'Import price': 131.21, 'Export price': 39.57, 'Power': 0}
2023-09-07T22:00:00: {'Index': 22, 'Hour': '2023-09-07T22:00:00', 'Import price': 123.8, 'Export price': 33.64, 'Power': -2160}
2023-09-07T23:00:00: {'Index': 23, 'Hour': '2023-09-07T23:00:00', 'Import price': 119.78, 'Export price': 30.42, 'Power': -4000}
2023-09-08T00:00:00: {'Index': 24, 'Hour': '2023-09-08T00:00:00', 'Import price': 133.39, 'Export price': 41.31, 'Power': 0}
2023-09-08T01:00:00: {'Index': 25, 'Hour': '2023-09-08T01:00:00', 'Import price': 128.7, 'Export price': 37.56, 'Power': 0}
2023-09-08T02:00:00: {'Index': 26, 'Hour': '2023-09-08T02:00:00', 'Import price': 127.12, 'Export price': 36.3, 'Power': 0}
2023-09-08T03:00:00: {'Index': 27, 'Hour': '2023-09-08T03:00:00', 'Import price': 126.55, 'Export price': 35.84, 'Power': 0}
2023-09-08T04:00:00: {'Index': 28, 'Hour': '2023-09-08T04:00:00', 'Import price': 134.39, 'Export price': 42.11, 'Power': 0}
2023-09-08T05:00:00: {'Index': 29, 'Hour': '2023-09-08T05:00:00', 'Import price': 239.36, 'Export price': 126.09, 'Power': 0}
2023-09-08T06:00:00: {'Index': 30, 'Hour': '2023-09-08T06:00:00', 'Import price': 268.59, 'Export price': 149.47, 'Power': 0}
2023-09-08T07:00:00: {'Index': 31, 'Hour': '2023-09-08T07:00:00', 'Import price': 299.66, 'Export price': 174.33, 'Power': 0}
2023-09-08T08:00:00: {'Index': 32, 'Hour': '2023-09-08T08:00:00', 'Import price': 283.29, 'Export price': 161.23, 'Power': 0}
2023-09-08T09:00:00: {'Index': 33, 'Hour': '2023-09-08T09:00:00', 'Import price': 249.85, 'Export price': 134.48, 'Power': 0}
2023-09-08T10:00:00: {'Index': 34, 'Hour': '2023-09-08T10:00:00', 'Import price': 234.3, 'Export price': 122.04, 'Power': 0}
2023-09-08T11:00:00: {'Index': 35, 'Hour': '2023-09-08T11:00:00', 'Import price': 223.31, 'Export price': 113.25, 'Power': 0}
2023-09-08T12:00:00: {'Index': 36, 'Hour': '2023-09-08T12:00:00', 'Import price': 212.32, 'Export price': 104.46, 'Power': 0}
2023-09-08T13:00:00: {'Index': 37, 'Hour': '2023-09-08T13:00:00', 'Import price': 206.09, 'Export price': 99.47, 'Power': 0}
2023-09-08T14:00:00: {'Index': 38, 'Hour': '2023-09-08T14:00:00', 'Import price': 208.55, 'Export price': 101.44, 'Power': 0}
2023-09-08T15:00:00: {'Index': 39, 'Hour': '2023-09-08T15:00:00', 'Import price': 219.96, 'Export price': 110.57, 'Power': 0}
2023-09-08T16:00:00: {'Index': 40, 'Hour': '2023-09-08T16:00:00', 'Import price': 232.14, 'Export price': 120.31, 'Power': 0}
2023-09-08T17:00:00: {'Index': 41, 'Hour': '2023-09-08T17:00:00', 'Import price': 261.16, 'Export price': 143.53, 'Power': 0}
2023-09-08T18:00:00: {'Index': 42, 'Hour': '2023-09-08T18:00:00', 'Import price': 353.35, 'Export price': 217.28, 'Power': 0}
2023-09-08T19:00:00: {'Index': 43, 'Hour': '2023-09-08T19:00:00', 'Import price': 433.48, 'Export price': 281.38, 'Power': 4000}
2023-09-08T20:00:00: {'Index': 44, 'Hour': '2023-09-08T20:00:00', 'Import price': 388.91, 'Export price': 245.73, 'Power': 2160}
2023-09-08T21:00:00: {'Index': 45, 'Hour': '2023-09-08T21:00:00', 'Import price': 138.54, 'Export price': 45.43, 'Power': 0}
2023-09-08T22:00:00: {'Index': 46, 'Hour': '2023-09-08T22:00:00', 'Import price': 118.01, 'Export price': 29.01, 'Power': 0}
2023-09-08T23:00:00: {'Index': 47, 'Hour': '2023-09-08T23:00:00', 'Import price': 114.99, 'Export price': 26.59, 'Power': 0}
"""
