import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
import openpyxl

# إعداد الصفحة
st.set_page_config(
    page_title="أتمتة إضافة مراجع WebBeds",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "تطبيق أتمتة إضافة مراجع WebBeds - الإصدار 1.0"
    }
)

# إضافة شعار WebBeds وتنسيق CSS
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
    }
    .logo-section {
        text-align: center;
    }
    .logo-section img {
        max-width: 150px;
        height: auto;
    }
    .title-section h1 {
        color: #d32f2f;
        text-align: center;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# عرض الشعار والعنوان
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="header-container">
        <div class="logo-section">
            <img src="https://www.webbeds.com/cache/sites/site_3/assets/images/logo_horizontal.png" alt="WebBeds Logo" style="max-width: 150px;">
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("<h1 style='text-align: center; color: #d32f2f;'>🤖 أتمتة إضافة مراجع WebBeds</h1>", unsafe_allow_html=True)

def load_excel(file, sheet_name=None):
    """تحميل ملف Excel أو CSV"""
    try:
        # التحقق من نوع الملف
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            if sheet_name:
                return pd.read_excel(file, sheet_name=sheet_name)
            else:
                return pd.read_excel(file)
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {str(e)}")
        return None

def get_sheet_names(file):
    """الحصول على أسماء الأوراق في ملف Excel (CSV ليس له أوراق)"""
    try:
        if file.name.endswith('.csv'):
            return ['Sheet1']  # CSV ملف واحد فقط
        xl_file = pd.ExcelFile(file)
        return xl_file.sheet_names
    except:
        return []

def extract_booking_number(webbeds_booking):
    """استخراج رقم الحجز من WebBeds Booking Number"""
    if pd.isna(webbeds_booking):
        return ""
    booking_str = str(webbeds_booking)
    number = re.sub(r'HTL-WBD-', '', booking_str)
    return number.strip()

def is_valid_supplier_reference(ref):
    """التحقق من صحة Supplier Reference"""
    if pd.isna(ref) or ref == "" or str(ref).strip() == "":
        return False
    try:
        float(str(ref))
        return True
    except:
        return False

def compare_files(webbeds_df, jood_df):
    """مقارنة ملفات WebBeds مع جود وإرجاع الحجوزات التي تحتاج مراجع"""
    
    # التحقق من الأعمدة المطلوبة
    required_webbeds = ['WebBeds Booking Number', 'Supplier reference']
    required_jood = ['ClientReference', 'HotelConf']
    
    missing_wb = [col for col in required_webbeds if col not in webbeds_df.columns]
    missing_jood = [col for col in required_jood if col not in jood_df.columns]
    
    if missing_wb:
        st.error(f"أعمدة مفقودة في ملف WebBeds: {', '.join(missing_wb)}")
        return None, None
    
    if missing_jood:
        st.error(f"أعمدة مفقودة في ملف جود: {', '.join(missing_jood)}")
        return None, None
    
    # استخراج أرقام الحجز
    webbeds_df = webbeds_df.copy()
    webbeds_df['BookingNumber'] = webbeds_df['WebBeds Booking Number'].apply(extract_booking_number)
    
    # تحويل ClientReference إلى نص
    jood_df = jood_df.copy()
    jood_df['ClientReference'] = jood_df['ClientReference'].astype(str)
    
    results = []
    automation_data = []
    
    for idx, wb_row in webbeds_df.iterrows():
        booking_number = wb_row['BookingNumber']
        supplier_ref = wb_row['Supplier reference']
        
        # البحث عن المطابقة في ملف جود
        jood_match = jood_df[jood_df['ClientReference'] == booking_number]
        
        if not jood_match.empty:
            jood_row = jood_match.iloc[0]
            hotel_conf = jood_row['HotelConf']
            
            # التحقق من حالة Supplier Reference
            needs_reference = not is_valid_supplier_reference(supplier_ref)
            
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'موجود',
                'HotelConf': hotel_conf,
                'Action_Needed': 'يحتاج إضافة مرجع' if needs_reference else 'موجود بالفعل',
                'Status': 'يحتاج إجراء' if needs_reference else 'مكتمل'
            }
            
            # إضافة للأتمتة إذا كان يحتاج مرجع
            if needs_reference:
                automation_data.append({
                    'ClientReference': booking_number,
                    'HotelConf': hotel_conf
                })
        else:
            result = {
                'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                'Booking_Number': booking_number,
                'Current_Supplier_Reference': supplier_ref,
                'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                'Jood_Match': 'لا يوجد',
                'HotelConf': '',
                'Action_Needed': 'غير موجود في جود',
                'Status': 'لا يحتاج إجراء'
            }
        
        results.append(result)
    
    return pd.DataFrame(results), pd.DataFrame(automation_data)

