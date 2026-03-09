import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from scipy import stats
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ============================================================
# 設定頁面配置
# ============================================================
st.set_page_config(
    page_title="MLB薪資表現分析儀表板",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 自定義CSS樣式
# ============================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
    }
    .section-title {
        font-size: 1.8rem;
        color: #3B82F6;
        border-bottom: 3px solid #3B82F6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .info-box {
        background-color: #f0f9ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 20px;
    }
    .formula-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #10B981;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 標題區域
# ============================================================
st.markdown('<h1 class="main-title">⚾ MLB球員薪資與表現分析儀表板</h1>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: #6B7280; margin-bottom: 2rem;">
    <p style="font-size: 1.1rem;">計量經濟學與財務分析專題：檢驗MLB薪資市場效率性</p>
    <p style="font-size: 0.9rem;">最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 數據載入函數 (Streamlit Cloud 相容版)
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    """從 GitHub 倉庫相對路徑載入數據，並執行 B 版本完整預處理"""
    try:
        # 1. 獲取當前執行腳本的目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. 定義在 GitHub 上可能存放數據的路徑 (按優先順序搜尋)
        possible_paths = [
            os.path.join(current_dir, "data", "merged_performance_salary.csv"),
            os.path.join(current_dir, "data", "processed", "merged_performance_salary.csv"),
            os.path.join(current_dir, "merged_performance_salary.csv"),
            os.path.join(current_dir, "notebooks", "data", "processed", "merged_performance_salary.csv")
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                # st.success(f"✅ 找到數據檔案: {path}") # 除錯用，確認後可註解掉
                break
        
        if data_path is None:
            st.error("❌ 找不到數據檔案：請確認 'merged_performance_salary.csv' 已上傳至 GitHub 倉庫。")
            st.info("建議路徑：`/data/merged_performance_salary.csv` 或與 `dashboard.py` 同層級。")
            return None
            
        # 3. 讀取數據
        df = pd.read_csv(data_path)
        
        # 4. 數據預處理 (B版本邏輯)
        if 'value_ratio' not in df.columns and 'WAR' in df.columns and 'Salary_millions' in df.columns:
            df['value_ratio'] = df['WAR'] / df['Salary_millions']
        
        # 標準化欄位名稱
        column_mapping = {}
        if 'Team' not in df.columns:
            for col in ['Team_performance', 'Team_salary', 'team', 'TEAM']:
                if col in df.columns:
                    column_mapping[col] = 'Team'; break
        if 'Position' not in df.columns:
            for col in ['Position_salary', 'position', 'Pos', 'POS']:
                if col in df.columns:
                    column_mapping[col] = 'Position'; break
        if 'Name' not in df.columns:
            for col in ['Name_clean', 'Player', 'Player_formatted', 'player']:
                if col in df.columns:
                    column_mapping[col] = 'Name'; break
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
            
        if 'Team' in df.columns:
            df = df[df['Team'] != '---']
            df = df.dropna(subset=['Team'])
            df['Team'] = df['Team'].astype(str)
            
        # 守備位置代碼轉換
        pos_map = {
            1: 'P', '1': 'P', '1.0': 'P',
            2: 'C', '2': 'C', '2.0': 'C',
            3: '1B', '3': '1B', '3.0': '1B',
            4: '2B', '4': '2B', '4.0': '2B',
            5: '3B', '5': '3B', '5.0': '3B',
            6: 'SS', '6': 'SS', '6.0': 'SS',
            7: 'LF', '7': 'LF', '7.0': 'LF',
            8: 'CF', '8': 'CF', '8.0': 'CF',
            9: 'RF', '9': 'RF', '9.0': 'RF',
            10: 'DH', '10': 'DH', 'O': 'DH'
        }
        if 'Position' in df.columns:
            df['Position'] = df['Position'].apply(lambda x: pos_map.get(x, x))

        # 5. 計算基礎財務分布指標
        if 'Salary_millions' in df.columns:
            df['salary_percentile'] = df['Salary_millions'].rank(pct=True) * 100
            df['salary_category'] = pd.qcut(df['Salary_millions'], q=4, 
                                            labels=['低薪資', '中低薪資', '中高薪資', '高薪資'])
        if 'WAR' in df.columns:
            df['war_percentile'] = df['WAR'].rank(pct=True) * 100
            df['war_category'] = pd.qcut(df['WAR'], q=4,
                                        labels=['低表現', '中低表現', '中高表現', '高表現'])
        
        # 6. 計算原創財務指標 (WVPI, RAV, MERI 等)
        df = calculate_original_financial_metrics(df)
        
        # 7. 終端機除錯訊息 (Streamlit Cloud 的日誌會顯示)
        debug_wvpi(df)
        
        return df
    
    except Exception as e:
        st.error(f"❌ 讀取數據失敗: {e}")
        return None

# 將 debug_wvpi 函數移到 load_data 函數之後
def debug_wvpi(df):
    """檢查 WVPI 的實際分佈"""
    if 'WVPI' in df.columns:
        print("=" * 50)
        print("WVPI 統計摘要:")
        print(f"最小值: {df['WVPI'].min():.2f}")
        print(f"最大值: {df['WVPI'].max():.2f}")
        print(f"平均值: {df['WVPI'].mean():.2f}")
        print(f"中位數: {df['WVPI'].median():.2f}")
        print(f"標準差: {df['WVPI'].std():.2f}")
        print("\n百分位數:")
        for p in [10, 25, 50, 75, 90, 95, 99]:
            print(f"{p}th: {df['WVPI'].quantile(p/100):.2f}")
        print("=" * 50)

# ============================================================
# 新增：原創財務指標計算函數 (依據 new_variables.md)
# ============================================================
def calculate_original_financial_metrics(df):
    """計算六個原創財務指標：WVPI, RAV, MERI, PSI, TPM, SEI"""
    
    # 檢查必要欄位
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        st.warning("⚠️ 缺少 WAR 或 Salary_millions 欄位，無法計算部分原創指標")
        return df
    
    # 2. 加權綜合價值指數 (WVPI)
    df = calculate_wvpi(df)
    
    # 3. 風險調整後價值 (RAV)
    df = calculate_rav(df)
    
    # 4. 市場效率殘差指數 (MERI)
    df = calculate_meri(df)
    
    # 5. 投資組合夏普指數 (PSI) - 需要球隊層級計算，稍後在球隊分析中進行
    
    # 6. 雙因子績效矩陣 (TPM) - 需要百分位，已在計算中
    
    # 7. 同步效率指數 (SEI) - 需要全局計算，稍後在綜合儀表板中進行
    
    return df

def calculate_wvpi(df):
    """計算加權綜合價值指數 (WVPI) - 修正版（所有項目標準化到 0-100）"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return df
    
    # 定義權重 (依據 new_variables.md 2.3 節)
    w1, w2, w3, w4 = 0.35, 0.30, 0.20, 0.15
    
    # 計算 WAR 百分位
    df['P_WAR'] = df['WAR'].rank(pct=True) * 100
    
    # 計算薪資百分位
    df['P_Salary'] = df['Salary_millions'].rank(pct=True) * 100
    
    # 計算 100 - P_Salary (相對成本項)
    df['P_Salary_inv'] = 100 - df['P_Salary']
    
    # 計算性價比 (WAR/Salary)
    df['VR'] = df['WAR'] / df['Salary_millions']
    
    # ==== 新增：標準化 WAR 和 VR 到 0-100 尺度 ====
    war_max = df['WAR'].max()
    vr_max = df['VR'].max()
    
    # 標準化 WAR (避免除以零)
    if war_max > 0:
        df['WAR_norm'] = (df['WAR'] / war_max) * 100
    else:
        df['WAR_norm'] = 0
    
    # 標準化 VR (避免除以零)
    if vr_max > 0:
        df['VR_norm'] = (df['VR'] / vr_max) * 100
    else:
        df['VR_norm'] = 0
    
    # 計算 WVPI - 使用標準化後的數值
    df['WVPI'] = (w1 * df['WAR_norm'] + 
                  w2 * df['VR_norm'] + 
                  w3 * df['P_WAR'] + 
                  w4 * df['P_Salary_inv'])
    
    # ==== 修正：根據實際分佈調整分類閾值 ====
    # 先計算 WVPI 的百分位數，用於調整整體分佈
    p25 = df['WVPI'].quantile(0.25)
    p50 = df['WVPI'].quantile(0.50)
    p75 = df['WVPI'].quantile(0.75)
    p90 = df['WVPI'].quantile(0.90)
    p95 = df['WVPI'].quantile(0.95)
    
    # 根據實際分佈設定閾值
    conditions = [
        df['WVPI'] > p90,                          # 前10% -> 頂級球星
        (df['WVPI'] > p75) & (df['WVPI'] <= p90),  # 前10-25% -> 優質球員
        (df['WVPI'] > p50) & (df['WVPI'] <= p75),  # 前25-50% -> 普通球員
        (df['WVPI'] > p25) & (df['WVPI'] <= p50),  # 後25-50% -> 效率待提升
        df['WVPI'] <= p25                           # 後25% -> 問題合約
    ]
    categories = ['頂級球星', '優質球員', '普通球員', '效率待提升', '問題合約']
    df['WVPI_category'] = np.select(conditions, categories, default='未知')
    
    return df

def calculate_rav(df):
    """計算風險調整後價值 (RAV)"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return df
    
    # 計算 WAR_min (替補球員水準) - 使用薪資低於第25百分位的球員平均WAR
    low_salary_threshold = df['Salary_millions'].quantile(0.25)
    bench_players = df[df['Salary_millions'] <= low_salary_threshold]
    WAR_min = bench_players['WAR'].mean() if len(bench_players) > 0 else 0
    
    # 計算 σ_WAR (生涯WAR標準差) - 由於無多年數據，使用近似公式
    # 使用位置平均WAR的絕對差異作為近似
    if 'Position' in df.columns:
        position_avg_war = df.groupby('Position')['WAR'].transform('mean')
        df['sigma_WAR_approx'] = np.abs(df['WAR'] - position_avg_war)
    else:
        df['sigma_WAR_approx'] = df['WAR'].std() if df['WAR'].std() > 0 else 1
    
    # 計算薪資中位數
    median_salary = df['Salary_millions'].median()
    
    # 計算 RAV
    df['RAV'] = ((df['WAR'] - WAR_min) / (df['sigma_WAR_approx'] + 1)) * (median_salary / df['Salary_millions'])
    
    # 添加 RAV 分類 (依據 new_variables.md 3.6 節)
    conditions = [
        df['RAV'] > 2.0,
        (df['RAV'] > 1.0) & (df['RAV'] <= 2.0),
        (df['RAV'] > 0) & (df['RAV'] <= 1.0),
        df['RAV'] <= 0
    ]
    categories = ['低風險高回報', '穩健型球員', '普通球員', '高風險或低於替補']
    df['RAV_category'] = np.select(conditions, categories, default='未知')
    
    return df

def calculate_meri(df, degree=4):
    """市場效率殘差指數 (MERI) - 升級為雙軌制：單一變數 vs 全維度對照"""
    df_out = df.copy()
    if 'WAR' not in df_out.columns or 'Salary_millions' not in df_out.columns:
        return df_out
    
    # --- A. 原有的單一變數 (WAR) 預期值 ---
    mask = df_out['WAR'].notna() & df_out['Salary_millions'].notna()
    X_war = df_out.loc[mask, 'WAR'].values
    y = df_out.loc[mask, 'Salary_millions'].values
    if len(X_war) > 0:
        coeffs = np.polyfit(X_war, y, degree)
        p = np.poly1d(coeffs)
        df_out.loc[mask, 'expected_salary_simple'] = np.maximum(p(X_war), 0.7)
        # 傳統 MERI
        df_out.loc[mask, 'MERI_simple'] = (df_out.loc[mask, 'Salary_millions'] - df_out.loc[mask, 'expected_salary_simple']) / df_out.loc[mask, 'expected_salary_simple'] * np.log(1 + np.abs(df_out.loc[mask, 'WAR']))

    # --- B. 新增：全維度多元模型殘差 ---
    # 這裡我們預設一組打者與投手的通用變數組合來快速計算
    try:
        # 為了計算方便，先簡單區分 P 與非 P
        for role in ['Hitter', 'Pitcher']:
            if role == 'Hitter':
                role_mask = mask & (~df_out['Position'].str.contains('P', na=False))
                cols = ['WAR', 'Age', 'Years', 'wRC+', 'Def']
            else:
                role_mask = mask & df_out['Position'].str.contains('P', na=False)
                cols = ['WAR', 'Age', 'Years']
                
            role_data = df_out[role_mask].dropna(subset=cols + ['Salary_millions']).copy()
            if len(role_data) > 10:
                role_data['Age2'] = role_data['Age']**2
                X = sm.add_constant(role_data[cols + ['Age2']].astype(float))
                y_log = np.log1p(role_data['Salary_millions'].astype(float))
                res = sm.OLS(y_log, X).fit()
                # 還原預測值
                df_out.loc[role_data.index, 'expected_salary_multi'] = np.expm1(res.fittedvalues)
                # 全維度 MERI (殘差)
                df_out.loc[role_data.index, 'MERI_ultimate'] = (df_out.loc[role_data.index, 'Salary_millions'] - df_out.loc[role_data.index, 'expected_salary_multi'])
    except:
        pass # 避免資料缺失導致整個儀表板崩潰
        
    return df_out

def calculate_team_psi(team_df, league_efficiency):
    """計算單一球隊的投資組合夏普指數 (PSI)"""
    total_war = team_df['WAR'].sum()
    total_salary = team_df['Salary_millions'].sum()
    expected_war = total_salary * league_efficiency
    excess_war = total_war - expected_war
    team_risk = team_df['WAR'].std() if len(team_df) > 1 else 1
    
    # PSI = 超額WAR / 球隊風險
    psi = excess_war / team_risk if team_risk != 0 else 0
    return psi

def calculate_sei(df):
    """計算同步效率指數 (SEI)"""
    if 'WAR' not in df.columns or 'Salary_millions' not in df.columns:
        return 0, 0, 0
    
    # 計算 WAR 與薪資的相關係數
    df_clean = df.dropna(subset=['WAR', 'Salary_millions'])
    correlation = df_clean['WAR'].corr(df_clean['Salary_millions'])
    
    # 計算薪資的基尼係數
    salaries = df_clean['Salary_millions'].values
    salaries = salaries[salaries > 0]
    
    if len(salaries) > 0:
        # 計算基尼係數
        salaries_sorted = np.sort(salaries)
        n = len(salaries_sorted)
        index = np.arange(1, n + 1)
        gini = ((2 * index - n - 1) * salaries_sorted).sum() / (n * salaries_sorted.sum())
    else:
        gini = 0
    
    # SEI = ρ × (1 - G)
    sei = correlation * (1 - gini)
    
    return correlation, gini, sei

# ============================================================
# 輔助函數 (升級：動態高次方多項式迴歸)
# ============================================================
def format_poly_equation(coeffs, var_name="WAR"):
    """將多項式係數格式化為漂亮的 LaTeX 數學方程式字串"""
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        deg = degree - i
        
        # 動態格式化：如果數字極小 (絕對值小於 0.001 且不為 0)，改用 LaTeX 科學記號
        if abs(c) < 0.001 and c != 0:
            base, exp = f"{c:.2e}".split('e')
            c_str = f"{base} \\times 10^{{{int(exp)}}}"
        else:
            c_str = f"{c:.3f}"
            
        if deg == 0:
            terms.append(f"{c_str}")
        elif deg == 1:
            terms.append(f"{c_str} \\text{{{var_name}}}")
        else:
            terms.append(f"{c_str} \\text{{{var_name}}}^{{{deg}}}")
            
    return " + ".join(terms).replace("+ -", "- ")

def calculate_polynomial_regression(x, y, degree=1):
    """計算高次方多項式迴歸"""
    try:
        # 使用 numpy 的 polyfit 進行高次擬合
        coeffs = np.polyfit(x, y, degree)
        p = np.poly1d(coeffs)
        
        y_pred = p(x)
        residuals = y - y_pred
        
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return coeffs, p, r_squared
    except Exception as e:
        st.warning(f"迴歸計算發生錯誤: {e}")
        return None, None, 0

def add_regression_line(fig, df, x_col, y_col, degree=1):
    """手動添加高次迴歸曲線到Plotly圖表"""
    try:
        x = df[x_col].dropna().values
        y = df[y_col].dropna().values
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]
        
        coeffs, p, r_squared = calculate_polynomial_regression(x, y, degree)
        
        if p is not None:
            # 創建平滑的回歸曲線數據 (100個點讓曲線平滑)
            x_range = np.linspace(x.min(), x.max(), 100)
            y_pred = p(x_range)
            
            # 防呆機制：預期薪資不能小於底薪 0.7M
            if y_col == 'Salary_millions':
                y_pred = np.maximum(y_pred, 0.7)
            
            # 添加迴歸曲線
            fig.add_trace(
                go.Scatter(
                    x=x_range,
                    y=y_pred,
                    mode='lines',
                    name=f'{degree}次方預測線 (R²={r_squared:.2f})',
                    line=dict(color='red', width=3, dash='dash' if degree==1 else 'solid'),
                    showlegend=True
                )
            )
    except Exception as e:
        pass
    
    return fig

def manual_poly_regression_stats(x, y, degree):
    """手動計算多項式回歸的統計量"""
    try:
        n = len(x)
        k = degree + 1  # 參數數量 (包含常數項)
        
        coeffs, p, r_squared = calculate_polynomial_regression(x, y, degree)
        y_pred = p(x)
        residuals = y - y_pred
        
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        
        # 調整後 R² (懲罰過多變數)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - k) if n > k else r_squared
        
        # F 統計量
        msr = (ss_tot - ss_res) / (k - 1) if k > 1 else 0
        mse = ss_res / (n - k) if n > k else 0
        f_value = msr / mse if mse != 0 else 0
        
        return {
            'coeffs': coeffs,
            'poly_obj': p,
            'r_squared': r_squared,
            'adj_r_squared': adj_r_squared,
            'f_value': f_value,
            'n': n,
            'residuals': residuals
        }
    except Exception as e:
        return None

def calculate_gini(series):
    """計算基尼係數 (0=完全平等, 1=完全不平等)"""
    # 確保數值為正
    incomes = np.sort(series.dropna().values)
    incomes = incomes[incomes > 0]
    if len(incomes) == 0: return 0
    
    n = len(incomes)
    index = np.arange(1, n + 1)
    return ((2 * index - n - 1) * incomes).sum() / (n * incomes.sum())

def plot_lorenz_curve(df, team_name="All Teams"):
    """繪製羅倫茲曲線"""
    incomes = np.sort(df['Salary_millions'].dropna().values)
    incomes = incomes[incomes > 0]
    if len(incomes) == 0: return go.Figure(), 0

    # 計算累積比例
    lorenz_curve = np.cumsum(incomes) / incomes.sum()
    lorenz_curve = np.insert(lorenz_curve, 0, 0)
    
    # 理想平等線
    x_axis = np.linspace(0, 1, len(lorenz_curve))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_axis, y=lorenz_curve,
        mode='lines', name='實際分配',
        fill='tozeroy', fillcolor='rgba(26, 35, 126, 0.2)',
        line=dict(color='#1a237e', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines', name='完全平等線',
        line=dict(dash='dash', color='#ef5350')
    ))
    
    gini = calculate_gini(df['Salary_millions'])
    
    fig.update_layout(
        title=f'{team_name} 薪資不平等分析 (Gini: {gini:.3f})',
        xaxis_title='球員累積百分比',
        yaxis_title='薪資累積百分比',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig, gini

def analyze_positional_arbitrage(df):
    """位置套利分析"""
    if 'Position' not in df.columns or 'WAR' not in df.columns:
        return None
        
    # 計算各位置平均數據
    pos_stats = df.groupby('Position').agg({
        'Salary_millions': 'mean',
        'WAR': 'mean',
        'Name': 'count'
    }).reset_index()
    
    # 過濾樣本過少的位置
    pos_stats = pos_stats[pos_stats['Name'] >= 5]
    
    # 計算每1 WAR的成本 (Cost per WAR)
    pos_stats['Cost_per_WAR'] = pos_stats['Salary_millions'] / pos_stats['WAR']
    pos_stats = pos_stats.sort_values('Cost_per_WAR')
    
    return pos_stats

def plot_player_radar(df, player_names):
    """繪製球員雷達比較圖 (使用百分位數)"""
    if not player_names: return None
    
    # 選擇要比較的指標
    metrics = ['Salary_millions', 'WAR', 'value_ratio', 'HR', 'RBI']
    labels = ['薪資', 'WAR', '性價比', '全壘打', '打點']
    
    # 新增原創指標到雷達圖
    if 'WVPI' in df.columns:
        metrics.append('WVPI')
        labels.append('WVPI')
    if 'RAV' in df.columns:
        metrics.append('RAV')
        labels.append('RAV')
    
    fig = go.Figure()
    
    for name in player_names:
        player_data = df[df['Name'] == name].iloc[0]
        
        # 為了讓雷達圖好看，我們計算該球員在全聯盟的百分位數
        values = []
        for metric in metrics:
            if metric in df.columns:
                try:
                    # 計算百分位數 (0-100)
                    percentile = stats.percentileofscore(df[metric].dropna(), player_data[metric])
                    values.append(percentile)
                except:
                    values.append(0)
            else:
                values.append(0)
        
        # 封閉雷達圖
        values.append(values[0])
        plot_labels = labels + [labels[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=plot_labels,
            fill='toself',
            name=f"{name} (PR值)"
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix='%')
        ),
        title="球員能力PR值對比 (數值為聯盟百分位數)",
        height=450
    )
    return fig

