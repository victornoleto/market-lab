# EDA — system 11504701

Generated: 2026-05-01

## Entry hour distribution (UTC)
- 00:00  →  0
- 01:00  →  0
- 02:00  →  6
- 03:00  →  3
- 04:00  →  5
- 05:00  →  1
- 06:00  →  1
- 07:00  →  2
- 08:00  →  0
- 09:00  →  17
- 10:00  →  5
- 11:00  →  9
- 12:00  →  0
- 13:00  →  0
- 14:00  →  5
- 15:00  →  172
- 16:00  →  12
- 17:00  →  63
- 18:00  →  0
- 19:00  →  0
- 20:00  →  0
- 21:00  →  10
- 22:00  →  0
- 23:00  →  3

## Day of week
- Monday: 15
- Tuesday: 55
- Wednesday: 87
- Thursday: 100
- Friday: 57
- Saturday: 0
- Sunday: 0

## Per-pair entry hour peak
```
          n  peak_hour  peak_n  pct_peak  hours_active
symbol                                                
ARCHIV    2         23       2     100.0             1
AUDUSD   44         15      23      52.3             9
EURUSD   69         15      41      59.4             6
GBPUSD   96         15      45      46.9             7
USDJPY  103         15      63      61.2             4
```

## Exit mechanism
- manual_or_time: 314

## SL/TP setting evolution (per-year)
```
        n sl_pips_med tp_pips_med  sl_pips_p95  tp_pips_p95
year                                                       
2025  251         NaN         NaN          NaN          NaN
2026   63         NaN         NaN          NaN          NaN
```

## PnL by pair (gross)
```
          n  win_pct  avg_pips  median_pips  total_pips  total_profit_usd
symbol                                                                   
USDJPY  103    94.17      7.58          3.7       781.2          25723.24
GBPUSD   96    95.83      4.21          1.8       404.4          17711.24
EURUSD   69    89.86      4.07          2.8       280.8          48354.65
AUDUSD   44    97.73      3.21          1.2       141.4           5228.86
ARCHIV    2     0.00      0.00          0.0         0.0           8119.31
```

## PnL by year (net, after Pepperstone Razor 2025 cost model)
```
        n  gross_avg  cost_avg  net_avg  net_total  win_pct_net  sharpe_net
year                                                                       
2025  251       5.43      1.44     3.99    1002.37        68.92       0.407
2026   63       3.89      1.51     2.38     149.86        53.97       0.253
```

## PnL by pair (net)
```
          n  gross_avg  cost  net_avg  net_total  win_pct_net
symbol                                                       
USDJPY  103       7.58  1.90     5.68     585.50        68.93
EURUSD   69       4.07  0.83     3.24     223.53        89.86
GBPUSD   96       4.21  1.20     3.01     289.20        57.29
AUDUSD   44       3.21  1.90     1.31      57.80        43.18
ARCHIV    2       0.00  1.90    -1.90      -3.80         0.00
```

## Direction by pair (Buy/Sell)
```
action  Buy  Sell  total  buy_pct
symbol                           
ARCHIV    2     0      2    100.0
AUDUSD   30    14     44     68.2
EURUSD   39    30     69     56.5
GBPUSD   50    46     96     52.1
USDJPY   51    52    103     49.5
```

## Yearly decay (gross)
```
        n  win_pct  avg_pips  std_pips  median_pips  total_pips  sharpe_naive
year                                                                         
2025  251    94.42      5.43      9.86          2.7      1362.9         0.551
2026   63    90.48      3.89      9.33          1.4       244.9         0.417
```

## Session structure
- single: 44
- 2_to_3: 34
- 4_to_6: 34
- 7_plus: 4
- n_distinct_sessions: 116
- Direction flip rate after loss: 75.0%