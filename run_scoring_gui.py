# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 11:13:49 2025

@author: Ziven Ryzhkov
"""

# run_scoring_gui.py
import pandas as pd
import inspect
from tkinter import Tk, filedialog, messagebox
import judge_funcs
from HISstruct import pdf_struct

def is_row_func(judge_func):
    params = list(inspect.signature(judge_func).parameters)
    return len(params) == 1 and params[0] in ["row", "record"]

JUDGE_FUNC_MAP = {fn: getattr(judge_funcs, fn) for fn in dir(judge_funcs) if fn.startswith('judge_')}

D_CAP_DICT = {
    '患者基本信息': 4,
    '住院过程信息': 0,
    '诊疗信息': 3,
    '费用信息': 2,
}

def score_all_rows(hqms_df, mapping_df):
    results = []

    for idx, row in hqms_df.iterrows():
        record = {'健康卡号': row.get('A47健康卡号', '')}
        total_score = 100
        deduct_items = []
        d_section_cap = {}

        for _, item in mapping_df.iterrows():
            name = item['评分项目']
            sec, cat = pdf_struct.get(name, ("其他", "其他"))
            score_col = f"{sec}|{cat}|{name}"
            full_score = item['分值']
            hqms_cols = str(item['实际系统内表头']).split(',')
            vals = [row.get(col.strip(), None) for col in hqms_cols]

            func_name = item.get('判定函数', '').strip() if '判定函数' in item else ''
            judge_func = JUDGE_FUNC_MAP.get(func_name) if func_name else None

            if judge_func is not None and func_name == 'judge_optimal':
                is_valid = True
            elif judge_func:
                if is_row_func(judge_func):
                    is_valid = judge_func(row)
                else:
                    is_valid = any(judge_func(val) for val in vals)
            else:
                is_valid = any(not (pd.isnull(val) or str(val).strip() == '') for val in vals)

            if cat == 'D':
                if sec not in d_section_cap:
                    d_section_cap[sec] = 0
                if not is_valid:
                    d_section_cap[sec] += full_score
                    record[score_col] = 0
                    deduct_items.append(score_col)
                else:
                    record[score_col] = full_score
            else:
                if not is_valid:
                    record[score_col] = 0
                    deduct_items.append(score_col)
                    total_score -= full_score
                else:
                    record[score_col] = full_score

        for sec, v in d_section_cap.items():
            cap = D_CAP_DICT.get(sec, 999)
            total_score -= min(v, cap)

        record['总分'] = max(total_score, 0)
        record['扣分项'] = ','.join(deduct_items)
        results.append(record)

    return pd.DataFrame(results)

def main():
    # 主窗口后台运行，不显示也不弹多余框
    root = Tk()
    root.withdraw()

    # 直接弹出选择评分标准
    mapping_path = filedialog.askopenfilename(
        title="请选择评分标准（表头映射）Excel文件",
        filetypes=[("Excel Files", "*.xlsx *.xls")],
        parent=root
    )
    if not mapping_path:
        root.destroy()
        return

    # 直接弹出选择HQMS原始数据
    hqms_path = filedialog.askopenfilename(
        title="请选择HQMS病案明细Excel文件",
        filetypes=[("Excel Files", "*.xlsx *.xls")],
        parent=root
    )
    if not hqms_path:
        root.destroy()
        return

    try:
        mapping = pd.read_excel(mapping_path)
        hqms = pd.read_excel(hqms_path)
    except Exception as e:
        messagebox.showerror("读取错误", f"读取Excel文件失败:\n{e}", parent=root)
        root.destroy()
        return

    result_df = score_all_rows(hqms, mapping)

    output_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        title="保存评分结果",
        filetypes=[("Excel Files", "*.xlsx")],
        parent=root
    )
    if not output_path:
        root.destroy()
        return

    try:
        result_df.to_excel(output_path, index=False)
        messagebox.showinfo("完成", f"评分完成，结果已保存至：\n{output_path}", parent=root)
    except Exception as e:
        messagebox.showerror("保存错误", f"保存文件失败:\n{e}", parent=root)

    # ✅ 彻底退出窗口
    root.destroy()

if __name__ == "__main__":
    main()
