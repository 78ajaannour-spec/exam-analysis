import streamlit as st
import pandas as pd

# 1. إعداد الصفحة
st.set_page_config(page_title="تحليل الامتحانات", layout="wide")
st.title("📊 نظام تحليل نتائج الامتحانات")

# 2. القائمة الجانبية للتحميل
st.sidebar.header("📂 1. رفع الملف")
uploaded_file = st.sidebar.file_uploader("اختر ملف البيانات (CSV أو Excel)", type=['csv', 'xlsx'])

# 3. دالة المعالجة
@st.cache_data
def load_data(file):
    try:
        # قراءة الملف حسب نوعه
        if file.name.lower().endswith('.csv'):
            df = pd.read_csv(file, delimiter=';')
        else:
            df = pd.read_excel(file)

        # تنظيف التواريخ
        if 'Examen.datum' in df.columns:
            df['Examen.datum'] = pd.to_datetime(df['Examen.datum'], dayfirst=True, errors='coerce')
        
        # تنظيف النتائج
        if 'Resultaat.uitslag' in df.columns:
            df['Resultaat.uitslag'] = df['Resultaat.uitslag'].astype(str).str.upper().str.strip()
            
        return df
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")
        return None

# 4. التشغيل الرئيسي
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.sidebar.markdown("---")
        st.sidebar.header("🔍 2. خيارات البحث")
        
        # التأكد من وجود تواريخ
        if 'Examen.datum' in df.columns and df['Examen.datum'].notnull().any():
            min_date = df['Examen.datum'].min().date()
            max_date = df['Examen.datum'].max().date()
            
            start_date = st.sidebar.date_input("من تاريخ", min_date)
            end_date = st.sidebar.date_input("إلى تاريخ", max_date)
            
            # فلتر التاريخ
            mask = (df['Examen.datum'].dt.date >= start_date) & (df['Examen.datum'].dt.date <= end_date)
        else:
            st.warning("⚠️ عمود التاريخ غير موجود أو فارغ!")
            mask = pd.Series([True] * len(df))

        # فلتر المراكز
        if 'Algemeen.locatie_naam' in df.columns:
            all_locs = sorted(df['Algemeen.locatie_naam'].dropna().astype(str).unique())
            selected_locs = st.sidebar.multiselect("المراكز:", all_locs)
            if selected_locs:
                mask = mask & df['Algemeen.locatie_naam'].isin(selected_locs)

        # فلتر الرموز
        if 'Algemeen.product_code' in df.columns:
            all_codes = sorted(df['Algemeen.product_code'].dropna().astype(str).unique())
            selected_codes = st.sidebar.multiselect("الرموز:", all_codes)
            if selected_codes:
                mask = mask & df['Algemeen.product_code'].isin(selected_codes)

        # تطبيق الفلاتر
        filtered_df = df[mask]

        # عرض النتائج
        st.markdown("---")
        st.subheader(f"النتائج: {len(filtered_df)} طالب")
        
        if 'Resultaat.uitslag' in filtered_df.columns:
            passed = len(filtered_df[filtered_df['Resultaat.uitslag'] == 'V'])
            failed = len(filtered_df[filtered_df['Resultaat.uitslag'] == 'O'])
            total = passed + failed
            rate = (passed / total * 100) if total > 0 else 0
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("العدد المحسوب (V+O)", total)
            c2.metric("✅ ناجح", passed)
            c3.metric("❌ راسب", failed)
            c4.metric("📈 نسبة النجاح", f"{rate:.1f}%")
        
        with st.expander("عرض الجدول"):
            st.dataframe(filtered_df)
            
else:
    st.info("👈 يرجى رفع ملف CSV أو Excel من القائمة الجانبية للبدء.")