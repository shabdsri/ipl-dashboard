"""
IPL Data Preparation Pipeline
=============================
Processes raw ball-by-ball IPL delivery data (2008-2024) into clean,
Power BI-ready fact and dimension tables.

Outputs:
  - data/clean/fact_deliveries.csv
  - data/clean/dim_team.csv
  - data/clean/dim_matches.csv (if data/raw/matches.csv exists)
"""

from pathlib import Path
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Team Name Standardization Mapping
# ---------------------------------------------------------------------------
# Note: Deccan Chargers was replaced by Sunrisers Hyderabad in 2013 (same city
# franchise transition). This mapping is clearly isolated below so it can easily
# be removed or modified if distinct historical franchise tracking is preferred.
TEAM_MAP = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    # --- Franchise transition (remove if separate franchise history is required) ---
    "Deccan Chargers": "Sunrisers Hyderabad",
    # --------------------------------------------------------------------------------
}

# Bowling dismissals credited to the bowler
BOWLER_DISMISSAL_KINDS = {
    "bowled",
    "caught",
    "caught and bowled",
    "lbw",
    "stumped",
    "hit wicket",
}


def get_project_root() -> Path:
    """Return project root directory regardless of current working directory."""
    # scripts/prepare_data.py -> project root is parent of scripts directory
    return Path(__file__).resolve().parent.parent


def standardize_team_names(series: pd.Series) -> pd.Series:
    """Standardize franchise names using TEAM_MAP."""
    return series.replace(TEAM_MAP)


def process_deliveries(raw_path: Path, clean_dir: Path) -> pd.DataFrame:
    """
    Load raw deliveries.csv, apply transformations, print metrics,
    and save fact_deliveries.csv and dim_team.csv.
    """
    print(f"Loading raw deliveries from: {raw_path}")
    if not raw_path.exists():
        raise FileNotFoundError(f"Deliveries file not found at: {raw_path}")

    df = pd.read_csv(raw_path, low_memory=False)
    print(f"Loaded {len(df):,} raw delivery records across {df['match_id'].nunique():,} matches.")

    # 1. Fill blank extras_type with "none"
    df["extras_type"] = df["extras_type"].fillna("none").astype(str).str.strip().str.lower()

    # 2. Add over_no = over + 1 (1 to 20)
    df["over_no"] = df["over"] + 1

    # 3. Add phase: 1-6 = Powerplay, 7-15 = Middle, 16-20 = Death
    conditions = [
        df["over_no"].between(1, 6),
        df["over_no"].between(7, 15),
        df["over_no"].between(16, 20),
    ]
    choices = ["Powerplay", "Middle", "Death"]
    df["phase"] = np.select(conditions, choices, default="Other")

    # 4. Add legal_ball_flag = 0 if extras_type is wides or noballs, else 1
    # Vectorized check
    is_wide_or_noball = df["extras_type"].isin(["wides", "noballs"])
    df["legal_ball_flag"] = np.where(is_wide_or_noball, 0, 1)

    # 5. Add batter_ball_flag = 0 only if extras_type is wides, else 1
    # No-balls count as balls faced for the batter
    df["batter_ball_flag"] = np.where(df["extras_type"] == "wides", 0, 1)

    # 6. Add bowler_runs = batsman_runs + extra_runs if wides or noballs, else batsman_runs
    # Byes, leg byes, and penalties are fielding extras and not charged to the bowler
    df["bowler_runs"] = np.where(
        is_wide_or_noball,
        df["batsman_runs"] + df["extra_runs"],
        df["batsman_runs"],
    )

    # 7. Add bowler_wicket_flag = 1 only for bowler-credited dismissals
    # Clean dismissal_kind for robust string matching
    clean_dismissal = df["dismissal_kind"].fillna("").astype(str).str.strip().str.lower()
    df["bowler_wicket_flag"] = np.where(clean_dismissal.isin(BOWLER_DISMISSAL_KINDS), 1, 0)

    # 8. Add four_flag, six_flag, dot_ball_flag
    df["four_flag"] = np.where(df["batsman_runs"] == 4, 1, 0)
    df["six_flag"] = np.where(df["batsman_runs"] == 6, 1, 0)
    df["dot_ball_flag"] = np.where((df["total_runs"] == 0) & (df["legal_ball_flag"] == 1), 1, 0)

    # 9. Standardize team names in BOTH batting_team and bowling_team
    df["batting_team"] = standardize_team_names(df["batting_team"].astype(str).str.strip())
    df["bowling_team"] = standardize_team_names(df["bowling_team"].astype(str).str.strip())

    # 10. Exclude super-over rows (inning > 2) and print count of matches that had them
    super_over_mask = df["inning"] > 2
    super_over_matches = df.loc[super_over_mask, "match_id"].nunique()
    super_over_rows = super_over_mask.sum()
    print(f"Super-over filter: excluded {super_over_rows:,} balls across {super_over_matches} matches.")

    fact_df = df.loc[~super_over_mask].copy()
    print(f"Clean fact_deliveries records: {len(fact_df):,} across {fact_df['match_id'].nunique():,} matches.")

    # 11. Export data/clean/fact_deliveries.csv and data/clean/dim_team.csv
    clean_dir.mkdir(parents=True, exist_ok=True)
    fact_csv_path = clean_dir / "fact_deliveries.csv"
    fact_df.to_csv(fact_csv_path, index=False)
    print(f"Saved: {fact_csv_path}")

    # Extract distinct standardized teams from both batting and bowling
    distinct_teams = sorted(set(fact_df["batting_team"].unique()) | set(fact_df["bowling_team"].unique()))
    dim_team_df = pd.DataFrame({"team": distinct_teams})
    dim_team_path = clean_dir / "dim_team.csv"
    dim_team_df.to_csv(dim_team_path, index=False)
    print(f"Saved: {dim_team_path} with {len(dim_team_df)} unique teams.")

    return fact_df