def plot_tpm_matrix(df):
    """繪製雙因子績效矩陣 (TPM)"""
    if 'war_percentile' not in df.columns or 'value_ratio' not in df.columns:
        return None, None
    
    # 計算性價比百分位
    df_temp = df.copy()
    df_temp['value_percentile'] = df_temp['value_ratio'].rank(pct=True) * 100
    
    # 定義象限 - 使用布林遮罩來避免 dtype 問題
    mask_star = (df_temp['war_percentile'] >= 50) & (df_temp['value_percentile'] >= 50)
    mask_premium = (df_temp['war_percentile'] >= 50) & (df_temp['value_percentile'] < 50)
    mask_rookie = (df_temp['war_percentile'] < 50) & (df_temp['value_percentile'] >= 50)
    mask_deadweight = (df_temp['war_percentile'] < 50) & (df_temp['value_percentile'] < 50)
    
    # 使用 loc 和布林遮罩來賦值
    df_temp['TPM_category'] = '未分類'
    df_temp.loc[mask_star, 'TPM_category'] = '明星價值'
    df_temp.loc[mask_premium, 'TPM_category'] = '溢價球星'
    df_temp.loc[mask_rookie, 'TPM_category'] = '潛力新秀'
    df_temp.loc[mask_deadweight, 'TPM_category'] = '球隊冗員'
    
    # 創建散點圖
    fig = px.scatter(
        df_temp,
        x='war_percentile',
        y='value_percentile',
        color='TPM_category',
        hover_name='Name' if 'Name' in df_temp.columns else None,
        hover_data=['Team', 'Position', 'WAR', 'Salary_millions'],
        title='雙因子績效矩陣 (TPM)',
        labels={'war_percentile': 'WAR百分位 (%)', 'value_percentile': '性價比百分位 (%)'},
        color_discrete_map={
            '明星價值': '#2E7D32',  # 綠色
            '溢價球星': '#C62828',  # 紅色
            '潛力新秀': '#FF8F00',  # 橙色
            '球隊冗員': '#757575',   # 灰色
            '未分類': '#000000'      # 黑色
        }
    )
    
    # 添加象限分隔線
    fig.add_hline(y=50, line_dash="dash", line_color="black", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="black", opacity=0.5)
    
    fig.update_layout(
        xaxis_range=[0, 100],
        yaxis_range=[0, 100],
        height=600
    )
    
    return fig, df_temp

