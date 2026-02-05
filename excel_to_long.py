import pandas as pd
import re

# ========================
# 1. 读取 Excel
# ========================

file_path = "deflection_raw.xlsx"

xls = pd.ExcelFile(file_path)

print("Sheets:", xls.sheet_names)


all_data = []


# ========================
# 2. 单 sheet 处理函数
# ========================

def process_sheet(sheet_name, arch_id):

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=[0, 1]
    )

    # 修正 Angle 列
    df.columns = [
        ("Angle", "") if "Angle" in str(c[0]) else c
        for c in df.columns
    ]


    # 重命名
    new_cols = []

    for col in df.columns:

        if col[0] == "Angle":
            new_cols.append("Angle")

        else:
            measure = col[0]
            method = col[1]

            trial = int(measure.replace("Measure", ""))

            new_cols.append(f"T{trial}_{method}")

    df.columns = new_cols


    # Wide → Long
    df_long = df.melt(
        id_vars="Angle",
        var_name="Trial_Method",
        value_name="Deflection"
    )

    df_long[["Trial", "Method"]] = df_long["Trial_Method"].str.extract(
        r"T(\d+)_(AMO|ASTM)"
    )

    df_long["Trial"] = df_long["Trial"].astype(int)

    df_long = df_long.drop(columns="Trial_Method")


    # 加 Arch
    df_long["Arch"] = arch_id


    return df_long[
        ["Arch", "Angle", "Trial", "Method", "Deflection"]
    ]


# ========================
# 3. 只处理前10个 Sheet
# ========================

for sheet in xls.sheet_names[:10]:

    print("Processing:", sheet)

    # 从 Arch#1 提取 1
    match = re.search(r"\d+", sheet)

    if match:
        arch_id = int(match.group())
    else:
        print(f"Warning: Cannot find number in {sheet}")
        continue


    df_one = process_sheet(sheet, arch_id)

    all_data.append(df_one)


# ========================
# 4. 合并 + 保存
# ========================

final_df = pd.concat(all_data, ignore_index=True)

final_df.to_csv("deflection_long.csv", index=False)

print("Done. Saved as deflection_long.csv")
print(final_df.head(20))