def process_matches(matches_raw_path: Path, clean_dir: Path, fact_df: pd.DataFrame | None = None) -> None:
    """
    Optional matches support:
    Processes matches.csv if present, prints column names, standardizes teams,
    calculates toss_winner_won_match and bat_first_won, and saves dim_matches.csv.
    """
    if not matches_raw_path.exists():
        print(f"Optional matches file not found at {matches_raw_path}. Skipping dim_matches creation.")
        return

    print(f"\nProcessing matches file: {matches_raw_path}")
    matches_df = pd.read_csv(matches_raw_path, low_memory=False)
    print("Matches CSV columns found:", list(matches_df.columns))

    # Rename "id" to "match_id" if needed
    if "id" in matches_df.columns and "match_id" not in matches_df.columns:
        matches_df = matches_df.rename(columns={"id": "match_id"})

    # Standardize team names in team1, team2, toss_winner, winner
    for col in ["team1", "team2", "toss_winner", "winner"]:
        if col in matches_df.columns:
            matches_df[col] = standardize_team_names(matches_df[col].astype(str).str.strip())

    # Toss winner won match flag
    if "toss_winner" in matches_df.columns and "winner" in matches_df.columns:
        matches_df["toss_winner_won_match"] = np.where(
            matches_df["toss_winner"] == matches_df["winner"], 1, 0
        )

    # Determine team batting first and bat_first_won
    # Approach 1: Check toss_decision (bat / field)
    # Approach 2: Cross-reference inning 1 batting team from fact_df if available
    bat_first_team = None
    if "toss_decision" in matches_df.columns and "toss_winner" in matches_df.columns:
        toss_dec = matches_df["toss_decision"].astype(str).str.strip().str.lower()
        # If toss winner chose bat -> toss winner batted first
        # If toss winner chose field -> the other team batted first
        other_team = np.where(
            matches_df["toss_winner"] == matches_df["team1"],
            matches_df["team2"],
            matches_df["team1"],
        )
        bat_first_team = np.where(toss_dec == "bat", matches_df["toss_winner"], other_team)
    elif fact_df is not None and "match_id" in matches_df.columns:
        # Determine from ball-by-ball delivery data
        inning1_teams = (
            fact_df[fact_df["inning"] == 1]
            .groupby("match_id")["batting_team"]
            .first()
            .to_dict()
        )
        bat_first_team = matches_df["match_id"].map(inning1_teams)

    if bat_first_team is not None and "winner" in matches_df.columns:
        matches_df["bat_first_won"] = np.where(
            matches_df["winner"] == bat_first_team, 1, 0
        )
    else:
        print("Could not determine team batting first; bat_first_won not computed.")

    clean_dir.mkdir(parents=True, exist_ok=True)
    dim_matches_path = clean_dir / "dim_matches.csv"
    matches_df.to_csv(dim_matches_path, index=False)
    print(f"Saved: {dim_matches_path} with {len(matches_df):,} matches.")


