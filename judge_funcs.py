# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 17:41:50 2025

@author: Ziven Ryzhkov
"""
# judge_funcs.py
from HISstruct import other_diag_code_cols
from HISstruct import main_operation_code_col
from HISstruct import other_operation_code_cols
import re  
import math
import datetime

def judge_sex(val):
    """性别：1-男 2-女 0-未知 9-未说明"""
    return str(val).strip() in ('1', '2', '0', '9')

def judge_marry(val):
    """婚姻状况：1-未婚 2-已婚 3-丧偶 4-离婚 9-其他"""
    return str(val).strip() in ('1', '2', '3', '4', '9')

def judge_occupation(val):
    RC003 = {'11','13','17','21','24','27','31','37','51','54','70','80','90'}
    return str(val).strip() in RC003

def judge_nation(val):
    """
    判定民族代码（RC035）是否合法：
    - 1~56（所有民族），66（其他），99（外籍人士）为合格
    - 允许字符串数字，空/无效为不合格
    """
    s = str(val).strip()
    if not s.isdigit():
        return False
    v = int(s)
    return (1 <= v <= 56) or v == 66 or v == 99

def judge_date(val):
    """
    判定日期是否合法，自动兼容常见格式、date/datetime对象等
    """
    from datetime import datetime, date
    import pandas as pd

    # 空或NaN直接不合格
    if val is None or (isinstance(val, float) and pd.isnull(val)):
        return False
    # 如果本身就是date/datetime对象，直接合格
    if isinstance(val, (datetime, date)):
        return True
    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "null"}:
        return False

    # 常见格式尝试
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y%m%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y.%m.%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            datetime.strptime(s, fmt)
            return True
        except:
            continue
    return False

def judge_age(val):
    """年龄：正数且不大于120"""
    try:
        v = float(val)
        return v > 0 and v <= 120
    except:
        return False

def judge_idcard(val):
    """
    身份证号判定：必须15/18位，空/占位符/科学记数/不可见字符一律不合格
    """
    EMPTY = {"", None, "-", "—", "null", "none"}
    # 1. 原始判空
    if val is None:
        return False
    # 2. 去字符串化，剔除全角空格和各种不可见符
    s = str(val).strip().replace('\u3000', '').replace('\xa0', '').replace(' ', '').upper()
    # 3. 空/占位符一律算不合格
    if s.lower() in EMPTY or s == "":
        return False
    # 4. 科学记数：尝试还原
    sci_match = re.match(r"^(\d+\.?\d*)e[+]?(\d+)$", s, re.I)
    if sci_match:
        try:
            s = '{:.0f}'.format(float(s))
        except:
            return False
    # 5. 尾部“.0”特殊清理
    if s.endswith('.0') and s[:-2].isdigit():
        s = s[:-2]
    # 6. 去掉所有非数字和X（如全角数字替换、异常字符清除）
    s = ''.join([c if c.isdigit() or c == 'X' else '' for c in s])
    # 7. 判15/18位格式
    if len(s) == 15 and s.isdigit():
        return True
    if len(s) == 18 and (s[:-1].isdigit() and (s[-1].isdigit() or s[-1] == 'X')):
        return True
    return False

def judge_phone(val):
    """手机号：11位数字"""
    s = str(val).strip()
    return s.isdigit() and len(s) == 11

def judge_postcode(val):
    """邮编：6位数字"""
    s = str(val).strip()
    return s.isdigit() and len(s) == 6

def judge_pay(val):
    """医疗付费方式：见RC032，这里校验是数字或小数点、最大长度5"""
    s = str(val).strip()
    return (s.replace('.', '').isdigit() and 1 <= len(s) <= 5)

def judge_blood(val):
    """ABO血型：1-6"""
    return str(val).strip() in ('1', '2', '3', '4', '5', '6')

def judge_rh(val):
    """Rh标识：1-4"""
    return str(val).strip() in ('1', '2', '3', '4')

def judge_insure(val):
    """健康卡号/医保号：只要非空"""
    return bool(str(val).strip())

def judge_text_notnull(val):
    """通用必填文本项（需非空，且不是常见占位符）"""
    EMPTY = {"", None, "-", "—", "null", "Null", "NULL", "none", "None"}
    # 转成字符串、去掉前后空格再统一小写
    s = str(val).strip().lower()
    # 判断特殊情况：空/常见占位符/全是空白
    if s in EMPTY or s == "":
        return False
    # 可以根据需要扩展 NaN 检查
    try:
        if isinstance(val, float) and math.isnan(val):
            return False
    except Exception:
        pass
    return True

def judge_optimal(val):
    """无论填写与否，都算合规，直接通过。"""
    return True

def judge_code_yn(val):
    """判断代码（1-是，2-否）"""
    return str(val).strip() in ('1', '2')

def is_newborn(record):
    """
    判定是否为新生儿：
    1. 若有A16年龄不足一周岁的年龄（天），且为数值且≤28，判为新生儿
    2. 否则，出生日期-入院日期≤28天且A14年龄≤1，判为新生儿
    """
    # 优先A16
    try:
        days = int(str(record.get('A16年龄不足一周岁的年龄（天）', '')).strip())
        if 0 <= days <= 28:
            return True
    except:
        pass

    # 兜底：出生日期与入院日期
    try:
        age = float(record.get('A14年龄', 99))
        if age > 1:
            return False
        birth_date = str(record.get('A13出生日期', '')).strip()
        admit_date = str(record.get('B12入院时间', '')).strip()
        if not birth_date or not admit_date:
            return False
        dt_birth = datetime.strptime(birth_date, '%Y-%m-%d')
        dt_admit = datetime.strptime(admit_date, '%Y-%m-%d')
        delta_days = (dt_admit - dt_birth).days
        return 0 <= delta_days <= 28
    except:
        return False

def judge_newborn_weight(record):
    """
    新生儿体重评分项判定：
    - 只针对新生儿（is_newborn为True）判定，否则直接通过
    - 新生儿入院体重、出生体重两项任一合格即可，都空或都不合格才算不合格
    """
    if not is_newborn(record):
        return True  # 非新生儿不判定

    admit_weight = str(record.get('A17新生儿入院体重（克）', '')).strip()
    birth_weight = str(record.get('A18x01新生儿出生体重（克）', '')).strip()

    admit_ok = False
    birth_ok = False

    if admit_weight:
        try:
            w = float(admit_weight)
            admit_ok = (500 <= w <= 10000)
        except:
            pass

    if birth_weight:
        try:
            w = float(birth_weight)
            birth_ok = (500 <= w <= 5000)
        except:
            pass

    return admit_ok or birth_ok

def judge_province(val):
    """
    判定A23C籍贯省是否合法（见RC036省市区代码表）
    允许1~35的整数，字符串也兼容
    """
    try:
        s = str(val).strip()
        if not s.isdigit():
            return False
        v = int(s)
        return 1 <= v <= 35
    except:
        return False

def judge_dept(val):
    """
    判定科别代码是否合法（见RC023科别代码表）
    - 有效代码为01-52、69，及其后续扩展（如0301、040101等，前缀正确即可）
    - 允许字符串/数字
    """
    s = str(val).strip()
    if not s:
        return False

    # 先判断是否为纯数字或前导零数字（如01、02、21、5001、69）
    # 允许长度2（如01-52、69）或更长（如0301、040101、5008等）
    if not s.isdigit():
        return False

    # 两位主科代码
    main_code = int(s[:2])
    if (1 <= main_code <= 52) or main_code == 69:
        return True
    return False

def judge_contact_relation(val):
    """
    判定联系人关系字段是否合规（RC033代码表）
    有效值为字符串数字 '0' ~ '9'
    """
    valid_codes = {str(i) for i in range(10)}  # '0'到'9'
    s = str(val).strip()
    return s in valid_codes

def judge_discharge_method(val):
    """
    判定离院方式是否合法（RC019代码表）
    有效值：1~5, 9（字符串或数字均可）
    """
    valid_codes = {'1', '2', '3', '4', '5', '9'}
    s = str(val).strip()
    return s in valid_codes

def judge_readmit_plan(val):
    """
    判定是否有31天内再住院计划（RC028代码表）
    有效值：'1'（无），'2'（有），字符串或数字都兼容
    """
    valid_codes = {'1', '2'}
    s = str(val).strip()
    return s in valid_codes

def judge_admission_route(val):
    """
    判定入院途径代码是否合法（RC026代码表）
    有效值：'1', '2', '3', '9'（字符串或数字均可）
    """
    valid_codes = {'1', '2', '3', '9'}
    s = str(val).strip()
    return s in valid_codes

def judge_admission_status(val):
    """
    判定入院病情代码是否合法（RC027代码表）
    有效值：'1'（有）、'2'（临床未确定）、'3'（情况不明）、'4'（无），字符串或数字均可
    """
    valid_codes = {'1', '2', '3', '4'}
    s = str(val).strip()
    return s in valid_codes

def judge_autopsy(record):
    """
    尸检记录判定：
    1. 仅当出院方式为'5'（死亡）时，本项才需要合规校验
    2. 尸检记录仅允许'1'（是）、'2'（否），否则为不合格
    3. 非死亡病例本项自动合格
    """
    discharge_code = str(record.get('B34C离院方式', '')).strip()
    if discharge_code != '5':
        return True  # 非死亡出院，不判定该项，视为合格

    autopsy_code = str(record.get('C34C死亡患者尸检', '')).strip()
    return autopsy_code in {'1', '2'}

def judge_total_cost(val):
    """
    判定住院总费用为大于0的数字
    """
    try:
        v = float(str(val).strip())
        return v > 0
    except:
        return False

def judge_allergy_drug(record):
    """
    联合判定药物过敏字段：
    1. C24C有无药物过敏（1-无，2-有），仅2时必须C25过敏药物名称非空
    2. C24C须为'1'或'2'，否则不合格
    3. 若C24C=2，则C25须非空，否则不合格
    """
    allergy_code = str(record.get('C24C有无药物过敏', '')).strip()
    if allergy_code not in {'1', '2'}:
        return False
    if allergy_code == '2':  # 有药物过敏，必须有药物名
        drug_name = str(record.get('C25过敏药物名称', '')).strip()
        return bool(drug_name)
    return True  # 无药物过敏，不要求药物名

def judge_transfer_dept(val):
    """
    判定转科科别（B21C）：
    - 允许空（''）、'-'（短横线）都视为未转科，合格
    - 有值时，必须为合法科别代码（见RC023）
    """
    s = str(val).strip()
    if not s or s == '-':
        return True  # 空或'-'均合格
    return judge_dept(s)

def judge_anesthesia_method(val):
    """
    判定麻醉方式代码（C22x01C主要手术操作麻醉方式）：
    - 允许为空（无麻醉/未手术时）/'-'/None/'nan'
    - 支持字符串、数字、数字字符串、数字带小数点等多种Excel导出格式
    - 自动补全前导零匹配代码表所有长度
    """
    import math

    valid_codes = {
        '01', '0101', '0102', '0103', '0104',
        '02', '0201', '020101', '020102', '020103',
        '0202', '020201', '020202', '020203', '020204', '020205', '020206', '020207', '020208', '020209',
        '03', '0301', '0302', '0303', '0304',
        '04', '05', '0501', '0502', '0503',
        '99'
    }

    # 1. 空/None/nan等直接合格
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True

    s = str(val).strip()
    if not s or s.lower() in {"nan", "none", "null", "-"}:
        return True

    # 2. 直接字符串匹配
    if s in valid_codes:
        return True

    # 3. 纯数字或带小数点的数字（如'102.0'），尝试转int后补零和代码表长度匹配
    if s.replace('.', '', 1).isdigit():
        try:
            num = int(float(s))
            # 生成所有可能长度的前导零字符串与代码表比对
            code_lengths = set(len(code) for code in valid_codes)
            for L in code_lengths:
                code_candidate = str(num).zfill(L)
                if code_candidate in valid_codes:
                    return True
        except Exception as e:
            print(f"[DEBUG] judge_anesthesia_method异常: {e}, 原值: {s}")
            pass

    # 4. 其它格式全部不合格
    return False

def judge_main_diag_code(row):
    """
    判定主诊断编码（C03C出院主要诊断编码）是否合规。
    合规标准见《逻辑校验规则》
    """
    # 1. 必填校验
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if not main_code:
        return False

    # 2. 结构化获取“其他诊断编码”所有列
    other_codes = [
        str(row.get(col, '')).strip()
        for col in other_diag_code_cols
        if str(row.get(col, '')).strip()
    ]

    #  合规标准
    if main_code == 'K70.300' and 'K72.903' in other_codes:
        # 此时主诊断编码应为K70.404，否则不合格
        return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C91.1'):
        # C09C病理诊断编码 必须为 M9823任意数字/3
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()

        # 正则：M9823 + 任意一位数字 + /3
        if not re.fullmatch(r"M9823\d/3", pathology_code):
            return False
        
        main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 判定是否在C77-C80区间（ICD10编号字符串可直接比较）

    if re.match(r"C7[7-9]\.", main_code) or re.match(r"C80\.", main_code):
        # 动态编码即病理诊断编码的“/6”结尾
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        if not pathology_code.endswith('/6'):
            return False
        
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 只要主诊断编码以R65、U、Z37开头，直接不合格
    if main_code.startswith('R65') or main_code.startswith('Z37') or re.match(r"U\d", main_code):
        return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C90.1'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须以M9830开头+任意数字，且/3结尾
        if not re.fullmatch(r"M9830\d/3", pathology_code):
            return False
    
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 判断是否以B65.902+开头
    if main_code.startswith('B65.902+'):
        # 检查其他诊断编码
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        if 'K72.903' in other_codes:
            # 若此时主诊断编码未被合并为B65.906+开头，则不合格
            # 业务含义推断：必须以B65.906+开头
            if not main_code.startswith('B65.906+'):
                return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 主诊断为I24.901
    if main_code == 'I24.901':
        # 获取所有其他诊断编码
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 检查是否存在指定诊断
        trigger = (
            'I21.300x004' in other_codes or
            'I21.401' in other_codes or
            'I20.000' in other_codes or
            any(code.startswith('I20.') and code.endswith('00') for code in other_codes)
        )
        if trigger:
            # 发现诱因诊断仍把I24.901作为主诊断，判为不合规
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 主诊断为C50.900x011
    if main_code == 'C50.900x011':
        # 获取所有手术操作编码
        op_codes = [
            str(row.get(col, '')).strip()
            for col in other_operation_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 判断是否存在85.20~85.44区间编码
        trigger = any(re.match(r"85\.(2[0-9]|3[0-9]|4[0-4])", code) for code in op_codes)
        if trigger:
            # 发现手术编码属于该区间，主诊断不得为C50.900x011
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'O82':
        # 获取所有手术及操作编码
        op_codes = [
            str(row.get(col, '')).strip()
            for col in other_operation_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 必须包含以74开头的编码
        has_74 = any(code.startswith('74') for code in op_codes)
        if not has_74:
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 主诊断为I20%或I25%
    if main_code.startswith('I20') or main_code.startswith('I25'):
        # 收集所有手术操作编码（主手术+其他手术）
        op_codes = [str(row.get(main_operation_code_col, '')).strip()] + [
            str(row.get(col, '')).strip() for col in other_operation_code_cols
        ]
        # 主手术操作编码
        main_op_code = str(row.get(main_operation_code_col, '')).strip()

        support_op = [code for code in op_codes if code.startswith('36.06') or code.startswith('36.07')]
        if support_op and not (main_op_code.startswith('36.06') or main_op_code.startswith('36.07')):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 判断主诊断是否以B16开头
    if main_code.startswith('B16'):
        # 获取所有其他诊断编码
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 如果存在K72.903，则主诊断编码必须以B16.0或B16.2开头
        if 'K72.903' in other_codes:
            if not (main_code.startswith('B16.0') or main_code.startswith('B16.2')):
                return False
            
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 主诊断为D35.21%或D35.22%
    if main_code.startswith('D35.21') or main_code.startswith('D35.22'):
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 若其他诊断没有E22%、E24.000x001或E05.800x001，则不合格
        exist = (
            any(code.startswith('E22') for code in other_codes) or
            'E24.000x001' in other_codes or
            'E05.800x001' in other_codes
        )
        if not exist:
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 主诊断为D35.21%或D35.22%
    if main_code.startswith('D35.21') or main_code.startswith('D35.22'):
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 若其他诊断没有E22%、E24.000x001或E05.800x001，则不合格
        exist = (
            any(code.startswith('E22') for code in other_codes) or
            'E24.000x001' in other_codes or
            'E05.800x001' in other_codes
        )
        if not exist:
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code in ['Z51.103', 'Z51.102']:
        main_op_code = str(row.get(main_operation_code_col, '')).strip()
        # 必须有99.25%或86.0600x004
        if not (main_op_code.startswith('99.25') or main_op_code == '86.0600x004'):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('D25.'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须全等于M88900/0
        if pathology_code != 'M88900/0':
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'K72.903':
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 存在以B16开头的其他诊断
        if any(code.startswith('B16') for code in other_codes):
            # 主诊断编码必须为B16.0或B16.2开头
            if not (main_code.startswith('B16.0') or main_code.startswith('B16.2')):
                return False

    discharge_status = str(row.get('F05出院主要诊断出院情况', '')).strip()
    discharge_method = str(row.get('B34C离院方式', '')).strip()
    # 3=未愈，1=医嘱离院
    if discharge_status == '3' and discharge_method == '1':
        return False
    
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'C34.900x001':
        # 检查所有手术编码（主手术+其他手术）
        op_codes = [str(row.get(main_operation_code_col, '')).strip()] + [
            str(row.get(col, '')).strip() for col in other_operation_code_cols
        ]
        # 是否有32开头的手术编码
        if any(code.startswith('32') for code in op_codes if code):
            # 此时主诊断不能为C34.900x001
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C91.3'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须以M9825开头+任意数字+/3结尾
        if not re.fullmatch(r"M9825\d+/3", pathology_code):
            return False
        
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C91.0'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须以M9821开头+任意数字+/3结尾
        if not re.fullmatch(r"M9821\d+/3", pathology_code):
            return False
        
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 其他诊断编码
    other_codes = [
        str(row.get(col, '')).strip()
        for col in other_diag_code_cols
        if str(row.get(col, '')).strip()
    ]
    # S/T码判定
    s_t_main = main_code.startswith('S') or main_code.startswith('T')
    s_t_other = any(code.startswith('S') or code.startswith('T') for code in other_codes)
    if s_t_main or s_t_other:
        # 损伤和中毒外部原因不能为空
        external_cause = str(row.get('C12C损伤、中度外部原因编码', '')).strip()
        if not external_cause:
            return False
        
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('D46.4'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须M9980+数字/1
        if not re.fullmatch(r"M9980\d+/1", pathology_code):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'I25.103':
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 如果有其他诊断以I20开头（心绞痛），主诊断不能是I25.103
        if any(code.startswith('I20') for code in other_codes):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'K72.903':
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        if any(code.startswith('B19') for code in other_codes):
            # 必须合并为B19.000x001
            if main_code != 'B19.000x001':
                return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'Z51.811':
        main_op_code = str(row.get(main_operation_code_col, '')).strip()
        if main_op_code != '92.2801':
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # S62.802为“指骨骨折未特指部位”——不应作为主诊断
    if main_code == 'S62.802':
        return False
    
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'Z51.899':
        main_op_code = str(row.get(main_operation_code_col, '')).strip()
        # 合规主手术编码集合
        valid_codes = ['41.42001', '50.29004', '52.22004', '60.9600x001']
        if main_op_code not in valid_codes:
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 所有其他诊断编码
    other_codes = [
        str(row.get(col, '')).strip()
        for col in other_diag_code_cols
        if str(row.get(col, '')).strip()
    ]
    # 汇总所有诊断编码
    all_codes = [main_code] + other_codes
    # 检查是否同时包含B18.107和B18.200
    if 'B18.107' in all_codes and 'B18.200' in all_codes:
        # 若没有B17.800x001则不合格
        if not any(code.startswith('B17.800x001') for code in all_codes):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C43.'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # M8720~M8799 + /3  正则：M87[2-9]\d+/3
        if not re.fullmatch(r"M87[2-9]\d+/3", pathology_code):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'O80':
        # 获取所有手术操作编码（主+其他）
        op_codes = [str(row.get(main_operation_code_col, '')).strip()] + [
            str(row.get(col, '')).strip() for col in other_operation_code_cols
        ]
        # 清宫术69%或缝合术75%
        if any(code.startswith('69') or code.startswith('75') for code in op_codes if code):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C91.5'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须以M9827+数字+/3结尾
        if not re.fullmatch(r"M9827\d+/3", pathology_code):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    other_codes = [
        str(row.get(col, '')).strip()
        for col in other_diag_code_cols
        if str(row.get(col, '')).strip()
    ]
    all_codes = [main_code] + other_codes


    # 判断是否存在O80–O84编码
    has_delivery = any(re.match(r"O8[0-4]", code) for code in all_codes)
    # 判断是否无O00–O08编码
    has_abortion = any(re.match(r"O0[0-8]", code) for code in all_codes)

    if has_delivery and not has_abortion:
        # 其它诊断编码必须有分娩结局编码Z37
        if not any(code.startswith('Z37') for code in other_codes):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    # 不能直接用M08.800x091做主诊断
    if main_code == 'M08.800x091':
        return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('B15'):
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 存在K72.903时，主诊断编码必须为B15.000
        if 'K72.903' in other_codes:
            if main_code != 'B15.000':
                return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('C91.2'):
        pathology_code = str(row.get('C09C病理诊断编码', '')).strip()
        # 必须以M9822+数字+/3结尾
        if not re.fullmatch(r"M9822\d+/3", pathology_code):
            return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code.startswith('B19'):
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 存在K72.903时，主诊断编码必须为B19.000x001
        if 'K72.903' in other_codes:
            if main_code != 'B19.000x001':
                return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'K72.903':
        other_codes = [
            str(row.get(col, '')).strip()
            for col in other_diag_code_cols
            if str(row.get(col, '')).strip()
        ]
        # 存在B15%时，主诊断编码必须为B15.000
        if any(code.startswith('B15') for code in other_codes):
            if main_code != 'B15.000':
                return False

    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    if main_code == 'Z51.800x095':
        main_op_code = str(row.get(main_operation_code_col, '')).strip()
        # 必须是99.28%开头，但不能是99.2800x006
        if not (main_op_code.startswith('99.28') and main_op_code != '99.2800x006'):
            return False
        
    main_code = str(row.get('C03C出院主要诊断编码', '')).strip()
    discharge_status = str(row.get('F05出院主要诊断出院情况', '')).strip()  # F05出院情况

    # 判断主诊断是否在Z00-Z99区间
    if re.match(r"Z\d{2}", main_code):
        # 出院情况为4或"死亡"
        if discharge_status == '4' or '死亡' in discharge_status:
            return False

    # ...后续合规标准可继续追加

    return True

