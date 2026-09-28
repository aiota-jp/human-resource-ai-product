# create_test_excel.py
"""テスト用Excelファイルを作成するスクリプト"""
import pandas as pd

# 社員台帳テスト
employee_data = {
    "社員番号": ["EMP001", "EMP002", "EMP003"],
    "氏名": ["山田太郎", "鈴木花子", "田中一郎"],
    "部署": ["人事部", "研修部", "営業部"],
    "役職": ["主任", "担当", "係長"],
    "入社日": ["2020-04-01", "2021-04-01", "2019-04-01"],
}
df_emp = pd.DataFrame(employee_data)
df_emp.to_excel("test_employee.xlsx", index=False)
print("test_employee.xlsx を作成しました")

# 研修結果テスト
training_data = {
    "社員番号": ["EMP001", "EMP002", "EMP003"],
    "氏名": ["山田太郎", "鈴木花子", "田中一郎"],
    "出席率": [100, 90, 85],
    "理解度": [85, 70, 75],
    "課題スコア": [95, 80, 70],
}
df_tr = pd.DataFrame(training_data)
df_tr.to_excel("test_training_result.xlsx", index=False)
print("test_training_result.xlsx を作成しました")
