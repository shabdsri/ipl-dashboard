# IPL Analytics Power BI Dashboard (2008–2024)

An end-to-end data analytics and business intelligence project exploring 17 seasons of Indian Premier League (IPL) cricket history. The pipeline processes over 260,000 ball-by-ball delivery records using Python and pandas into optimized dimensional star-schema tables for analysis and reporting in Power BI Desktop.

---

## Business Questions

This project explores key analytical questions in modern T20 cricket:
1. **Strike Rate vs. Economy**: How do premier batters balance scoring acceleration with risk, and which bowlers consistently suppress run rates across match situations?
2. **Phase Dynamics (Powerplay vs. Middle vs. Death)**: How do team scoring trajectories, boundary rates, and bowling economies shift across the three distinct innings phases?
3. **Toss Impact & Match Outcomes**: Does winning the coin toss or electing to bat/field first confer a measurable win-probability advantage across venues and tournament editions?

---

## Data Source

- **Dataset**: Kaggle IPL Complete Dataset (2008–2024) ball-by-ball delivery data.
- **Raw Files**: Raw data (`deliveries.csv` and optional `matches.csv`) is not tracked in version control due to file size constraints.
- **Download Instructions**:
  > *[Placeholder: Add Kaggle dataset download link and extraction instructions here]*
  >
  > Place `deliveries.csv` (and optionally `matches.csv`) into the `data/raw/` directory before running the data pipeline.

---

## How to Reproduce

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/ipl-dashboard.git
   cd ipl-dashboard
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add Raw Data**:
   Ensure `data/raw/deliveries.csv` is present.

5. **Run the Data Preparation Pipeline**:
   ```bash
   python scripts/prepare_data.py
   ```
   This generates:
   - `data/clean/fact_deliveries.csv`: Cleaned ball-by-ball facts with engineered flags and phases.
   - `data/clean/dim_team.csv`: Standardized franchise dimension.
   - `data/clean/dim_matches.csv` (if `matches.csv` is present).

6. **Open Dashboard**:
   Load the cleaned CSVs into Power BI Desktop and follow the measures defined in [`docs/dax_measures.md`](docs/dax_measures.md).

---

## Data Model

*[Placeholder: Insert data model diagram / star schema screenshot showing relationships between Fact_Deliveries, Dim_Team, and Dim_Matches]*

---

## Dashboard Screenshots

*[Placeholder: Insert high-resolution screenshots of Power BI report pages (Overview, Batting Analysis, Bowling Analysis, Phase Breakdown, Head-to-Head)]*

---

## Key Insights

*[Placeholder: Key analytical findings and strategic takeaways to be added after dashboard analysis]*

---

## Tools Used

- **Python 3.12**: Environment scripting and orchestration
- **pandas**: Vectorized data transformation, feature engineering, and cleaning
- **Power BI Desktop**: Data modeling, interactive visualization, and dashboard design
- **DAX (Data Analysis Expressions)**: Custom dynamic business measures and time/phase aggregations
- **Git & GitHub**: Version control and project documentation
