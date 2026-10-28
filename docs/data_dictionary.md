# Data Dictionary: Fact_Deliveries

This document describes all columns present in `data/clean/fact_deliveries.csv` (imported into Power BI Desktop as `Fact_Deliveries`).

| Column Name | Data Type | Source / Derivation | Description & Business Meaning |
| :--- | :--- | :--- | :--- |
| **`match_id`** | Whole Number | Raw | Unique numeric identifier for the IPL match. |
| **`inning`** | Whole Number | Raw | Inning of the match (1 or 2). Super overs (innings 3–6) are excluded. |
| **`batting_team`** | Text | Raw (Standardized) | Standardized franchise name of the team batting on this delivery. |
| **`bowling_team`** | Text | Raw (Standardized) | Standardized franchise name of the team bowling on this delivery. |
| **`over`** | Whole Number | Raw | 0-indexed over number (0 to 19). |
| **`ball`** | Whole Number | Raw | Sequential delivery number within the over (1 to 6+, accounting for extras). |
| **`batter`** | Text | Raw | Name of the batsman on strike facing the delivery. |
| **`bowler`** | Text | Raw | Name of the bowler delivering the ball. |
| **`non_striker`** | Text | Raw | Name of the batsman standing at the non-striker's end. |
| **`batsman_runs`** | Whole Number | Raw | Runs scored off the bat by the striker (0, 1, 2, 3, 4, 5, 6). |
| **`extra_runs`** | Whole Number | Raw | Additional runs conceded as extras on this delivery. |
| **`total_runs`** | Whole Number | Raw | Total runs conceded on this delivery (`batsman_runs + extra_runs`). |
| **`extras_type`** | Text | Cleaned | Type of extra: `none`, `wides`, `noballs`, `byes`, `legbyes`, or `penalty`. Empty raw values filled with `"none"`. |
| **`is_wicket`** | Whole Number | Raw | Flag indicating whether any dismissal occurred on this delivery (1 = wicket fell, 0 = no wicket). |
| **`player_dismissed`** | Text | Raw | Name of the dismissed batsman (`NA` if no wicket fell). |
| **`dismissal_kind`** | Text | Raw | Mode of dismissal (e.g., `bowled`, `caught`, `run out`, `lbw`, `stumped`, `hit wicket`, `caught and bowled`, `retired out`, `retired hurt`, `obstructing the field`, or `NA`). |
| **`fielder`** | Text | Raw | Name of the primary fielder involved in the dismissal (`NA` if unassisted or no wicket). |
| **`over_no`** | Whole Number | Derived | 1-indexed over number (1 to 20), computed as `over + 1`. |
| **`phase`** | Text | Derived | T20 match phase: `Powerplay` (overs 1–6), `Middle` (overs 7–15), or `Death` (overs 16–20). |
| **`legal_ball_flag`** | Whole Number | Derived | Flag for fair deliveries: `0` if `extras_type` is `wides` or `noballs`, else `1`. Divisor for overs bowled, economy rate, and dot ball rate. |
| **`batter_ball_flag`** | Whole Number | Derived | Flag for balls faced by the batter: `0` if `wides`, else `1` (no-balls count as legitimate balls faced). Divisor for batting strike rate. |
| **`bowler_runs`** | Whole Number | Derived | Runs charged against the bowler: `batsman_runs + extra_runs` on wides/no-balls; otherwise `batsman_runs`. Fielding extras (byes, leg byes, penalties) are excluded. |
| **`bowler_wicket_flag`**| Whole Number | Derived | Flag for wickets credited to the bowler: `1` if `dismissal_kind` is `bowled`, `caught`, `caught and bowled`, `lbw`, `stumped`, or `hit wicket`; `0` for run outs, retirements, or non-wickets. |
| **`four_flag`** | Whole Number | Derived | Flag for boundaries scored: `1` if `batsman_runs == 4`, else `0`. |
| **`six_flag`** | Whole Number | Derived | Flag for maximums scored: `1` if `batsman_runs == 6`, else `0`. |
| **`dot_ball_flag`** | Whole Number | Derived | Flag for dot balls: `1` if `total_runs == 0` AND `legal_ball_flag == 1`, else `0`. |

---

### Supporting Dimension Tables

#### `dim_team.csv`
Contains the deduplicated list of standardized IPL franchises:
- **`team`** (Text): Standardized team name used for slicing batting and bowling performance.

#### `dim_matches.csv` (Optional, generated when `matches.csv` is provided)
- **`match_id`** (Whole Number): Primary key linking to `fact_deliveries[match_id]`.
- **`team1`**, **`team2`** (Text): Competing teams (standardized names).
- **`toss_winner`** (Text): Team winning the coin toss (standardized).
- **`toss_decision`** (Text): Selected decision (`bat` or `field`).
- **`winner`** (Text): Match winning franchise (standardized).
- **`toss_winner_won_match`** (Whole Number): `1` if toss winner won the match, else `0`.
- **`bat_first_won`** (Whole Number): `1` if team batting in 1st innings won the match, else `0`.