# ============================================================
# 側邊欄控制面板
# ============================================================
with st.sidebar:
    st.markdown("## 控制面板")
    
    # 分析選項
    st.markdown("### 選擇分析功能")
    analysis_mode = st.selectbox(
        "選擇要進行的分析",
        ["綜合儀表板", "全維度薪資模型", "球員搜尋", "球隊分析", "市場異常偵測", "進階策略分析", "原創財務指標", "公式與變數說明"],
        key="analysis_mode"
    )
    
    st.markdown("---")
    
    # 數據資訊
    st.markdown("### 專題資訊")
    st.markdown("**主題**: MLB薪資市場效率性分析")
    st.markdown("**方法**: 計量經濟學 + 財務分析")
    st.markdown("**目標**: 識別市場異常與投資機會")
    
    st.markdown("---")
    st.markdown(f"**更新時間:** {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# 主內容區域
# ============================================================

# 載入數據
df = load_data()

if df is None:
    st.warning("正在載入數據...")
    st.stop()

# 根據選擇的模組顯示不同內容
if analysis_mode == "綜合儀表板":
    st.markdown('<h2 class="section-title">綜合分析儀表板</h2>', unsafe_allow_html=True)
    
    # 使用說明
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 專題介紹
        **主題**: MLB薪資市場效率性分析  
        **方法**: 計量經濟學 + 財務分析  
        **目標**: 識別市場異常與投資機會
        
        ### 如何使用本儀表板
        1. **查看關鍵指標**：下方的卡片顯示整體數據概況
        2. **探索圖表**：互動式圖表可放大、縮小、懸停查看詳細信息
        3. **篩選數據**：使用圖表上方的篩選器查看特定範圍的數據
        4. **導出數據**：表格部分支持篩選和導出功能
        """)
    
    # 全局篩選條件
    st.markdown("### 數據篩選")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Team' in df.columns:
            all_teams = ["所有球隊"] + sorted(df['Team'].dropna().unique().tolist())
            selected_team = st.selectbox("選擇球隊", all_teams)
    
    with col2:
        if 'WAR' in df.columns:
            war_min, war_max = float(df['WAR'].min()), float(df['WAR'].max())
            war_range = st.slider("WAR範圍", war_min, war_max, (war_min, war_max))
    
    with col3:
        if 'Salary_millions' in df.columns:
            salary_min, salary_max = float(df['Salary_millions'].min()), float(df['Salary_millions'].max())
            salary_range = st.slider("薪資範圍 (百萬美元)", salary_min, salary_max, (salary_min, salary_max))
    
    # 應用篩選
    filtered_df = df.copy()
    
    if 'Team' in df.columns and selected_team != "所有球隊":
        filtered_df = filtered_df[filtered_df['Team'] == selected_team]
    
    if 'WAR' in df.columns:
        filtered_df = filtered_df[(filtered_df['WAR'] >= war_range[0]) & (filtered_df['WAR'] <= war_range[1])]
    
    if 'Salary_millions' in df.columns:
        filtered_df = filtered_df[(filtered_df['Salary_millions'] >= salary_range[0]) & 
                                 (filtered_df['Salary_millions'] <= salary_range[1])]
    
    # 關鍵指標卡片
    st.markdown("### 關鍵績效指標")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("球員總數", f"{len(filtered_df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if 'Salary_millions' in filtered_df.columns:
            avg_salary = filtered_df['Salary_millions'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("平均薪資", f"${avg_salary:.2f}M")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if 'WAR' in filtered_df.columns:
            avg_war = filtered_df['WAR'].mean()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("平均WAR", f"{avg_war:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if 'WAR' in filtered_df.columns and 'Salary_millions' in filtered_df.columns:
            correlation = filtered_df['WAR'].corr(filtered_df['Salary_millions'])
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("相關係數", f"{correlation:.3f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 圖表區域
    st.markdown("### 互動式圖表分析")
    
    tab1, tab2, tab3, tab4 = st.tabs(["薪資表現關係", "數據分布", "性價比分析", "市場效率指標"])
    
    with tab1:
        if 'WAR' in filtered_df.columns and 'Salary_millions' in filtered_df.columns:
            # 加入多項式次方選擇器
            st.markdown("#### ⚙️ 調整模型擬合度")
            poly_degree = st.slider(
                "選擇預期薪資模型次方數 (Degree)", 
                min_value=1, max_value=8, value=1, step=1,
                help="1為線性。3次方以上可捕捉巨星溢價，7~8次方可能產生過度擬合(Overfitting)。"
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 散點圖
                fig = px.scatter(
                    filtered_df, x='WAR', y='Salary_millions',
                    hover_name='Name' if 'Name' in filtered_df.columns else None,
                    hover_data=['Team', 'Position'] if all(col in filtered_df.columns for col in ['Team', 'Position']) else None,
                    title=f'薪資與表現關係圖 ({poly_degree}次方多項式擬合)',
                    labels={'WAR': '勝場貢獻值 (WAR)', 'Salary_millions': '薪資 (百萬美元)'}
                )
                
                # 添加高次迴歸線
                fig = add_regression_line(fig, filtered_df, 'WAR', 'Salary_millions', degree=poly_degree)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 統計分析
                x = filtered_df['WAR'].dropna().values
                y = filtered_df['Salary_millions'].dropna().values
                
                coeffs, p_obj, r_squared = calculate_polynomial_regression(x, y, degree=poly_degree)
                
                st.markdown("#### 迴歸分析結果")
                st.markdown("**模型方程式:**")
                eq_str = format_poly_equation(coeffs, 'WAR')
                st.markdown(rf"$$ \widehat{{\text{{Salary}}}} = {eq_str} $$")
                st.write(f"**決定係數 R²:** {r_squared:.3f}")
                st.write(f"**模型解釋力:** {r_squared*100:.1f}%")
                
                if poly_degree >= 5:
                    st.warning("⚠️ **過度擬合警告**：高次方多項式雖能完美穿過資料點，但會失去外插預測力。")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Salary_millions' in filtered_df.columns:
                fig1 = px.histogram(
                    filtered_df,
                    x='Salary_millions',
                    nbins=30,
                    title='薪資分布',
                    labels={'Salary_millions': '薪資 (百萬美元)'},
                    marginal="box"
                )
                st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
        
        with col2:
            if 'WAR' in filtered_df.columns:
                fig2 = px.histogram(
                    filtered_df,
                    x='WAR',
                    nbins=30,
                    title='WAR分布',
                    labels={'WAR': '勝場貢獻值'},
                    marginal="violin"
                )
                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
    
    with tab3:
        if 'value_ratio' in filtered_df.columns and 'Name' in filtered_df.columns:
            # 性價比排名
            st.markdown("#### 性價比最高球員")
            
            # 篩選出有正面WAR的球員
            positive_war = filtered_df[filtered_df['WAR'] > 0].copy()
            positive_war = positive_war[positive_war['value_ratio'].notna()]
            
            if len(positive_war) > 0:
                top_players = positive_war.nlargest(20, 'value_ratio')
                
                fig = px.bar(
                    top_players,
                    x='Name',
                    y='value_ratio',
                    color='value_ratio',
                    title='性價比最高球員 (前20名)',
                    labels={'value_ratio': '性價比 (WAR/百萬美元)', 'Name': '球員姓名'},
                    hover_data=['Team', 'WAR', 'Salary_millions']
                )
                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
            else:
                st.warning("沒有找到有正面WAR值的球員")
    
    with tab4:
        st.markdown("#### 市場效率指標分析")
        
        if all(col in filtered_df.columns for col in ['WVPI', 'RAV', 'MERI']):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_wvpi = filtered_df['WVPI'].mean()
                st.metric("平均 WVPI", f"{avg_wvpi:.2f}")
                st.caption("加權綜合價值指數")
            
            with col2:
                avg_rav = filtered_df['RAV'].mean()
                st.metric("平均 RAV", f"{avg_rav:.2f}")
                st.caption("風險調整後價值")
            
            with col3:
                avg_meri = filtered_df['MERI'].mean()
                st.metric("平均 MERI", f"{avg_meri:.4f}")
                st.caption("市場效率殘差指數")
            
            # 顯示原創指標的分布
            fig_wvpi = px.histogram(
                filtered_df,
                x='WVPI',
                nbins=30,
                title='WVPI 分布',
                color='WVPI_category' if 'WVPI_category' in filtered_df.columns else None
            )
            st.plotly_chart(fig_wvpi, use_container_width=True)  # 保留原始參數
    
    # 數據表格
    st.markdown("### 詳細數據表格")
    
    # 欄位選擇
    available_cols = filtered_df.columns.tolist()
    
    # 優先顯示的欄位 (加入原創指標)
    priority_cols = ['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'value_ratio', 'WVPI', 'RAV', 'MERI']
    priority_cols = [col for col in priority_cols if col in available_cols]
    
    # 搜尋功能
    search_col1, search_col2 = st.columns([2, 1])
    
    with search_col1:
        search_term = st.text_input("搜尋球員姓名", "", placeholder="輸入球員姓名關鍵字")
    
    with search_col2:
        sort_by = st.selectbox("排序依據", priority_cols)
    
    # 應用搜尋和排序
    display_df = filtered_df.copy()
    
    if search_term and 'Name' in filtered_df.columns:
        display_df = display_df[display_df['Name'].str.contains(search_term, case=False, na=False)]
    
    display_df = display_df.sort_values(sort_by, ascending=False)
    
    # 顯示數據
    st.dataframe(
        display_df[priority_cols].head(100),
        use_container_width=True,  # 保留原始參數
        height=400
    )
    
    # 下載按鈕
    csv = display_df[priority_cols].to_csv(index=False)
    st.download_button(
        label="下載篩選後數據",
        data=csv,
        file_name=f"mlb_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

elif analysis_mode == "全維度薪資模型":
    st.markdown('<h2 class="section-title">⚖️ 全維度薪資特徵定價模型 (Hedonic Pricing Model)</h2>', unsafe_allow_html=True)
    
    # --- 1. 學術規格說明與理論背景 ---
    st.markdown("""
    <div class="info-box">
    <b>🏛️ 計量經濟學理論背景：</b><br>
    本分析採用 <b>Hedonic Pricing (特徵定價法)</b> 與 <b>Log-Level (對數-線性)</b> 規格。
    透過將依變數（薪資）取對數，我們可以將 $\\beta$ 係數解釋為「半彈性 (Semi-elasticity)」，即特徵每增加一單位，薪資預期變動之百分比。<br>
    本模型特別區分了<b>投手 (Pitcher)</b> 與 <b>打者 (Hitter)</b> 市場，以排除不同守備特性造成的結構性偏差 (Structural Break)。
    </div>
    """, unsafe_allow_html=True)

    # --- 2. 數據分群與嚴謹的特徵工程 ---
    m_df = df.copy()
    
    # 側邊欄控制：模型切換與參數調整
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔬 專業模型設定")
    m_scope = st.sidebar.radio("模型分析範圍", ["打者模型 (Hitter Model)", "投手模型 (Pitcher Model)"])
    
    # 變數定義：根據模型類型切換 X 變數
    if m_scope == "打者模型 (Hitter Model)":
        # 變數包含：產值(WAR)、生理(Age)、制度(Years)、攻擊(wRC+)、防守(Def)
        X_vars = ['WAR', 'Age', 'Years', 'wRC+', 'Def']
        m_df = m_df[~m_df['Position'].str.contains('P', na=False)]
        latex_formula = r"\ln(\text{Salary}) = \beta_0 + \beta_1 \text{WAR} + \beta_2 \text{Age} + \beta_3 \text{Age}^2 + \beta_4 \text{Years} + \beta_5 \text{wRC+} + \beta_6 \text{Def} + \epsilon"
        m_label = "Hitter"
    else:
        # 投手模型：排除打擊與防守指標
        X_vars = ['WAR', 'Age', 'Years'] 
        m_df = m_df[m_df['Position'].str.contains('P', na=False)]
        latex_formula = r"\ln(\text{Salary}) = \beta_0 + \beta_1 \text{WAR} + \beta_2 \text{Age} + \beta_3 \text{Age}^2 + \beta_4 \text{Years} + \epsilon"
        m_label = "Pitcher"

    # 數據強制清洗 (確保數值化)
    for c in X_vars + ['Salary_millions']:
        m_df[c] = pd.to_numeric(m_df[c], errors='coerce')
    m_df = m_df.dropna(subset=X_vars + ['Salary_millions'])

    # 特徵轉換：Log 與 Age-Squared (巔峰效應)
    m_df['Log_Salary'] = np.log1p(m_df['Salary_millions'].astype(float))
    m_df['Age_Squared'] = m_df['Age'].astype(float) ** 2

    # --- 3. 執行多元迴歸 (OLS) ---
    X_matrix = m_df[X_vars + ['Age_Squared']].astype(float)
    X_matrix = sm.add_constant(X_matrix) # 截距項
    y_vector = m_df['Log_Salary'].astype(float)

    try:
        results = sm.OLS(y_vector, X_matrix).fit()

        # --- 4. 呈現模型估計方程式 ---
        st.write(f"#### 🎓 {m_scope}：估計方程式")
        st.latex(latex_formula)

        # --- 5. 深度分析分頁系統 ---
        t_coef, t_diag, t_resid, t_sim = st.tabs([
            "📋 統計係數與半彈性", "🔍 模型診斷與共線性", "🕵️ 全維度殘差異常", "🧪 薪資邊際模擬器"
        ])

        with t_coef:
            st.subheader("迴歸係數與經濟影響力分析")
            
            # 建立係數表
            summary_df = pd.DataFrame({
                "Beta 係數": results.params,
                "標準誤": results.bse,
                "t 統計量": results.tvalues,
                "P-Value": results.pvalues,
                "邊際貢獻率 (%)": (np.exp(results.params) - 1) * 100
            })
            
            # 顯著性邏輯判斷
            def get_sig_stars(p):
                if p < 0.01: return "★★★ (p<0.01)"
                if p < 0.05: return "★★ (p<0.05)"
                if p < 0.1: return "★ (p<0.1)"
                return "n.s. (不具統計顯著性)"
            summary_results = summary_df.copy()
            summary_results['顯著性標記'] = summary_results['P-Value'].apply(get_sig_stars)
            
            st.markdown("**註：邊際貢獻率為該特徵增加一單位時，預期薪資變動之百分比。**")
            st.dataframe(summary_results.style.format({
                "Beta 係數": "{:.4f}",
                "標準誤": "{:.4f}",
                "t 統計量": "{:.2f}",
                "P-Value": "{:.4f}",
                "邊際貢獻率 (%)": "{:.1f}%"
            }), use_container_width=True)

            col_met1, col_met2, col_met3 = st.columns(3)
            col_met1.metric("解釋力 R-squared", f"{results.rsquared:.4f}")
            col_met2.metric("調整後 R²", f"{results.rsquared_adj:.3f}")
            col_met3.metric("樣本規模 (N)", len(m_df))

        with t_diag:
            st.subheader("模型診斷與穩健性檢查")
            col_v1, col_v2 = st.columns(2)
            
            with col_v1:
                # 執行 VIF 共線性檢定 (確保變數無重疊)
                st.write("**變數膨脹因子 (VIF) 檢定**")
                from statsmodels.stats.outliers_influence import variance_inflation_factor
                vif_data = pd.DataFrame()
                vif_data["變數"] = X_matrix.columns
                vif_data["VIF 指數"] = [variance_inflation_factor(X_matrix.values, i) for i in range(len(X_matrix.columns))]
                st.dataframe(vif_data.round(2), hide_index=True)
                st.caption("註：Age 與 Age² 之間具備結構性共線性，VIF > 10 為預期內正常現象。")

            with col_v2:
                # 殘差常態性診斷
                fig_hist = px.histogram(results.resid, nbins=30, title="殘差分佈圖 (Residual Normality)",
                                         labels={'value': '殘差值'}, color_discrete_sequence=['#1e3a8a'])
                st.plotly_chart(fig_hist, use_container_width=True)
                

        with t_resid:
            st.subheader("全維度市場異常偵測 (2.0)")
            st.markdown("當我們考慮了年齡、年資與守備位置後，仍無法被模型解釋的殘差部分即為「定價偏差」。")
            
            # 預測值還原 (Antilog)
            m_df['Predicted_Salary'] = np.expm1(results.fittedvalues.astype(float))
            m_df['Ultimate_Residual'] = m_df['Salary_millions'] - m_df['Predicted_Salary']
            
            fig_res = px.scatter(m_df, x='Predicted_Salary', y='Salary_millions', 
                                 hover_name='Name', color='Ultimate_Residual',
                                 color_continuous_scale='RdBu_r',
                                 labels={'Predicted_Salary': '模型預估身價 (M$)', 'Salary_millions': '實際薪資 (M$)'},
                                 title=f"{m_scope}：預期 vs 實際薪資分佈")
            
            # 繪製 45 度理想對角線
            diag_max = max(m_df['Salary_millions'].max(), m_df['Predicted_Salary'].max())
            fig_res.add_trace(go.Scatter(x=[0, diag_max], y=[0, diag_max], mode='lines', 
                                         line=dict(color='black', dash='dot'), name='效率邊界'))
            st.plotly_chart(fig_res, use_container_width=True)

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.success("💎 **真正被低估球員 (低於預期身價)**")
                st.dataframe(m_df.nsmallest(15, 'Ultimate_Residual')[['Name', 'WAR', 'Salary_millions', 'Predicted_Salary']].round(2), hide_index=True)
            with col_res2:
                st.error("⚠️ **真正溢價合約 (高於預期身價)**")
                st.dataframe(m_df.nlargest(15, 'Ultimate_Residual')[['Name', 'WAR', 'Salary_millions', 'Predicted_Salary']].round(2), hide_index=True)

        with t_sim:
            st.subheader("🧪 邊際經濟價值模擬器")
            st.write("設定球員特徵參數，推算在當前市場結構下的「合理年度定價」：")
            
            sc1, sc2 = st.columns(2)
            with sc1:
                s_war = st.slider("球員戰力 (WAR)", -2.0, 10.0, 4.0)
                s_age = st.slider("球員年齡", 20, 45, 27)
            with sc2:
                s_years = st.slider("剩餘合約/年資 (Years)", 1, 13, 6)
                if m_label == "Hitter":
                    s_wrc = st.slider("進攻貢獻 (wRC+)", 50, 200, 110)
                else:
                    s_wrc = 0

            # 計算預測薪資 (Log 空間相加再還原)
            sim_log_p = (results.params['const'] + 
                         results.params['WAR'] * s_war + 
                         results.params['Age'] * s_age + 
                         results.params['Age_Squared'] * (s_age**2) + 
                         results.params['Years'] * s_years)
            if 'wRC+' in results.params: sim_log_p += results.params['wRC+'] * s_wrc
            
            sim_final = np.expm1(sim_log_p)
            
            st.markdown(f"""
            <div style="text-align: center; background-color: #f1f5f9; padding: 30px; border-radius: 20px; border: 3px solid #1E3A8A;">
                <p style="color: #64748b; font-size: 1.2rem; margin-bottom: 0;">此特徵組合下之「理想年度薪資」預測</p>
                <h1 style="font-size: 4rem; color: #1e40af; margin: 10px 0;">${sim_final:.2f} M</h1>
                <p style="color: #94a3b8;">(已根據市場生理曲線、年資紅利與戰力指標進行動態校正)</p>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"模型運算錯誤。這通常是因為特定子群組資料量不足或共線性過強導致矩陣奇異。")
        st.info(f"詳細錯誤訊息: {e}")
        
