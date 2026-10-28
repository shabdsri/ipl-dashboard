# DAX Measures Reference Guide

This document contains standardized DAX measures created for the `Fact_Deliveries` table in Power BI Desktop. Every ratio utilizes `DIVIDE` to prevent division-by-zero errors.

---

### Core Volume & Batting Measures

#### 1. Total Runs
```dax
Total Runs = SUM(Fact_Deliveries[total_runs])
```
*Total runs scored across all matches, combining runs off the bat and all extras.*

#### 2. Batter Runs
```dax
Batter Runs = SUM(Fact_Deliveries[batsman_runs])
```
*Total runs scored directly off the bat by batsmen.*

#### 3. Balls Faced
```dax
Balls Faced = SUM(Fact_Deliveries[batter_ball_flag])
```
*Total balls faced by batters, excluding wides and including no-balls.*

#### 4. Strike Rate
```dax
Strike Rate = DIVIDE([Batter Runs] * 100, [Balls Faced], BLANK())
```
*Batting scoring rate represented as runs scored per 100 balls faced.*

#### 5. Fours
```dax
Fours = SUM(Fact_Deliveries[four_flag])
```
*Count of 4s scored off the bat.*

#### 6. Sixes
```dax
Sixes = SUM(Fact_Deliveries[six_flag])
```
*Count of 6s scored off the bat.*

#### 7. Boundary %
```dax
Boundary % = DIVIDE([Fours] + [Sixes], [Balls Faced], BLANK())
```
*Percentage of balls faced that resulted in a boundary (4 or 6).*

---

### Bowling & Economy Measures

#### 8. Legal Balls
```dax
Legal Balls = SUM(Fact_Deliveries[legal_ball_flag])
```
*Count of fair deliveries bowled (excludes wides and no-balls) used as the divisor for bowling metrics.*

#### 9. Runs Conceded
```dax
Runs Conceded = SUM(Fact_Deliveries[bowler_runs])
```
*Runs charged to the bowler (includes bat runs, wides, and no-balls; excludes byes, leg-byes, and penalties).*

#### 10. Economy
```dax
Economy = DIVIDE([Runs Conceded] * 6, [Legal Balls], BLANK())
```
*Average runs conceded per over (6 legal deliveries).*

#### 11. Wickets
```dax
Wickets = SUM(Fact_Deliveries[bowler_wicket_flag])
```
*Total dismissals credited to the bowler (bowled, caught, caught and bowled, lbw, stumped, hit wicket).*

#### 12. Dot Ball %
```dax
Dot Ball % = DIVIDE(SUM(Fact_Deliveries[dot_ball_flag]), [Legal Balls], BLANK())
```
*Percentage of legal deliveries where zero runs were conceded.*

---

### Match Context & Phase-Specific Measures

#### 13. Matches
```dax
Matches = DISTINCTCOUNT(Fact_Deliveries[match_id])
```
*Total count of distinct matches played.*

#### 14. Runs per Over
```dax
Runs per Over = DIVIDE([Total Runs] * 6, [Legal Balls], BLANK())
```
*Overall scoring rate of the match or innings per 6 legal deliveries.*

#### 15. Powerplay Economy
```dax
Powerplay Economy = CALCULATE([Economy], Fact_Deliveries[phase] = "Powerplay")
```
*Bowler economy rate filtered specifically to the Powerplay phase (overs 1–6).*

#### 16. Middle Economy
```dax
Middle Economy = CALCULATE([Economy], Fact_Deliveries[phase] = "Middle")
```
*Bowler economy rate filtered specifically to the Middle overs phase (overs 7–15).*

#### 17. Death Economy
```dax
Death Economy = CALCULATE([Economy], Fact_Deliveries[phase] = "Death")
```
*Bowler economy rate filtered specifically to the Death overs phase (overs 16–20).*

---

### Usage Notes for Power BI
1. Create a dedicated measure table (e.g. `_Measures`) to organize these metrics.
2. Format `Strike Rate`, `Economy`, `Powerplay Economy`, and `Death Economy` as Decimal Number with 2 decimal places.
3. Format `Dot Ball %` and `Boundary %` as Percentage with 1 or 2 decimal places.
4. Format `Batter Runs`, `Runs Conceded`, `Balls Faced`, and `Legal Balls` as Whole Number with thousands separators.
