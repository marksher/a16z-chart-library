"""Table chart — Plotly default theme (theme=None)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../..", "scripts"))
import pandas as pd
from a16z_charts import table, save_png

OUT = os.path.dirname(__file__)

df = pd.DataFrame({
    "Company": ["Salesforce", "HubSpot", "Zendesk", "Notion", "GitHub", "Slack"],
    "AI Packaging": ["Add-on > core", "Core", "Add-on", "Add-on > core", "Core", "Core"],
    "Billing": ["Subscription > hybrid", "Hybrid", "Usage", "Subscription", "Subscription", "Subscription"],
})
fig = table(df, title="SaaS AI Pricing Strategies", source="Public pricing pages",
            highlight_rows=[0, 3], theme=None)
save_png(fig, os.path.join(OUT, "table.png"))
fig.write_html(os.path.join(OUT, "table.html"))
print("table.png written")