elif analysis_mode == "球員搜尋":
    st.markdown('<h2 class="section-title">球員搜尋與比較</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **球員搜尋**：輸入球員姓名（支援部分關鍵字）
        2. **球員比較**：選擇多位球員進行詳細比較
        3. **詳細資訊**：點擊球員姓名展開查看完整數據
        
        ### 使用技巧
        - 搜尋時可以使用姓氏或名字的任何部分
        - 最多可同時比較5位球員
        - 所有數據皆可排序和篩選
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 球員搜尋")
        
        # 快速搜尋
        search_term = st.text_input("輸入球員姓名", "", 
                                   placeholder="例如：Ohtani, Trout, Judge...",
                                   key="player_search")
        
        if search_term and 'Name' in df.columns:
            search_results = df[df['Name'].str.contains(search_term, case=False, na=False)]
            
            if len(search_results) > 0:
                st.success(f"找到 {len(search_results)} 位球員")
                
                # 顯示搜尋結果
                for idx, player in search_results.iterrows():
                    with st.expander(f"👤 {player['Name']}", expanded=False):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if 'Team' in df.columns:
                                st.write(f"**球隊:** {player.get('Team', 'N/A')}")
                            if 'Position' in df.columns:
                                st.write(f"**位置:** {player.get('Position', 'N/A')}")
                            if 'WAR' in df.columns:
                                st.write(f"**WAR:** {player.get('WAR', 'N/A'):.2f}")
                            if 'WVPI' in df.columns:
                                st.write(f"**WVPI:** {player.get('WVPI', 'N/A'):.2f}")
                        
                        with col_b:
                            if 'Salary_millions' in df.columns:
                                st.write(f"**薪資:** ${player.get('Salary_millions', 'N/A'):.2f}M")
                            if 'HR' in df.columns:
                                st.write(f"**全壘打:** {player.get('HR', 'N/A')}")
                            if 'RBI' in df.columns:
                                st.write(f"**打點:** {player.get('RBI', 'N/A')}")
                            if 'RAV' in df.columns:
                                st.write(f"**RAV:** {player.get('RAV', 'N/A'):.2f}")
                        
                        if 'value_ratio' in df.columns and pd.notna(player.get('value_ratio')):
                            st.write(f"**性價比:** {player.get('value_ratio', 'N/A'):.3f} WAR/百萬美元")
            else:
                st.warning("找不到符合條件的球員")
                st.info("試試看：使用姓氏或名字的任何部分進行搜尋")
    
    with col2:
        st.markdown("#### 球員比較")
        
        # 球員選擇
        if 'Name' in df.columns:
            # 顯示球員選擇器
            player_options = df['Name'].sort_values().tolist()
            
            selected_players = st.multiselect(
                "選擇要比較的球員",
                player_options,
                max_selections=5,
                help="可選擇最多5位球員進行詳細比較"
            )
            
            if len(selected_players) >= 1:
                compare_df = df[df['Name'].isin(selected_players)]
                
                # 選擇要顯示的欄位 (加入原創指標)
                compare_cols = ['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'value_ratio', 'WVPI', 'RAV', 'MERI']
                
                # 檢查欄位是否存在
                available_cols = [col for col in compare_cols if col in compare_df.columns]
                
                if len(available_cols) >= 4:  # 至少要有姓名和主要數據
                    st.dataframe(
                        compare_df[available_cols].sort_values('WAR', ascending=False),
                        use_container_width=True,  # 保留原始參數
                        hide_index=True
                    )
                    
                    # 簡單比較圖表
                    if len(selected_players) >= 2:
                        st.markdown("#### 比較圖表")
                        
                        # 新增：雷達圖比較
                        st.markdown("**能力值比較 (PR值雷達圖)**")
                        fig_radar = plot_player_radar(df, selected_players)
                        if fig_radar:
                            st.plotly_chart(fig_radar, use_container_width=True)  # 保留原始參數

                        # 原有的柱狀圖
                        st.markdown("**數值直接比較**")
                        fig = go.Figure()
                        
                        fig.add_trace(go.Bar(
                            x=compare_df['Name'],
                            y=compare_df['WAR'],
                            name='WAR',
                            marker_color='blue'
                        ))
                        
                        fig.add_trace(go.Bar(
                            x=compare_df['Name'],
                            y=compare_df['Salary_millions'],
                            name='薪資 (M)',
                            marker_color='green',
                            yaxis='y2'
                        ))
                        
                        fig.update_layout(
                            title='球員WAR與薪資比較',
                            yaxis=dict(title='WAR'),
                            yaxis2=dict(title='薪資 (百萬美元)', overlaying='y', side='right'),
                            barmode='group'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)  # 保留原始參數

elif analysis_mode == "球隊分析":
    st.markdown('<h2 class="section-title">球隊分析</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **球隊選擇**：選擇要分析的球隊（可多選）
        2. **效率排名**：比較不同球隊的薪資使用效率
        3. **詳細統計**：查看每支球隊的詳細數據
        4. **投資組合夏普指數 (PSI)**：衡量球隊風險調整後的績效表現
        
        ### 關鍵指標
        - **總WAR**：球隊所有球員的WAR總和
        - **總薪資**：球隊薪資支出總額
        - **效率**：每百萬美元薪資能獲得的WAR
        - **PSI**：投資組合夏普指數，衡量風險調整後的超額績效
        """)
    
    if 'Team' in df.columns:
        # 球隊選擇
        all_teams = sorted(df['Team'].dropna().unique().tolist())
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_teams = st.multiselect(
                "選擇球隊（可多選）",
                all_teams,
                default=all_teams[1:5] if len(all_teams) > 4 else all_teams,
                help="選擇要分析的球隊，預設顯示前4支球隊"
            )
        
        with col2:
            # 分析類型選擇
            analysis_type = st.selectbox(
                "分析類型",
                ["效率排名", "詳細統計", "薪資分布", "薪資不平等分析", "投資組合夏普指數 (PSI)"],
                help="選擇要進行的分析類型"
            )
        
        if selected_teams:
            team_df = df[df['Team'].isin(selected_teams)]
            
            if analysis_type == "效率排名":
                # 計算球隊統計
                team_stats = team_df.groupby('Team').agg({
                    'Name': 'count',
                    'WAR': 'sum',
                    'Salary_millions': 'sum',
                }).round(2).reset_index()
                
                team_stats['efficiency'] = (team_stats['WAR'] / team_stats['Salary_millions']).round(3)
                team_stats = team_stats.rename(columns={
                    'Name': '球員數',
                    'WAR': '總WAR',
                    'Salary_millions': '總薪資(M)'
                })
                
                # 排序選項
                sort_by = st.selectbox("排序方式", ["總WAR", "效率", "總薪資(M)", "球員數"])
                
                if sort_by == "效率":
                    team_stats = team_stats.sort_values('efficiency', ascending=False)
                elif sort_by == "總薪資(M)":
                    team_stats = team_stats.sort_values('總薪資(M)', ascending=False)
                elif sort_by == "球員數":
                    team_stats = team_stats.sort_values('球員數', ascending=False)
                else:  # 總WAR
                    team_stats = team_stats.sort_values('總WAR', ascending=False)
                
                # 顯示排名
                st.dataframe(team_stats, use_container_width=True, hide_index=True)  # 保留原始參數
                
                # 可視化
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.bar(
                        team_stats,
                        x='Team',
                        y='總WAR',
                        title='球隊總WAR排名',
                        color='總WAR',
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
                
                with col2:
                    fig2 = px.bar(
                        team_stats,
                        x='Team',
                        y='efficiency',
                        title='球隊效率排名',
                        color='efficiency',
                        color_continuous_scale='plasma'
                    )
                    st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
            
            elif analysis_type == "詳細統計":
                st.markdown("#### 球隊詳細統計")
                
                if 'Team' in team_df.columns:
                    # 為每支球隊創建詳細統計
                    for team in selected_teams:
                        team_players = team_df[team_df['Team'] == team]
                        
                        if len(team_players) > 0:
                            with st.expander(f"{team} - {len(team_players)}位球員", expanded=False):
                                # 球隊摘要指標
                                col_a, col_b, col_c, col_d = st.columns(4)
                                
                                with col_a:
                                    total_war = team_players['WAR'].sum() if 'WAR' in team_players.columns else 0
                                    st.metric("總WAR", f"{total_war:.2f}")
                                
                                with col_b:
                                    total_salary = team_players['Salary_millions'].sum() if 'Salary_millions' in team_players.columns else 0
                                    st.metric("總薪資", f"${total_salary:.2f}M")
                                
                                with col_c:
                                    avg_salary = team_players['Salary_millions'].mean() if 'Salary_millions' in team_players.columns else 0
                                    st.metric("平均薪資", f"${avg_salary:.2f}M")
                                
                                with col_d:
                                    if total_salary > 0 and 'WAR' in team_players.columns:
                                        efficiency = total_war / total_salary
                                        st.metric("效率", f"{efficiency:.3f}")
                                    else:
                                        st.metric("效率", "N/A")
                                
                                # 分頁顯示
                                stat_tab1, stat_tab2, stat_tab3 = st.tabs(["球員列表", "表現分析", "薪資結構"])
                                
                                with stat_tab1:
                                    # 顯示球員列表
                                    display_cols = []
                                    if 'Name' in team_players.columns:
                                        display_cols.append('Name')
                                    if 'Position' in team_players.columns:
                                        display_cols.append('Position')
                                    if 'WAR' in team_players.columns:
                                        display_cols.append('WAR')
                                    if 'Salary_millions' in team_players.columns:
                                        display_cols.append('Salary_millions')
                                    if 'value_ratio' in team_players.columns:
                                        display_cols.append('value_ratio')
                                    if 'WVPI' in team_players.columns:
                                        display_cols.append('WVPI')
                                    
                                    if display_cols:
                                        # 排序選項
                                        sort_option = st.selectbox(
                                            f"排序方式 ({team})",
                                            [col for col in ['WAR', 'Salary_millions', 'value_ratio', 'WVPI'] if col in display_cols],
                                            key=f"sort_{team}"
                                        )
                                        
                                        if sort_option in team_players.columns:
                                            sorted_players = team_players.sort_values(sort_option, ascending=False)
                                            st.dataframe(
                                                sorted_players[display_cols],
                                                use_container_width=True,  # 保留原始參數
                                                hide_index=True
                                            )
                                        else:
                                            st.dataframe(
                                                team_players[display_cols],
                                                use_container_width=True,  # 保留原始參數
                                                hide_index=True
                                            )
                                
                                with stat_tab2:
                                    # 表現分析
                                    if 'WAR' in team_players.columns:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # WAR分布
                                            fig1 = px.histogram(
                                                team_players,
                                                x='WAR',
                                                nbins=20,
                                                title=f'{team} - WAR分布',
                                                labels={'WAR': '勝場貢獻值'}
                                            )
                                            st.plotly_chart(fig1, use_container_width=True)  # 保留原始參數
                                        
                                        with col2:
                                            # WAR百分位
                                            if 'war_percentile' in team_players.columns:
                                                fig2 = px.box(
                                                    team_players,
                                                    y='war_percentile',
                                                    title=f'{team} - WAR百分位分布',
                                                    labels={'war_percentile': 'WAR百分位 (%)'}
                                                )
                                                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
                                
                                with stat_tab3:
                                    # 薪資結構分析
                                    if 'Salary_millions' in team_players.columns:
                                        col1, col2 = st.columns(2)
                                        
                                        with col1:
                                            # 薪資分布
                                            fig3 = px.pie(
                                                team_players,
                                                values='Salary_millions',
                                                names='Position' if 'Position' in team_players.columns else None,
                                                title=f'{team} - 薪資按位置分布',
                                                hole=0.3
                                            )
                                            st.plotly_chart(fig3, use_container_width=True)  # 保留原始參數
                                        
                                        with col2:
                                            # 薪資級別分析
                                            if 'salary_category' in team_players.columns:
                                                salary_cat_counts = team_players['salary_category'].value_counts()
                                                fig4 = px.bar(
                                                    x=salary_cat_counts.index,
                                                    y=salary_cat_counts.values,
                                                    title=f'{team} - 薪資級別分布',
                                                    labels={'x': '薪資級別', 'y': '球員數'}
                                                )
                                                st.plotly_chart(fig4, use_container_width=True)  # 保留原始參數
                        
                        else:
                            st.info(f"球隊 {team} 沒有可用的球員數據")

            elif analysis_type == "薪資分布":
                st.markdown("#### 球隊薪資分布分析")
                
                if 'Salary_millions' in team_df.columns and 'Team' in team_df.columns:
                    # 使用標籤頁組織不同視圖
                    dist_tab1, dist_tab2, dist_tab3 = st.tabs(["視覺化分布", "統計摘要", "球隊比較"])
                    
                    with dist_tab1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 箱形圖顯示分布
                            fig_box = px.box(
                                team_df,
                                x='Team',
                                y='Salary_millions',
                                title='各球隊薪資分布',
                                labels={'Salary_millions': '薪資（百萬美元）'},
                                color='Team'
                            )
                            fig_box.update_layout(showlegend=False)
                            st.plotly_chart(fig_box, use_container_width=True)  # 保留原始參數
                        
                        with col2:
                            # 小提琴圖顯示概率密度
                            fig_violin = px.violin(
                                team_df,
                                x='Team',
                                y='Salary_millions',
                                box=True,
                                points="outliers",
                                title='薪資密度分布',
                                labels={'Salary_millions': '薪資（百萬美元）'}
                            )
                            st.plotly_chart(fig_violin, use_container_width=True)  # 保留原始參數
                    
                    with dist_tab2:
                        # 詳細統計表格
                        stats_cols = ['Team', 'Salary_millions']
                        if 'WAR' in team_df.columns:
                            stats_cols.append('WAR')
                        if 'value_ratio' in team_df.columns:
                            stats_cols.append('value_ratio')
                        
                        stats_df = team_df[stats_cols].groupby('Team').agg({
                            'Salary_millions': ['count', 'mean', 'median', 'std', 'min', 'max', 'sum'],
                            **({'WAR': 'sum'} if 'WAR' in stats_cols else {}),
                            **({'value_ratio': 'mean'} if 'value_ratio' in stats_cols else {})
                        }).round(2)
                        
                        # 扁平化多層索引
                        stats_df.columns = ['_'.join(col).strip() for col in stats_df.columns.values]
                        stats_df = stats_df.reset_index()
                        
                        # 重新命名欄位
                        column_rename = {
                            'Salary_millions_count': '球員數',
                            'Salary_millions_mean': '平均薪資',
                            'Salary_millions_median': '薪資中位數',
                            'Salary_millions_std': '薪資標準差',
                            'Salary_millions_min': '最低薪資',
                            'Salary_millions_max': '最高薪資',
                            'Salary_millions_sum': '薪資總額'
                        }
                        
                        if 'WAR_sum' in stats_df.columns:
                            column_rename['WAR_sum'] = '總WAR'
                        if 'value_ratio_mean' in stats_df.columns:
                            column_rename['value_ratio_mean'] = '平均性價比'
                        
                        stats_df = stats_df.rename(columns=column_rename)
                        
                        st.dataframe(stats_df, use_container_width=True, hide_index=True)  # 保留原始參數
                    
                    with dist_tab3:
                        # 球隊間比較
                        st.markdown("##### 球隊間薪資結構比較")
                        
                        comparison_cols = st.multiselect(
                            "選擇比較指標",
                            ['平均薪資', '薪資中位數', '薪資總額', '球員數', '總WAR', '平均性價比'],
                            default=['平均薪資', '總WAR']
                        )
                        
                        if comparison_cols and stats_df is not None:
                            # 確保選擇的欄位存在
                            available_cols = [col for col in comparison_cols if col in stats_df.columns]
                            
                            if available_cols:
                                comparison_df = stats_df[['Team'] + available_cols]
                                
                                # 創建比較圖表
                                fig = go.Figure()
                                
                                for col in available_cols:
                                    fig.add_trace(go.Bar(
                                        name=col,
                                        x=comparison_df['Team'],
                                        y=comparison_df[col],
                                        text=comparison_df[col].round(2),
                                        textposition='auto'
                                    ))
                                
                                fig.update_layout(
                                    title='球隊間指標比較',
                                    barmode='group',
                                    xaxis_title="球隊",
                                    yaxis_title="數值"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                            else:
                                st.info("請選擇有效的比較指標")
                
                else:
                    st.warning("⚠️ 無法進行薪資分布分析：缺少必要的薪資或球隊數據")
            
            # 新增：薪資不平等分析區塊
            elif analysis_type == "薪資不平等分析":
                st.markdown("#### 球隊薪資結構與不平等 (Gini Coefficient)")
                
                for team in selected_teams:
                    team_data = team_df[team_df['Team'] == team]
                    
                    with st.expander(f"{team} - 薪資不平等分析", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 羅倫茲曲線與 Gini
                            fig_lorenz, gini = plot_lorenz_curve(team_data, team)
                            st.plotly_chart(fig_lorenz, use_container_width=True)  # 保留原始參數
                            
                            # Gini 解讀
                            if gini > 0.5:
                                st.warning(f"⚠️ 薪資分配極度不均 (Gini: {gini:.3f}) - 球隊資源高度集中於少數球星")
                            else:
                                st.success(f"✅ 薪資分配相對平均 (Gini: {gini:.3f}) - 團隊薪資結構較為均衡")

                        with col2:
                            # 薪資級別分布
                            if 'salary_category' in team_data.columns:
                                cat_counts = team_data['salary_category'].value_counts()
                                fig2 = px.pie(
                                    values=cat_counts.values,
                                    names=cat_counts.index,
                                    title=f'{team} 薪資級別分布',
                                    hole=0.4
                                )
                                st.plotly_chart(fig2, use_container_width=True)  # 保留原始參數
            
            elif analysis_type == "投資組合夏普指數 (PSI)":
                st.markdown("#### 投資組合夏普指數 (Portfolio Sharpe Index)")
                st.markdown("""
                **PSI** 衡量球隊風險調整後的績效表現，類似夏普比率。
                
                $$ \\text{PSI} = \\frac{\\text{總WAR} - \\text{總薪資} \\times \\bar{e}_{\\text{league}}}{\\sigma_{\\text{WAR}}^{\\text{team}}} $$
                
                其中：
                - $\\bar{e}_{\\text{league}}$：聯盟平均效率（每百萬美元可獲得的WAR）
                - $\\sigma_{\\text{WAR}}^{\\text{team}}$：球隊內部球員WAR的標準差（衡量風險）
                """)
                
                # 計算聯盟平均效率
                league_efficiency = df['WAR'].sum() / df['Salary_millions'].sum()
                
                # 計算每支球隊的PSI
                team_psi_list = []
                for team in selected_teams:
                    team_data = team_df[team_df['Team'] == team]
                    
                    if len(team_data) >= 3:  # 至少需要3個球員
                        total_war = team_data['WAR'].sum()
                        total_salary = team_data['Salary_millions'].sum()
                        expected_war = total_salary * league_efficiency
                        excess_war = total_war - expected_war
                        team_risk = team_data['WAR'].std()
                        
                        psi = excess_war / team_risk if team_risk > 0 else 0
                        
                        team_psi_list.append({
                            'Team': team,
                            '總WAR': total_war,
                            '總薪資(M)': total_salary,
                            '預期WAR': expected_war,
                            '超額WAR': excess_war,
                            '球隊風險': team_risk,
                            'PSI': psi
                        })
                
                if team_psi_list:
                    psi_df = pd.DataFrame(team_psi_list)
                    
                    # 顯示PSI排名
                    psi_df_sorted = psi_df.sort_values('PSI', ascending=False)
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.dataframe(
                            psi_df_sorted[['Team', 'PSI', '超額WAR', '球隊風險']].round(3),
                            use_container_width=True,  # 保留原始參數
                            hide_index=True
                        )
                    
                    with col2:
                        # PSI分類 (依據 new_variables.md 5.6 節)
                        conditions = [
                            psi_df_sorted['PSI'] > 1.5,
                            (psi_df_sorted['PSI'] > 0.5) & (psi_df_sorted['PSI'] <= 1.5),
                            (psi_df_sorted['PSI'] > -0.5) & (psi_df_sorted['PSI'] <= 0.5),
                            (psi_df_sorted['PSI'] > -1.5) & (psi_df_sorted['PSI'] <= -0.5),
                            psi_df_sorted['PSI'] <= -1.5
                        ]
                        categories = ['卓越管理', '良好管理', '平庸管理', '效率不佳', '糟糕管理']
                        psi_df_sorted['管理評價'] = np.select(conditions, categories, default='未知')
                        
                        st.dataframe(
                            psi_df_sorted[['Team', 'PSI', '管理評價']], 
                            use_container_width=True,  # 保留原始參數
                            hide_index=True
                        )
                    
                    # 可視化
                    fig = px.bar(
                        psi_df_sorted,
                        x='Team',
                        y='PSI',
                        color='PSI',
                        color_continuous_scale='RdYlGn',
                        title='球隊投資組合夏普指數 (PSI) 排名',
                        labels={'PSI': '投資組合夏普指數'}
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig.add_hline(y=0.5, line_dash="dash", line_color="green", opacity=0.3)
                    fig.add_hline(y=-0.5, line_dash="dash", line_color="red", opacity=0.3)
                    
                    st.plotly_chart(fig, use_container_width=True)  # 保留原始參數
                    
                    # PSI 解讀
                    st.markdown("**PSI 解讀**")
                    st.markdown("""
                    - **PSI > 1.5**：卓越管理（光芒、道奇等級）
                    - **0.5 < PSI ≤ 1.5**：良好管理
                    - **-0.5 < PSI ≤ 0.5**：平庸管理
                    - **-1.5 < PSI ≤ -0.5**：效率不佳
                    - **PSI ≤ -1.5**：糟糕管理（需要重組）
                    """)
                else:
                    st.warning("所選球隊數據不足，無法計算PSI")

elif analysis_mode == "市場異常偵測":
    st.markdown('<h2 class="section-title">🕵️ 市場異常偵測：一維產值 vs. 全維度定價對照</h2>', unsafe_allow_html=True)
    
    with st.expander("使用說明", expanded=True):
        st.markdown("""
        ### 功能介紹
        1. **異常偵測**：識別實際薪資偏離模型預期身價的球員。
        2. **模型切換**：可選擇 **[單一戰力曲線]** 或 **[全維度計量模型]**。
        3. **MERI 指標**：透過戰力加權殘差，判斷定價偏離的嚴重性。
        """)

    # --- 1. 偵測與模型設定 (保留所有原始 Slider) ---
    if 'WAR' in df.columns and 'Salary_millions' in df.columns:
        min_salary_threshold = 1.0  
        st.markdown("### ⚙️ 偵測與模型設定")
        
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            poly_degree = st.slider("1. WAR 曲線擬合次方數 (對照組)", 1, 8, 3)
        with col_m2:
            threshold = st.slider("異常值判定閾值 (%)", 10, 100, 30, step=5)

        col1, col2 = st.columns(2)
        with col1:
            min_val = float(df['WAR'].min())
            max_val = float(df['WAR'].max())
            min_war = st.slider("最小WAR要求", min_val, max_val, 1.0)
        with col2:
            exclude_rookies = st.checkbox("排除底薪球員 (< $1M)", value=True)

        analysis_focus = st.radio("選擇身價判定邏輯", ["單一 WAR 曲線", "全維度計量模型"], horizontal=True)

        # --- 2. 核心計算區：兩套模型並行 ---
        # 模型 A：原本的多項式回歸 (你的邏輯)
        df_model_simple = df[df['Salary_millions'] > min_salary_threshold].dropna(subset=['WAR', 'Salary_millions']).copy()
        coeffs_s = np.polyfit(df_model_simple['WAR'].values, df_model_simple['Salary_millions'].values, poly_degree)
        p_simple = np.poly1d(coeffs_s)
        
        # 模型 B：全維度多元回歸 (計量引擎)
        m_scope = "Hitter" if (~df['Position'].str.contains('P', na=False)).sum() > df['Position'].str.contains('P', na=False).sum() else "Pitcher"
        X_vars = ['WAR', 'Age', 'Years', 'wRC+', 'Def'] if m_scope == "Hitter" else ['WAR', 'Age', 'Years']
            
        df_model_multi = df.dropna(subset=X_vars + ['Salary_millions']).copy()
        df_model_multi['Log_Salary'] = np.log1p(df_model_multi['Salary_millions'].astype(float))
        df_model_multi['Age_Squared'] = df_model_multi['Age']**2
        X_m = sm.add_constant(df_model_multi[X_vars + ['Age_Squared']].astype(float))
        res_multi = sm.OLS(df_model_multi['Log_Salary'], X_m).fit()

        # --- 3. 應用基準與計算 ---
        df_clean = df.dropna(subset=['WAR', 'Salary_millions', 'Age', 'Years']).copy()
        df_clean['Age_Squared'] = df_clean['Age']**2

        if "單一 WAR" in analysis_focus:
            df_clean['expected_salary'] = np.maximum(p_simple(df_clean['WAR']), 0.7)
        else:
            X_pred = sm.add_constant(df_clean[X_vars + ['Age_Squared']].astype(float))
            df_clean['expected_salary'] = np.expm1(res_multi.predict(X_pred))

        df_clean['salary_residual'] = df_clean['Salary_millions'] - df_clean['expected_salary']
        df_clean['residual_percent'] = (df_clean['salary_residual'] / df_clean['expected_salary']) * 100
        df_clean['MERI'] = (df_clean['salary_residual'] / df_clean['expected_salary']) * np.log(1 + np.abs(df_clean['WAR']))

        # --- 4. 顯示模型詳細資訊 (Beta 公式化) ---
        with st.expander("📝 當前模型估計方程式與變數解釋", expanded=True):
            if "單一 WAR" in analysis_focus:
                eq_str = format_poly_equation(coeffs_s, 'WAR')
                st.write("**單一維度產值定價公式：**")
                st.latex(rf"\widehat{{\text{{Salary}}}} = {eq_str}")
            else:
                # 提取 Beta 並動態生成 LaTeX 公式
                b = res_multi.params
                if m_scope == "Hitter":
                    formula = (rf"\ln(\text{{Salary}}) = {b['const']:.3f} + {b['WAR']:.3f}(\text{{WAR}}) + {b['Age']:.3f}(\text{{Age}}) "
                               rf"+ {b['Age_Squared']:.4f}(\text{{Age}}^2) + {b['Years']:.3f}(\text{{Years}}) "
                               rf"+ {b['wRC+']:.4f}(\text{{wRC+}}) + {b['Def']:.3f}(\text{{Def}})")
                else:
                    formula = (rf"\ln(\text{{Salary}}) = {b['const']:.3f} + {b['WAR']:.3f}(\text{{WAR}}) + {b['Age']:.3f}(\text{{Age}}) "
                               rf"+ {b['Age_Squared']:.4f}(\text{{Age}}^2) + {b['Years']:.3f}(\text{{Years}})")
                
                st.write("**全維度計量定價公式 (Log-Level)：**")
                st.latex(formula)
                
                st.markdown("---")
                st.markdown("**變數中文翻譯與經濟意義：**")
                cols = st.columns(2)
                with cols[0]:
                    st.write("- **WAR (勝場貢獻值)**: 球員相較於替補球員為球隊多贏得的勝場。")
                    st.write("- **Age (年齡)**: 球員的生理年齡。")
                    st.write("- **Age² (年齡平方)**: 用於捕捉生理巔峰後的報酬遞減（折舊）效應。")
                with cols[1]:
                    st.write("- **Years (合約/年資)**: 合約保障年限或服務年資。")
                    if m_scope == "Hitter":
                        st.write("- **wRC+ (加權得分創造)**: 修正後的攻擊效率（100為聯盟平均）。")
                        st.write("- **Def (防守貢獻)**: 球員在場上相較於平均水準的防守產值。")

        # --- 5. 異常名單排行榜 (維持原始格式) ---
        analysis_df = df_clean[df_clean['WAR'] >= min_war].copy()
        if exclude_rookies:
            analysis_df = analysis_df[analysis_df['Salary_millions'] >= min_salary_threshold]
        
        undervalued = analysis_df[analysis_df['residual_percent'] < -threshold].sort_values('MERI')
        overvalued = analysis_df[analysis_df['residual_percent'] > threshold].sort_values('MERI', ascending=False)
        
        st.markdown("### 🏆 市場定價異常排行榜 (按 MERI 排序)")
        col_tab1, col_tab2 = st.columns(2)
        
        for data_group, col, title, label in zip([undervalued, overvalued], [col_tab1, col_tab2], 
                                                ["💎 高性價比名單 (低於預期身價)", "⚠️ 溢價合約名單 (高於預期身價)"],
                                                ["download_under", "download_over"]):
            with col:
                st.markdown(title)
                if len(data_group) > 0:
                    display_df = data_group.head(20).copy()
                    display_df = display_df[['Name', 'Team', 'WAR', 'Salary_millions', 'expected_salary', 'residual_percent', 'MERI']]
                    display_df.columns = ['姓名', '球隊', 'WAR', '實際薪資(M)', '預期薪資(M)', '差異%', 'MERI 指標']
                    st.dataframe(display_df.round(3), use_container_width=True, hide_index=True)
                    csv = display_df.to_csv(index=False)
                    st.download_button(label=f"📥 下載名單", data=csv, file_name=f"{label}.csv", mime="text/csv", key=label)
                else:
                    st.info("未發現符合條件的球員")

    # --- 6. 殘差分布視覺化 ---
    st.markdown("### 殘差分佈診斷 (Residual Diagnostics)")
    fig_res = px.scatter(analysis_df, x='expected_salary', y='Salary_millions', 
                         hover_name='Name', color='MERI', color_continuous_scale='RdBu_r',
                         title="預期身價 vs. 實際薪資 (顏色代表 MERI 強度)")
    fig_res.add_trace(go.Scatter(x=[0, analysis_df['Salary_millions'].max()], 
                                 y=[0, analysis_df['Salary_millions'].max()], 
                                 mode='lines', line=dict(color='black', dash='dot'), name='效率線'))
    st.plotly_chart(fig_res, use_container_width=True)

elif analysis_mode == "進階策略分析":
    st.markdown('<h2 class="section-title">進階策略分析 (Moneyball & Arbitrage)</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>分析說明：</b> 本模組運用 Moneyball 概念，分析不同守備位置的「購買成本」，尋找市場上的套利機會。
    同時提供手動 OLS 回歸模型檢驗，以供進階統計驗證。
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["位置套利分析 (Moneyball)", "手動 OLS 回歸驗證"])
    
    with tab1:
        st.markdown("### 位置價值與套利分析")
        st.markdown("分析哪個守備位置的「每勝場成本 (Cost per WAR)」最低，尋找市場定價效率較差的領域。")

        pos_arbitrage = analyze_positional_arbitrage(df)
        
        if pos_arbitrage is not None:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_pos = px.bar(
                    pos_arbitrage,
                    x='Position',
                    y='Cost_per_WAR',
                    color='Cost_per_WAR',
                    title='各守備位置的購買成本 (每1 WAR價格)',
                    labels={'Cost_per_WAR': '每單位WAR成本($M)', 'Position': '守備位置'},
                    color_continuous_scale='RdYlGn_r' # 成本越低越綠
                )
                st.plotly_chart(fig_pos, use_container_width=True)  # 保留原始參數
                
            with col2:
                st.markdown("**分析洞察**")
                cheapest = pos_arbitrage.iloc[0]
                most_expensive = pos_arbitrage.iloc[-1]
                
                st.success(f"💰 **最高CP值位置: {cheapest['Position']}**\n\n平均每1 WAR僅需 ${cheapest['Cost_per_WAR']:.2f}M")
                st.error(f"💸 **最昂貴位置: {most_expensive['Position']}**\n\n平均每1 WAR高達 ${most_expensive['Cost_per_WAR']:.2f}M")
                
                st.markdown("---")
                st.dataframe(
                    pos_arbitrage[['Position', 'Cost_per_WAR', 'WAR', 'Salary_millions']]
                    .style.format({'Cost_per_WAR': '{:.2f}', 'WAR': '{:.1f}', 'Salary_millions': '${:.1f}M'}),
                    use_container_width=True,  # 保留原始參數
                    hide_index=True
                )
    
    with tab2:
        st.markdown("### 手動高次多項式迴歸驗證")
        st.markdown("探討自變數與薪資之間的非線性結構，並提供模型整體解釋力檢定。")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            x_col = st.selectbox("選擇自變數 (X)", ['WAR', 'HR', 'RBI', 'ERA'], index=0)
        with col2:
            y_col = st.selectbox("選擇依變數 (Y)", ['Salary_millions', 'value_ratio'], index=0)
        with col3:
            deg = st.number_input("多項式次方", min_value=1, max_value=8, value=1)
            
        if x_col in df.columns and y_col in df.columns:
            data_reg = df[[x_col, y_col]].dropna()
            
            if len(data_reg) > 10:
                result = manual_poly_regression_stats(data_reg[x_col].values, data_reg[y_col].values, deg)
                
                if result:
                    st.markdown("#### 迴歸統計結果")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("R² (決定係數)", f"{result['r_squared']:.4f}")
                    c2.metric("調整後 R²", f"{result['adj_r_squared']:.4f}")
                    c3.metric("F-Statistic", f"{result['f_value']:.2f}")
                    c4.metric("樣本數 (n)", result['n'])
                    
                    st.markdown("#### 多項式方程式")
                    eq_str = format_poly_equation(result['coeffs'], x_col)
                    st.markdown(rf"$$ \widehat{{\text{{{y_col}}}}} = {eq_str} $$")
                    
                    # 繪製曲線
                    fig_poly = px.scatter(data_reg, x=x_col, y=y_col, title=f'{y_col} vs {x_col} ({deg}次方擬合)')
                    x_range = np.linspace(data_reg[x_col].min(), data_reg[x_col].max(), 100)
                    y_pred = result['poly_obj'](x_range)
                    fig_poly.add_trace(go.Scatter(x=x_range, y=y_pred, mode='lines', name='預測曲線', line=dict(color='red')))
                    st.plotly_chart(fig_poly, use_container_width=True)
            else:
                st.error("樣本數不足，無法進行回歸分析")

# 新增：原創財務指標頁面
elif analysis_mode == "原創財務指標":
    st.markdown('<h2 class="section-title">🎓 原創財務指標：計量引擎與風險評價系統</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <b>原創指標說明：</b> 本模組展示根據財務學概念設計的六個原創指標，用於評估 MLB 球員的市場價值、投資效率與風險調整後績效。
    本版本已將 <b>Multivariate OLS (全維度迴歸)</b> 運算結果整合進 MERI 殘差分析中。
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # 核心計量引擎：進入頁面即時運算 (確保數據絕對顯示)
    # ============================================================
    st.sidebar.markdown("---")
    m_scope = st.sidebar.radio("🔭 指標分析基準群組", ["打者模型 (Hitter)", "投手模型 (Pitcher)"], key="om_scope_radio")
    
    m_df = df.copy()
    # 區分投手與打者變數
    if m_scope == "打者模型 (Hitter)":
        X_vars = ['WAR', 'Age', 'Years', 'wRC+', 'Def']
        m_df = m_df[~m_df['Position'].str.contains('P', na=False)]
    else:
        X_vars = ['WAR', 'Age', 'Years']
        m_df = m_df[m_df['Position'].str.contains('P', na=False)]

    # 數據清洗與轉換
    m_df[X_vars + ['Salary_millions']] = m_df[X_vars + ['Salary_millions']].apply(pd.to_numeric, errors='coerce')
    m_df = m_df.dropna(subset=X_vars + ['Salary_millions'])
    m_df['Age_Squared'] = m_df['Age']**2

    # 執行全維度計量迴歸 (取得實測 Beta)
    X_matrix = sm.add_constant(m_df[X_vars + ['Age_Squared']].astype(float))
    y_log = np.log1p(m_df['Salary_millions'].astype(float))
    res_ols = sm.OLS(y_log, X_matrix).fit()
    b = res_ols.params # 提取 Beta 數值
    m_df['Expected_Fair_Value'] = np.expm1(res_ols.fittedvalues) # 還原預測值

    # 重新計算原創指標 (確保欄位在當前 m_df 中絕對存在)
    m_df['MERI'] = ((m_df['Salary_millions'] - m_df['Expected_Fair_Value']) / m_df['Expected_Fair_Value']) * np.log(1 + np.abs(m_df['WAR']))
    # --- 修正：補回 MERI 分類標籤，否則 Plotly 會報錯 ---
    conditions = [
        m_df['MERI'] > 0.5,
        (m_df['MERI'] > 0.1) & (m_df['MERI'] <= 0.5),
        (m_df['MERI'] >= -0.1) & (m_df['MERI'] <= 0.1),
        (m_df['MERI'] >= -0.5) & (m_df['MERI'] < -0.1),
        m_df['MERI'] < -0.5
    ]
    categories = ['嚴重高估', '稍微高估', '合理定價', '稍微低估', '嚴重低估']
    m_df['MERI_category'] = np.select(conditions, categories, default='未知')
    m_df = calculate_wvpi(m_df) # 重新調用 WVPI 計算
    m_df = calculate_rav(m_df)  # 重新調用 RAV 計算

    # ============================================================
    # 分頁展示區域 (保留所有原始 Tab)
    # ============================================================
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "WVPI (加權綜合價值指數)", 
        "RAV (風險調整後價值)", 
        "MERI (市場效率殘差指數)",
        "TPM (雙因子績效矩陣)",
        "PSI (投資組合夏普指數)",
        "SEI (同步效率指數)"
    ])
    
    with tab1:
        st.markdown("### 加權綜合價值指數 (WVPI)")
        st.markdown(r"$$ \text{WVPI} = w_1 \text{WAR} + w_2 \frac{\text{WAR}}{\text{Salary}} + w_3 P_{\text{WAR}} + w_4 (100 - P_{\text{Salary}}) $$")
        
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        comp_cols = ['WAR_norm', 'VR_norm', 'P_WAR', 'P_Salary_inv']
        comp_names = ['絕對表現(WAR)', '效率(VR)', '相對表現(P_WAR)', '相對成本(P_Salary)']
        
        if all(col in m_df.columns for col in comp_cols):
            df_v = m_df.dropna(subset=comp_cols + ['Name', 'Team']).copy()
            scaler = StandardScaler()
            pca = PCA().fit(scaler.fit_transform(df_v[comp_cols]))
            pca_weights = np.abs(pca.components_[0]) / np.sum(np.abs(pca.components_[0]))
            df_v['WVPI_PCA'] = (pca_weights[0]*df_v['WAR_norm'] + pca_weights[1]*df_v['VR_norm'] + 
                                pca_weights[2]*df_v['P_WAR'] + pca_weights[3]*df_v['P_Salary_inv'])
            
            wvpi_tab1, wvpi_tab2 = st.tabs(["📊 績效與排名分析", "⚖️ 權重設定客觀驗證 (PCA)"])
            with wvpi_tab1:
                c_t1, c_t2 = st.columns(2)
                with c_t1:
                    st.markdown("#### 🏆 原創 WVPI 最高球員")
                    st.dataframe(m_df.nlargest(20, 'WVPI')[['Name', 'Team', 'WAR', 'Salary_millions', 'WVPI']].round(2), use_container_width=True, hide_index=True)
                with c_t2:
                    st.markdown("#### 🤖 PCA 基準最高球員")
                    st.dataframe(df_v.nlargest(20, 'WVPI_PCA')[['Name', 'Team', 'WAR', 'Salary_millions', 'WVPI_PCA']].round(2), use_container_width=True, hide_index=True)
                
                c_ch, c_st = st.columns([2, 1])
                with c_ch:
                    st.plotly_chart(px.histogram(m_df, x='WVPI', color='WVPI_category', nbins=40, title='WVPI 分佈與分類'), use_container_width=True)
                with c_st:
                    st.markdown("#### WVPI 分類統計")
                    for cat in ['頂級球星', '優質球員', '普通球員', '效率待提升', '問題合約']:
                        st.metric(cat, len(m_df[m_df['WVPI_category'] == cat]))
            
            with wvpi_tab2:
                st.info("比較主觀財務權重與 PCA 客觀權重的吻合度。")
                cw1, cw2 = st.columns([1, 2])
                with cw1:
                    orig_w = [0.35, 0.30, 0.20, 0.15]
                    compare_df = pd.DataFrame({"維度": comp_names, "原創設定": orig_w, "PCA客觀": pca_weights})
                    st.table(compare_df.style.format({"原創設定": "{:.1%}", "PCA客觀": "{:.1%}"}))
                with cw2:
                    st.plotly_chart(px.scatter(df_v, x='WVPI_PCA', y='WVPI', hover_name='Name', color='WAR', title="兩種評分系統對比"), use_container_width=True)

    with tab2:
        st.markdown("### 風險調整後價值 (RAV)")
        st.latex(r"RAV = \frac{WAR - WAR_{min}}{\sigma_{WAR} + 1} \times \frac{Median(Salary)}{Salary}")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("#### RAV 最高球員 (前20名)")
            st.dataframe(m_df.nlargest(20, 'RAV')[['Name', 'Team', 'Position', 'WAR', 'Salary_millions', 'RAV', 'RAV_category']].round(2), use_container_width=True, hide_index=True)
        with col_r2:
            st.plotly_chart(px.scatter(m_df, x='WAR', y='RAV', color='RAV_category', hover_name='Name', title='RAV vs WAR 關係圖'), use_container_width=True)

    with tab3:
        st.markdown("### 市場效率殘差指數 (MERI) - 計量引擎版")
        
        # --- 1. 恢復被我刪掉的原創公式說明 (理論定義) ---
        st.markdown(r"""
        **MERI** 是基於迴歸分析的殘差概念，加入非線性戰力權重，識別市場異常的指標。
        
        $$ \text{MERI}_i = \frac{\text{Salary}_i - \widehat{\text{Salary}}_i}{\widehat{\text{Salary}}_i} \times \ln(1 + |\text{WAR}_i|) $$
        
        *其中 $\widehat{\text{Salary}}_i$ 為模型推算之預期身價。MERI > 0：代表被高估，MERI < 0：代表被低估。*
        """)

        # --- 2. 注入計量 $\beta$ 實測方程式 (實作細節) ---
        with st.expander("📝 檢視當前迴歸模型之 $\beta$ 參數與變數定義", expanded=False):
            b = res_ols.params
            if m_scope == "打者模型 (Hitter)":
                formula = (rf"\ln(\text{{Salary}}) = {b['const']:.3f} + {b['WAR']:.3f}(\text{{WAR}}) + {b['Age']:.3f}(\text{{Age}}) "
                           rf"- {abs(b['Age_Squared']):.4f}(\text{{Age}}^2) + {b['Years']:.3f}(\text{{Years}}) "
                           rf"+ {b['wRC+']:.4f}(\text{{wRC+}}) - {abs(b['Def']):.3f}(\text{{Def}})")
            else:
                formula = (rf"\ln(\text{{Salary}}) = {b['const']:.3f} + {b['WAR']:.3f}(\text{{WAR}}) + {b['Age']:.3f}(\text{{Age}}) "
                           rf"- {abs(b['Age_Squared']):.4f}(\text{{Age}}^2) + {b['Years']:.3f}(\text{{Years}})")
            
            st.write("**實測計量定價方程式：**")
            st.latex(formula)
            
            st.markdown("---")
            st.markdown("**變數中文說明與財務意義：**")
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.write("- **WAR (勝場貢獻值)**: 衡量球員相較於替補球員的「超額技術產出」。")
                st.write("- **Age (年齡)**: 球員生理年資。")
                st.write("- **Age² (年齡平方)**: 捕捉「生理折舊」，反映隨年齡增長而遞減的邊際報酬。")
            with c_v2:
                st.write("- **Years (服務年資)**: 制度保障年限，反映 MLB 薪資體系的結構性溢價。")
                if m_scope == "打者模型 (Hitter)":
                    st.write("- **wRC+ (加權得分創造)**: 進攻純效率指標，100 為聯盟平均。")
                    st.write("- **Def (防守產值)**: 守備對球隊的隱性價值貢獻。")

        # --- 3. 異常名單排行榜 (不准動你的欄位) ---
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success("💎 **計量定價 - 真正低估球員 (MERI < 0)**")
            st.dataframe(m_df.nsmallest(20, 'MERI')[['Name', 'Team', 'WAR', 'Salary_millions', 'Expected_Fair_Value', 'MERI']].round(3), use_container_width=True, hide_index=True)
        with col_m2:
            st.error("⚠️ **計量定價 - 真正高估球員 (MERI > 0)**")
            st.dataframe(m_df.nlargest(20, 'MERI')[['Name', 'Team', 'WAR', 'Salary_millions', 'Expected_Fair_Value', 'MERI']].round(3), hide_index=True)
        
        # --- 4. 恢復分類分佈圖 ---
        st.plotly_chart(px.histogram(m_df, x='MERI', color='MERI_category', nbins=50, title='全維度 MERI 分佈圖'), use_container_width=True)
    
    with tab4:
        st.markdown("### 雙因子績效矩陣 (TPM)")
        st.markdown("""
        **TPM** 是一個 2×2 的分類矩陣，根據 WAR 百分位和性價比百分位將球員分為四類。
        
        | 象限 | WAR 百分位 | 性價比百分位 | 類別 |
        | :--- | :--- | :--- | :--- |
        | **Q1** | ≥ 50 | ≥ 50 | 明星價值 |
        | **Q2** | ≥ 50 | < 50 | 溢價球星 |
        | **Q3** | < 50 | ≥ 50 | 潛力新秀 |
        | **Q4** | < 50 | < 50 | 球隊冗員 |
        """)
        
        # --- 核心修正：正確接回帶有標籤的 m_df ---
        tpm_fig, m_df = plot_tpm_matrix(m_df)
        if tpm_fig is not None:
            st.plotly_chart(tpm_fig, use_container_width=True)
            
            st.markdown("#### 各象限球員分佈統計")
            # 確保欄位存在後進行計數
            qc = m_df['TPM_category'].value_counts()
            
            cq1, cq2, cq3, cq4 = st.columns(4)
            cq1.metric("⭐ 明星價值", qc.get('明星價值', 0))
            cq2.metric("💰 溢價球星", qc.get('溢價球星', 0))
            cq3.metric("🌱 潛力新秀", qc.get('潛力新秀', 0))
            cq4.metric("📉 球隊冗員", qc.get('球隊冗員', 0))

    with tab5:
        st.markdown("### 投資組合夏普指數 (PSI)")
        st.markdown(r"""
        **PSI** 將球隊視為投資組合，評估風險調整後的績效表現。
        
        $$ \text{PSI}_t = \frac{\text{總WAR}_t - \text{總薪資}_t \times \bar{e}_{\text{league}}}{\sigma_{\text{WAR}}^{\text{team}}} $$
        
        其中 $\bar{e}_{\text{league}}$ 為聯盟平均效率（每百萬美元可獲得的 WAR），$\sigma_{\text{WAR}}^{\text{team}}$ 為球隊內部球員表現的標準差（代表投資風險）。
        """)
        
        # 計算聯盟基準效率
        league_eff = m_df['WAR'].sum() / m_df['Salary_millions'].sum()
        
        # 計算各球隊 PSI
        t_psi_list = []
        for team in m_df['Team'].unique():
            td = m_df[m_df['Team'] == team]
            if len(td) >= 3: # 至少 3 人才計算風險(標準差)
                team_war_sum = td['WAR'].sum()
                team_salary_sum = td['Salary_millions'].sum()
                team_risk = td['WAR'].std()
                
                # 計算 PSI
                if team_risk > 0:
                    psi_val = (team_war_sum - (team_salary_sum * league_eff)) / team_risk
                else:
                    psi_val = 0
                    
                t_psi_list.append({
                    'Team': team,
                    'PSI': psi_val,
                    '總WAR': team_war_sum,
                    '總薪資(M)': team_salary_sum,
                    '球隊風險(σ)': team_risk
                })
        
        if t_psi_list:
            psi_results = pd.DataFrame(t_psi_list).sort_values('PSI', ascending=False)
            
            c_p1, c_p2 = st.columns([1, 1])
            with c_p1:
                st.markdown("**球隊管理效率排名**")
                st.dataframe(psi_results[['Team', 'PSI', '總WAR', '總薪資(M)']].round(3), 
                             use_container_width=True, hide_index=True)
            
            with c_p2:
                # PSI 管理評價分類
                def eval_psi(p):
                    if p > 1.5: return '卓越管理'
                    if p > 0.5: return '良好管理'
                    if p > -0.5: return '平庸管理'
                    return '效率不佳'
                
                psi_results['管理評價'] = psi_results['PSI'].apply(eval_psi)
                eval_counts = psi_results['管理評價'].value_counts()
                st.plotly_chart(px.pie(values=eval_counts.values, names=eval_counts.index, 
                                       title="全聯盟管理品質分佈", hole=0.4), use_container_width=True)
            
            # PSI 柱狀圖
            st.plotly_chart(px.bar(psi_results, x='Team', y='PSI', color='PSI', 
                                   color_continuous_scale='RdYlGn', title="各球隊投資組合夏普指數排名"), 
                            use_container_width=True)

    with tab6:
        st.markdown("### 同步效率指數 (SEI)")
        st.markdown(r"""
        **SEI** 結合市場相關性與分配公平性，是一個衡量整體市場健康度的宏觀指標。
        
        $$ \text{SEI} = \rho(\text{WAR}, \text{Salary}) \times (1 - G_{\text{Salary}}) $$
        
        其中 $\rho$ 為 WAR 與薪資的相關係數，$G$ 為薪資的基尼係數。
        """)
        
        # 計算相關係數 (ρ)
        corr_val = m_df['WAR'].corr(m_df['Salary_millions'])
        
        # 計算基尼係數 (G)
        sal_sorted = np.sort(m_df['Salary_millions'].dropna().values)
        n = len(sal_sorted)
        if n > 0:
            index = np.arange(1, n + 1)
            gini_val = ((2 * index - n - 1) * sal_sorted).sum() / (n * sal_sorted.sum())
        else:
            gini_val = 0
            
        # 計算 SEI
        sei_val = corr_val * (1 - gini_val)
        
        c_s1, c_s2, c_s3 = st.columns(3)
        c_s1.metric("相關係數 (ρ)", f"{corr_val:.4f}")
        c_s2.metric("基尼係數 (G)", f"{gini_val:.4f}")
        c_s3.metric("同步效率 (SEI)", f"{sei_val:.4f}")
        
        st.markdown("#### 市場狀態象限分析")
        
        # 繪製市場狀態矩陣
        fig_sei = go.Figure()
        
        # 添加象限背景顏色
        # 左下: 混亂 (紅), 右下: 平均 (橙), 左上: 菁英 (藍), 右上: 理想 (綠)
        fig_sei.add_shape(type="rect", x0=0, y0=0, x1=0.5, y1=0.5, fillcolor="rgba(239, 83, 80, 0.1)", line_width=0)
        fig_sei.add_shape(type="rect", x0=0.5, y0=0, x1=1, y1=0.5, fillcolor="rgba(255, 167, 38, 0.1)", line_width=0)
        fig_sei.add_shape(type="rect", x0=0, y0=0.5, x1=0.5, y1=1, fillcolor="rgba(66, 165, 245, 0.1)", line_width=0)
        fig_sei.add_shape(type="rect", x0=0.5, y0=0.5, x1=1, y1=1, fillcolor="rgba(102, 187, 106, 0.1)", line_width=0)
        
        # 添加標籤
        fig_sei.add_annotation(x=0.25, y=0.25, text="混亂市場", showarrow=False, font=dict(color="gray"))
        fig_sei.add_annotation(x=0.75, y=0.25, text="平均主義", showarrow=False, font=dict(color="gray"))
        fig_sei.add_annotation(x=0.25, y=0.75, text="菁英市場", showarrow=False, font=dict(color="gray"))
        fig_sei.add_annotation(x=0.75, y=0.75, text="理想市場", showarrow=False, font=dict(color="gray"))
        
        # 標註當前位置
        fig_sei.add_trace(go.Scatter(
            x=[gini_val], y=[corr_val],
            mode='markers+text',
            marker=dict(size=25, color='red', symbol='star'),
            text=['當前市場'], textposition='top center'
        ))
        
        fig_sei.update_layout(
            title="MLB 市場定價效率矩陣圖",
            xaxis_title="薪資基尼係數 (G) → 不公平度",
            yaxis_title="表現相關係數 (ρ) → 效率度",
            xaxis_range=[0, 1], yaxis_range=[0, 1],
            height=500, showlegend=False
        )
        st.plotly_chart(fig_sei, use_container_width=True)
        
        with st.expander("🎓 市場狀態學術解讀"):
            st.markdown("""
            1. **理想市場 (右上)**: 薪資與表現高度相關，且薪資分配相對合理。
            2. **菁英市場 (左上)**: 表現決定薪資，但極少數巨星拿走絕大部分預算。
            3. **平均主義 (右下)**: 薪資分配平均，但薪資水平與場上表現脫節。
            4. **混亂市場 (左下)**: 表現與薪資無關，且薪資集中在少數人手中。
            """)

elif analysis_mode == "公式與變數說明":
    st.markdown('<h2 class="section-title">公式與變數說明</h2>', unsafe_allow_html=True)
    
    # 使用標籤頁組織內容
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["數據來源", "打者指標", "投手指標", "薪資分析", "分析方法", "原創財務指標"])
    
    with tab1:
        st.markdown("""
        ## 數據來源與工具
        
        ### 數據獲取工具
        - **pybaseball**: Python套件，用於獲取MLB官方統計數據
        - **數據年限**: 2023年賽季
        - **資格限制**: 
          - 打者: 至少50個打席 (qual=50)
          - 投手: 至少30局投球 (qual=30)
        
        ### 數據結構
        ```python
        # 主要數據欄位結構
        data = {
            'Name': '球員姓名',
            'Team': '所屬球隊',
            'Position': '守備位置',
            'WAR': '勝場貢獻值',
            'Salary_millions': '薪資（百萬美元）'
        }
        ```
        """)
    
    with tab2:
        st.markdown("""
        ## 打者表現指標
        
        ### 基礎傳統指標
        | 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
        |--------|----------|----------|--------------|
        | **Name** | Player Name | 球員姓名 | - |
        | **Team** | Team | 所屬球隊 | - |
        | **W** | Wins | 勝場數 | 球員所屬球隊在該球員出賽時的勝場數 |
        | **L** | Losses | 敗場數 | 球員所屬球隊在該球員出賽時的敗場數 |
        | **W-L%** | Win-Loss Percentage | 勝率 | W / (W + L) |
        | **GB** | Games Behind | 勝差 | 與分區領先球隊的勝場差 |
        
        ### 打擊表現指標
        | 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
        |--------|----------|----------|--------------|
        | **PA** | Plate Appearances | 打席數 | 上場打擊的次數 |
        | **AB** | At Bats | 打數 | 打席數扣除保送、犧牲打等 |
        | **R** | Runs | 得分 | 跑回本壘得分 |
        | **H** | Hits | 安打數 | - |
        | **2B** | Doubles | 二壘安打 | - |
        | **3B** | Triples | 三壘安打 | - |
        | **HR** | Home Runs | 全壘打 | - |
        | **RBI** | Runs Batted In | 打點 | 使跑者得分 |
        | **SB** | Stolen Bases | 盜壘成功 | - |
        | **CS** | Caught Stealing | 盜壘失敗 | - |
        
        ### 進階打擊率指標
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **打擊率 (AVG)**
        ```
        AVG = H / AB
        ```
        衡量擊出安打的能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **上壘率 (OBP)**
        ```
        OBP = (H + BB + HBP) / (AB + BB + HBP + SF)
        ```
        衡量上壘能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **長打率 (SLG)**
        ```
        SLG = (1B + 2×2B + 3×3B + 4×HR) / AB
        ```
        衡量長打能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **綜合攻擊指數 (OPS)**
        ```
        OPS = OBP + SLG
        ```
        綜合評估攻擊能力
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 進階分析指標
        | 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 | 
        |--------|----------|----------|--------------|
        | **WAR** | Wins Above Replacement | 勝場貢獻值 | 衡量球員比替補球員多貢獻多少勝場 | 
        | **wOBA** | Weighted On-Base Average | 加權上壘率 | 考慮不同上壘方式的價值 | 
        | **wRC+** | Weighted Runs Created Plus | 調整後得分創造 | 100為聯盟平均，>100優於平均 | 
        | **OPS+** | Adjusted OPS | 調整後OPS | 考慮球場因素，100為聯盟平均 | 
        """)
    
    with tab3:
        st.markdown("""
        ## 投手表現指標
        
        ### 基礎投球數據
        | 變數名 | 英文全名 | 中文名稱 | 說明 |
        |--------|----------|----------|------|
        | **W** | Wins | 勝投 | 先發投手投滿5局且球隊領先時退場 |
        | **L** | Losses | 敗投 | 失分導致球隊落後時退場 |
        | **ERA** | Earned Run Average | 防禦率 | 每9局自責分，越低越好 |
        | **G** | Games | 出賽數 | - |
        | **GS** | Games Started | 先發場次 | - |
        | **CG** | Complete Games | 完投 | 投完整場比賽 |
        | **SHO** | Shutouts | 完封 | 完投且對方未得分 |
        
        ### 投球結果數據
        | 變數名 | 英文全名 | 中文名稱 | 計算公式 |
        |--------|----------|----------|----------|
        | **IP** | Innings Pitched | 投球局數 | 如 202.1 表示202又1/3局 |
        | **H** | Hits Allowed | 被安打數 | - |
        | **R** | Runs Allowed | 失分 | - |
        | **ER** | Earned Runs | 自責分 | 扣除隊友失誤導致的失分 |
        | **HR** | Home Runs Allowed | 被全壘打數 | - |
        | **BB** | Walks | 保送 | - |
        | **SO** | Strikeouts | 三振 | - |
        
        ### 進階投球指標
        | 變數名 | 英文全名 | 中文名稱 | 計算公式/說明 |
        |--------|----------|----------|--------------|
        | **WAR** | Wins Above Replacement | 勝場貢獻值 | 投手版，衡量對球隊勝場貢獻 |
        | **WHIP** | Walks and Hits per Inning | 每局被上壘率 | (BB + H) / IP |
        | **FIP** | Fielding Independent Pitching | 防守獨立投球指數 | 只考慮三振、保送、全壘打的防禦率 |
        | **xFIP** | Expected FIP | 預期FIP | 考慮被擊球品質調整的FIP |
        """)
    
    with tab4:
        st.markdown("""
        ## 薪資相關變數
        
        ### 主要薪資變數
        | 變數名 | 說明 | 計算公式 |
        |--------|------|----------|
        | **Salary_millions** | 薪資（百萬美元） | 實際薪資除以1,000,000 |
        | **value_ratio** | 性價比 | WAR / salary_in_millions |
        | **salary_percentile** | 薪資百分位 | 薪資在樣本中的百分位排名 |
        | **salary_category** | 薪資級別 | 四分位數分組（低/中低/中高/高） |
        
        ### 性價比計算
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **性價比 (Value Ratio)**
        ```
        value_ratio = WAR / Salary_millions
        ```
        意義：每百萬美元薪資能獲得多少WAR
        - 值越高表示球員越「划算」
        - 值越低表示球員越「昂貴」
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 薪資級別分類
        使用四分位數將球員分為四個薪資級別：
        1. **低薪資**：最低25%的薪資
        2. **中低薪資**：25%-50%的薪資
        3. **中高薪資**：50%-75%的薪資
        4. **高薪資**：最高25%的薪資
        """)
    
    with tab5:
        st.markdown("""
        ## 分析方法
        
        ### 1. 預期薪資定價模型 (多項式迴歸)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown(r"""
        **高次方多項式迴歸模型**
        
        為解決傳統線性迴歸無法捕捉頂級球員「稀缺性溢價」的缺陷，本系統升級採用多項式迴歸建立預期薪資基準：
        $$\widehat{\text{Salary}} = \beta_n \text{WAR}^n + \dots + \beta_1 \text{WAR} + \beta_0$$
        
        說明：
        - 採用 3 至 4 次方可使曲線尾端自然上揚，合理化巨星（如 Aaron Judge, 大谷翔平）的超高薪資，避免其在異常偵測中被系統性誤判為「嚴重高估」。
        - 設定底薪防呆機制：$\widehat{\text{Salary}} = \max(\widehat{\text{Salary}}, 0.7)$
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 2. 市場異常偵測
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **薪資殘差計算**
        ```
        salary_residual = actual_salary - expected_salary
        ```
        **差異百分比**
        ```
        residual_percent = (salary_residual / expected_salary) × 100%
        ```
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 3. 市場效率指標
        
        #### 決定係數 (R²)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        ```
        R² = 1 - (SS_res / SS_tot)
        ```
        意義：模型能解釋的薪資變異比例。模型次方數越高，R² 通常越大，但需防範過度擬合 (Overfitting)。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 4. 球隊效率分析
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        **球隊效率**
        ```
        team_efficiency = total_WAR / total_salary
        ```
        意義：每百萬美元團隊薪資能獲得多少總 WAR。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab6:
        st.markdown("""
        ## 原創財務指標 (依據 new_variables.md)
        
        ### 1. 加權綜合價值指數 (WVPI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{WVPI} = w_1 \\times \\text{WAR} + w_2 \\times \\frac{\\text{WAR}}{\\text{Salary}} + w_3 \\times P_{\\text{WAR}} + w_4 \\times (100 - P_{\\text{Salary}}) $$
        
        權重：$w_1=0.35, w_2=0.30, w_3=0.20, w_4=0.15$
        
        意義：多維度球員評估，結合絕對表現、效率、相對排名與成本效益。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 2. 風險調整後價值 (RAV)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{RAV} = \\frac{\\text{WAR} - \\text{WAR}_{\\text{min}}}{\\sigma_{\\text{WAR}} + 1} \\times \\frac{\\text{Median}(\\text{Salary})}{\\text{Salary}} $$
        
        意義：借鑑夏普比率，衡量風險調整後的超額貢獻。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 3. 市場效率殘差指數 (MERI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{MERI}_i = \\frac{\\text{Salary}_i - \\widehat{\\text{Salary}}_i}{\\widehat{\\text{Salary}}_i} \\times \\ln(1 + \\text{WAR}_i) $$
        
        意義：基於迴歸殘差，加入非線性權重，識別市場異常。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 4. 投資組合夏普指數 (PSI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{PSI}_t = \\frac{\\text{WAR}_t^{\\text{team}} - \\text{Salary}_t^{\\text{team}} \\times \\bar{e}_{\\text{league}}}{\\sigma_{\\text{WAR}}^{\\text{team}}} $$
        
        意義：將球隊視為投資組合，評估風險調整後的績效表現。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 5. 雙因子績效矩陣 (TPM)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$
        \\text{Category}(i) = 
        \\begin{cases}
        \\text{明星價值} & \\text{if } Q_{\\text{WAR}} \\geq 50 \\text{ and } Q_{\\text{Value}} \\geq 50 \\\\
        \\text{溢價球星} & \\text{if } Q_{\\text{WAR}} \\geq 50 \\text{ and } Q_{\\text{Value}} < 50 \\\\
        \\text{潛力新秀} & \\text{if } Q_{\\text{WAR}} < 50 \\text{ and } Q_{\\text{Value}} \\geq 50 \\\\
        \\text{球隊冗員} & \\text{if } Q_{\\text{WAR}} < 50 \\text{ and } Q_{\\text{Value}} < 50
        \\end{cases}
        $$
        
        意義：2×2分類矩陣，根據WAR百分位和性價比百分位分類球員。
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 6. 同步效率指數 (SEI)
        """)
        
        st.markdown('<div class="formula-box">', unsafe_allow_html=True)
        st.markdown("""
        $$ \\text{SEI} = \\rho(\\text{WAR}, \\text{Salary}) \\times (1 - G_{\\text{Salary}}) $$
        
        意義：結合市場相關性與分配公平性，總體市場健康指標。
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 頁尾
# ============================================================
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #6B7280; padding: 1rem 0;">
    <p style="font-size: 0.9rem;">
        MLB薪資市場效率分析專題 | 指導教授: 黃宜侯 | 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)