def export_excel(dict_of_dfs):
    """تصدير عدة DataFrames إلى ملف Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dict_of_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

# واجهة المستخدم
st.markdown("---")

# قسم رفع الملفات
st.header("📁 رفع الملفات")

col1, col2 = st.columns(2)

with col1:
    st.subheader("ملف WebBeds")
    webbeds_file = st.file_uploader("webbeds_sheet.xlsx", type=['xlsx', 'csv'], key="webbeds")
    webbeds_sheet = None
    if webbeds_file:
        sheets = get_sheet_names(webbeds_file)
        if len(sheets) > 1:
            webbeds_sheet = st.selectbox("اختر الورقة:", sheets, key="wb_sheet")
        else:
            webbeds_sheet = sheets[0] if sheets else None

with col2:
    st.subheader("ملف جود (arrivals_jood_webbeds)")
    jood_file = st.file_uploader("arrivals_jood_webbeds.xlsx", type=['xlsx', 'csv'], key="jood")
    jood_sheet = None
    if jood_file:
        sheets = get_sheet_names(jood_file)
        if len(sheets) > 1:
            jood_sheet = st.selectbox("اختر الورقة:", sheets, key="jood_sheet")
        else:
            jood_sheet = sheets[0] if sheets else None

st.markdown("---")

# زر المقارنة
if st.button("🔍 مقارنة الملفات", type="primary"):
    if not all([webbeds_file, jood_file]):
        st.error("يرجى رفع كلا الملفين")
    else:
        with st.spinner("جاري مقارنة الملفات..."):
            webbeds_df = load_excel(webbeds_file, webbeds_sheet)
            jood_df = load_excel(jood_file, jood_sheet)
            
            if all([df is not None for df in [webbeds_df, jood_df]]):
                comparison_results, automation_data = compare_files(webbeds_df, jood_df)
                
                if comparison_results is not None:
                    st.session_state['comparison_results'] = comparison_results
                    st.session_state['automation_data'] = automation_data
                    st.session_state['audit_completed'] = True
                    st.success("✅ تمت المقارنة بنجاح!")

# عرض النتائج
if st.session_state.get('audit_completed', False):
    st.markdown("---")
    st.header("📊 نتائج المقارنة")
    
    comparison_results = st.session_state['comparison_results']
    automation_data = st.session_state['automation_data']
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bookings = len(comparison_results)
        st.metric("إجمالي الحجوزات", total_bookings)
    
    with col2:
        matched_bookings = len(comparison_results[comparison_results['Jood_Match'] == 'موجود'])
        st.metric("الحجوزات المطابقة", matched_bookings)
    
    with col3:
        need_action = len(comparison_results[comparison_results['Status'] == 'يحتاج إجراء'])
        st.metric("يحتاج إضافة مرجع", need_action)
    
    with col4:
        completed = len(comparison_results[comparison_results['Status'] == 'مكتمل'])
        st.metric("مكتمل", completed)
    
    # عرض الجدول مع فلترة
    st.subheader("تفاصيل المقارنة")
    
    filter_option = st.selectbox("عرض:", ["الكل", "يحتاج إضافة مرجع", "مكتمل", "غير موجود في جود"])
    
    if filter_option == "يحتاج إضافة مرجع":
        filtered_results = comparison_results[comparison_results['Status'] == 'يحتاج إجراء']
    elif filter_option == "مكتمل":
        filtered_results = comparison_results[comparison_results['Status'] == 'مكتمل']
    elif filter_option == "غير موجود في جود":
        filtered_results = comparison_results[comparison_results['Jood_Match'] == 'لا يوجد']
    else:
        filtered_results = comparison_results
    
    st.dataframe(filtered_results, use_container_width=True)
    
    # قسم التحميل
    st.markdown("---")
    st.header("📥 تحميل النتائج")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # تحميل نتائج المقارنة
        comparison_excel = export_excel({
            'comparison_results': comparison_results,
            'need_action': comparison_results[comparison_results['Status'] == 'يحتاج إجراء'],
            'completed': comparison_results[comparison_results['Status'] == 'مكتمل']
        })
        
        st.download_button(
            label="📥 تحميل نتائج المقارنة",
            data=comparison_excel,
            file_name="webbeds_comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        # تحميل ملف الأتمتة (ClientReference + HotelConf فقط)
        if not automation_data.empty:
            # تحميل CSV (أبسط للقراءة)
            csv_data = automation_data.to_csv(index=False)
            
            st.download_button(
                label="📄 تحميل ملف الأتمتة (CSV)",
                data=csv_data,
                file_name="automation_data.csv",
                mime="text/csv"
            )
            
            automation_excel = export_excel({
                'automation_data': automation_data
            })
            
            st.download_button(
                label="📥 تحميل ملف الأتمتة (Excel)",
                data=automation_excel,
                file_name="automation_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success(f"✅ ملف الأتمتة يحتوي على {len(automation_data)} حجز")
        else:
            st.info("لا توجد حجوزات تحتاج إضافة مراجع")

# معلومات إضافية
st.markdown("---")
st.markdown("""
### 📋 تعليمات الاستخدام:

1. **رفع الملفات**:
   - ملف WebBeds (يحتوي على WebBeds Booking Number و Supplier reference)
   - ملف جود arrivals_jood_webbeds (يحتوي على ClientReference و HotelConf)

2. **المقارنة**:
   - يستخرج الأرقام من WebBeds Booking Number (يزيل HTL-WBD-)
   - يطابق مع ClientReference في ملف جود
   - يتحقق من وجود Supplier Reference صحيح

3. **التحميل**:
   - ملف نتائج المقارنة الكامل
   - ملف الأتمتة يحتوي على ClientReference و HotelConf فقط للحجوزات التي تحتاج مراجع

### 🤖 استخدام ملف الأتمتة:
- حمل ملف "automation_data.xlsx"
- استخدمه في Chrome Extension للأتمتة
- يحتوي على ClientReference (للبحث) و HotelConf (للإضافة)
""")