def validate_metrics(df: pd.DataFrame) -> None:
    """Print validation metrics to compare against expectations."""
    print("\n" + "=" * 60)
    print("VALIDATION METRICS")
    print("=" * 60)

    total_rows = len(df)
    total_matches = df["match_id"].nunique()
    print(f"Total Rows:    {total_rows:,} (Expected: ~260,759)")
    print(f"Total Matches: {total_matches:,} (Expected: 1,095)")

    # 1. Virat Kohli validation
    # Runs: batsman_runs sum
    # Strike rate: batsman_runs / batter_ball_flag sum * 100
    kohli_df = df[df["batter"] == "V Kohli"]
    kohli_runs = kohli_df["batsman_runs"].sum()
    kohli_balls = kohli_df["batter_ball_flag"].sum()
    kohli_sr = (kohli_runs / kohli_balls * 100) if kohli_balls > 0 else 0
    print(f"\nV Kohli:")
    print(f"  Runs:        {kohli_runs:,} (Expected: ~8,004)")
    print(f"  Balls Faced: {kohli_balls:,}")
    print(f"  Strike Rate: {kohli_sr:.2f} (Expected: ~132)")

    # 2. JJ Bumrah validation
    # Wickets: bowler_wicket_flag sum
    # Economy: bowler_runs / legal_ball_flag sum * 6
    bumrah_df = df[df["bowler"] == "JJ Bumrah"]
    bumrah_wickets = bumrah_df["bowler_wicket_flag"].sum()
    bumrah_runs = bumrah_df["bowler_runs"].sum()
    bumrah_legal_balls = bumrah_df["legal_ball_flag"].sum()
    bumrah_econ = (bumrah_runs / bumrah_legal_balls * 6) if bumrah_legal_balls > 0 else 0
    print(f"\nJJ Bumrah:")
    print(f"  Wickets:     {bumrah_wickets} (Expected: ~165)")
    print(f"  Runs Conc:   {bumrah_runs:,}")
    print(f"  Legal Balls: {bumrah_legal_balls:,} ({bumrah_legal_balls / 6:.1f} overs)")
    print(f"  Economy:     {bumrah_econ:.2f} (Expected: ~7.3)")

    # 3. League-wide economy by phase
    print("\nLeague-wide Economy / Run Rate by Phase (Expected: Powerplay ~7.85, Middle ~7.79, Death ~9.96):")
    phase_stats = df.groupby("phase").agg(
        bowler_runs=("bowler_runs", "sum"),
        total_runs=("total_runs", "sum"),
        legal_balls=("legal_ball_flag", "sum"),
    )
    phase_stats["overall_run_rate"] = (phase_stats["total_runs"] / phase_stats["legal_balls"]) * 6
    phase_stats["bowler_economy"] = (phase_stats["bowler_runs"] / phase_stats["legal_balls"]) * 6
    for phase in ["Powerplay", "Middle", "Death"]:
        if phase in phase_stats.index:
            rr = phase_stats.loc[phase, "overall_run_rate"]
            be = phase_stats.loc[phase, "bowler_economy"]
            print(f"  {phase:10s}: {rr:.2f} (overall run rate / league economy) | {be:.2f} (bowler economy)")

    print("=" * 60 + "\n")


def main() -> None:
    root = get_project_root()
    raw_dir = root / "data" / "raw"
    clean_dir = root / "data" / "clean"

    deliveries_path = raw_dir / "deliveries.csv"
    fact_df = process_deliveries(deliveries_path, clean_dir)

    matches_path = raw_dir / "matches.csv"
    process_matches(matches_path, clean_dir, fact_df)

    validate_metrics(fact_df)


if __name__ == "__main__":
    main()
