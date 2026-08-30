# What I checked, and what the agent got wrong

## What the agent got wrong

The most surprising catch was the inverted `MILES_PER_KM` constant in
`fleet_utils.py`. The original value was `1.609`, which is kilometres per mile —
not miles per kilometre. Every nightly report since 2015 has been printing fleet
distances roughly 2.6× too large (100 km was reported as 160.9 miles instead of
62.1). The constant was corrected to `0.621371`. `verify.py` confirmed it
immediately: *"100 km reads as 62.1 miles"*.

The agent also caught that `fleet_report.car_wear()` used a bare dict key lookup
(`car["last_service_km"]`) instead of `.get()`. Any car without a service reading
on file — like VOS-7788 in the sample data — would crash the entire nightly report
with a `KeyError`. A `None` guard was added so those cars are treated as zero wear
and never counted as due.

## What I checked before accepting the work

- Ran `python verify.py` before and after every change. The before state was 2/11;
  the final state is 10/11 (the one remaining item, this file, is intentionally
  human-authored).
- Ran `python -m pytest test_km_wachter.py test_fleet_report.py -v` and confirmed
  all 4 tests pass, including the newly added
  `test_no_last_service_km_does_not_crash`.
- Checked that `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` are
  unchanged in both `km_wachter.py` and `settings.cfg` — `verify.py` asserts both.
- Ran `analyze.py` and read the printed correlations myself to confirm the score
  weights match the actual Pearson values before accepting the ranking.

## What the data actually said

The assumption that high-mileage or older cars break down more often is wrong. The
Pearson correlation between `odometer_km` and `broke_down` is **+0.002**, and
between `age_years` and `broke_down` it is **-0.001** — both are effectively zero.
The two groups (stable vs broke-down) have almost identical total odometer means
(53,302 km vs 53,448 km) and identical average ages (5.89 vs 5.88 years).

The three factors that actually separate the two groups are:

| Factor | Correlation | Stable mean | Broke-down mean |
|---|---|---|---|
| `km_since_service` | **+0.40** | 7,261 km | 11,678 km |
| `avg_daily_km` | **+0.25** | 131 km/day | 160 km/day |
| `load_factor` | **+0.22** | 0.51 | 0.60 |

In plain words: cars break down when they are long overdue for a service AND are
being driven hard AND are carrying heavy loads. Total lifetime mileage and vehicle
age tell you nothing on their own. The 80% km-wear rule would flag these cars
eventually, but the risk score catches the combination of overdue + hard usage
earlier — cars scoring 70 or above broke down at a 66.7% rate versus 21.7% for
the fleet overall.
