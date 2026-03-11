# EHR_QC
Eeletronic health record quality control related
CN_ver
HQMS住院病案首页评分系统  
版本：v1.0 Alpha  
作者：刘强森 
日期：2025年8月
邮箱：liu_qiangsen@outlook.com 
==========================================
📌 简介：
本工具用于自动化评估医院HQMS系统导出的住院病案首页数据质量，依据国家《住院病案首页数据质量评分标准（2016年印刷）》逐条打分，并输出结构化评分结果表格，适用于病案科、信息科、质控科等。

无需安装Python环境，双击运行评分程序后按提示操作即可。

==========================================
🚀 使用步骤：
1️⃣ 双击运行 “HQMS评分系统.exe”

2️⃣ 程序将依次弹出两个文件选择窗口：

    ① 请选择评分标准Excel表（通常为 “A评分标准-表头映射表EX.xlsx”）
    ② 请选择病案首页明细数据（HQMS导出的xlsx文件）

3️⃣ 程序自动进行评分，约几秒~几十秒取决于病案数量

4️⃣ 弹出保存窗口，选择保存路径与文件名，结果保存为Excel表格（宽表格式）

==========================================
📤 输出内容说明：
输出文件为结构化宽表，包含以下字段：

- 健康卡号：用于标识病人唯一性
- Section|类别|评分项：每项评分结果（满分/0分）
- 总分：满分100，扣除不合规项得分
- 扣分项：所有不合格的评分项名称，逗号分隔

示例输出文件名：
评分结构化宽表输出.xlsx

==========================================
📁 示例文件说明：
- A评分标准-表头映射表EX.xlsx：评分规则映射表（手工维护）
- HQMSTS202501.xlsx：医院信息科导出的原始数据（模拟）
- logo.ico：系统图标（仅用于打包）

==========================================
⚠ 注意事项：
- 本程序仅支持 Excel 文件（.xlsx/.xls），不支持 CSV
- 请确保HQMS文件字段名称与评分标准中的“实际系统内表头”一致
- 推荐使用 UTF-8 编码保存Excel（避免乱码）
- 程序不会对原始数据做任何修改，只读取和评分

==========================================
🛠 技术支持：
如需定制开发、评分规则升级、导出模板对接、数据自动上传等服务，请联系作者：

 
邮箱：liu_qiangsen@outlook.com 
GitHub主页：https://github.com/neku-oss

本程序已申请软件著作权保护，严禁擅自盗用及商业贩卖。

==========================================


EN_ver
HQMS Inpatient Front Page Scoring System

Version: v1.0 Alpha

Author: 刘强森

Date: August 2025

==========================================

📌 Overview:

This tool is designed to automatically evaluate the data quality of inpatient front page records exported from HQMS systems, based on the national standard:  
"Data Quality Scoring Criteria for Inpatient Front Page (2016 Edition)".

It outputs a structured scoring table and is suitable for use by departments such as Medical Records, IT, and Quality Control.

No Python environment is required. Simply double-click to run the scoring program and follow the prompts.

==========================================

🚀 Usage Steps:

1️⃣ Double-click to run `HQMS评分系统.exe`

2️⃣ The program will prompt you to select two files in order:

    ① The scoring criteria Excel file  
       (usually named "A评分标准-表头映射表EX.xlsx")

    ② The inpatient front page data file  
       (exported from HQMS, in `.xlsx` format)

3️⃣ The program will run the scoring process automatically.  
    Duration ranges from a few seconds to a few dozen seconds depending on the number of records.

4️⃣ A save window will pop up. Choose where to save the output Excel file (wide-format table).

==========================================

📤 Output File Description:

The output is a structured wide-format Excel file with the following fields:

- Patient ID (Health Card Number): uniquely identifies each patient

- Section|Category|Scoring Item: individual item score (full or zero)

- Total Score: out of 100 points, deducting for non-compliant items

- Deducted Items: list of all failed scoring item names, separated by commas

Example output filename:  
`Structured_Scoring_Output.xlsx`

==========================================

📁 Included Sample Files:

- `A评分标准-表头映射表EX.xlsx`: The scoring criteria mapping sheet (manually maintained)

- `HQMSTS202501.xlsx`: Example data exported by hospital IT (simulated)

- `logo.ico`: System icon (used during packaging)

==========================================

⚠ Notes:

- Only Excel files (.xlsx/.xls) are supported (CSV not supported)

- Make sure HQMS field names match the "actual field names in system" in the scoring sheet

- UTF-8 encoding is recommended for Excel files to avoid garbled characters

- The program does not modify original data—it only reads and scores

==========================================

🛠 Technical Support:

For custom development, scoring rules upgrades, export template integration, or automated data upload solutions, please contact:

GitHub: https://github.com/neku-oss

This software is protected by copyright.  
Unauthorized commercial use or redistribution is strictly prohibited.

==========================================
