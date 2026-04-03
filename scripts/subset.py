import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/subsets/20_users")
OUT.mkdir(parents=True, exist_ok=True)

users_all = pd.read_csv(RAW / "users.csv")
chosen = (users_all["user_id"]
          .dropna()
          .drop_duplicates()
          .sample(n=20, random_state=42))
chosen.to_csv(OUT / "selected_users.csv", index=False)

def filter_log(filename, user_col="user"):
    out_file = OUT / filename
    out_file.unlink(missing_ok=True)
    for chunk in pd.read_csv(RAW / filename, chunksize=1_000_000):
        keep = chunk[chunk[user_col].isin(chosen)]
        if not keep.empty:
            mode = "a" if out_file.exists() else "w"
            header = not out_file.exists()
            keep.to_csv(out_file, mode=mode, header=header, index=False)

for name in ["logon.csv", "email.csv", "file.csv", "device.csv", "http.csv"]:
    filter_log(name)

users_all[users_all["user_id"].isin(chosen)].to_csv(OUT / "users.csv", index=False)
pd.read_csv(RAW / "psychometric.csv").query("user_id in @chosen").to_csv(
    OUT / "psychometric.csv", index=False
)