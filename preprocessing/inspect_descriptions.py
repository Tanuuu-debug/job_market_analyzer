import pandas as pd


# Load cleaned dataset
df = pd.read_csv("data/cleaned_postings.csv")


print("===== SAMPLE JOB DESCRIPTIONS =====\n")

for i in range(5):
    print(f"JOB {i + 1}")
    print("Title:", df.iloc[i]["title"])
    print("Description:")
    print(df.iloc[i]["description"])
    print("\n" + "=" * 80 + "\n")