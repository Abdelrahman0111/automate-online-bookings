import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
import openpyxl

# إعداد الصفحة
st.set_page_config(
    page_title="🚀 أتمتة حجوزات الأونلاين",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "أتمتة حجوزات الأونلاين - نظام ذكي لإدارة المراجع والحجوزات"
    }
)

# تنسيق صفحة مخصص
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 3em;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .main-header p {
        font-size: 1.2em;
        margin: 10px 0;
        opacity: 0.95;
    }
    .section-header {
        border-left: 5px solid #667eea;
        padding-left: 15px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
    <div class="main-header">
        <h1>🚀 أتمتة حجوزات الأونلاين</h1>
        <p>نظام ذكي للتعامل مع المراجع والحجوزات</p>
        <p style="font-size: 0.9em; opacity: 0.9;">WebBeds | EET Global | العطايا | Safa | وجميع الشركات الأخرى</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("")

# اختيار نوع العملية
st.markdown("""
    <div class="section-header">
        <h2>⚙️ اختر نوع العملية</h2>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    st.info("💼 **WebBeds**\nللتعامل مع حجوزات WebBeds")

with col2:
    st.info("🏢 **Extranet**\nللشركات الأخرى (EET Global، العطايا، Safa، إلخ)")

with col3:
    st.info("✈️ **Almosafer**\nللتعامل مع حجوزات المسافر")

with col4:
    st.info("📊 معلومات إضافية\nسيتم عرض تفاصيل المقارنة")

operation_type = st.selectbox(
    "اختر نوع العملية التي تريدها:",
    ["اختر...", "WebBeds", "Extranet (جميع الشركات الأخرى)", "Almosafer"],
    help="حدد ما إذا كنت تعمل مع WebBeds أو شركات Extranet الأخرى أو Almosafer"
)

if operation_type == "اختر...":
    st.warning("⚠️ الرجاء اختيار نوع العملية أولاً لبدء المعالجة")
    st.stop()

st.markdown("---")

# دوال مساعدة
def load_excel(file, sheet_name=0):
    """قراءة ملف Excel/CSV بطرق متعددة"""
    file.seek(0)
    
    # محاولة قراءة حسب الامتداء أولاً
    try:
        if file.name.lower().endswith('.csv'):
            return pd.read_csv(file, encoding='utf-8-sig')
    except:
        file.seek(0)
    
    # محاولة XLSX
    try:
        file.seek(0)
        return pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
    except:
        pass
    
    # محاولة XLS
    try:
        file.seek(0)
        return pd.read_excel(file, sheet_name=sheet_name, engine='xlrd')
    except:
        pass
    
    # محاولة CSV مع encodings مختلفة
    try:
        file.seek(0)
        return pd.read_csv(file, encoding='utf-8')
    except:
        pass
    
    try:
        file.seek(0)
        return pd.read_csv(file)
    except:
        return None

def extract_booking_number(webbeds_booking):
    if pd.isna(webbeds_booking):
        return ""
    booking_str = str(webbeds_booking)
    number = re.sub(r'HTL-WBD-', '', booking_str)
    return number.strip()

def is_valid_supplier_reference(ref):
    if pd.isna(ref) or ref == "" or str(ref).strip() == "":
        return False
    try:
        float(str(ref))
        return True
    except:
        return False

def is_valid_hotel_conf(val):
    """فلترة HotelConf - استبعاد sent والقيم الفارغة"""
    if pd.isna(val) or val == "" or str(val).strip() == "":
        return False
    val_str = str(val).strip().lower()
    if 'sent' in val_str:
        return False
    return True

def export_excel(dict_of_dfs):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dict_of_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

if operation_type == "WebBeds":
    # WebBeds Logic
    st.markdown("""
        <div class="section-header">
            <h2>📋 أتمتة حجوزات WebBeds</h2>
            <p>تحميل ملفات WebBeds وجود والمقارنة بينهما لاستخراج المراجع الناقصة</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**📁 رفع الملفات المطلوبة:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1️⃣ ملف جود (Jood Arrivals)")
        st.markdown("""
        - يحتوي على **ClientReference** و **HotelConf**
        - صيغة: CSV
        - يتضمن جميع الحجوزات في النظام
        """)
        jood_file = st.file_uploader(
            "اختر ملف جود", 
            type=['xlsx', 'xls', 'csv'], 
            key="jood_wb",
            help="ملف CSV يحتوي على بيانات الوصول في جود"
        )
    
    with col2:
        st.markdown("### 2️⃣ ملف WebBeds")
        st.markdown("""
        - يحتوي على **WebBeds Booking Number** و **Supplier reference**
        - صيغة: XLSX/CSV
        - بيانات الحجوزات من WebBeds
        """)
        webbeds_file = st.file_uploader(
            "اختر ملف WebBeds", 
            type=['xlsx', 'xls', 'csv'], 
            key="webbeds_file",
            help="ملف يحتوي على بيانات حجوزات WebBeds"
        )
    
    st.markdown("---")
    
    if jood_file and webbeds_file:
        if st.button("🔍 بدء المقارنة والتحليل", key="wb_process", use_container_width=True):
            with st.spinner("⏳ جاري المقارنة والتحليل الذكي..."):
                try:
                    jood_df = load_excel(jood_file)
                    webbeds_df = load_excel(webbeds_file)
                    
                    # التحقق من أن النتائج DataFrames وليست None أو dictionaries
                    if jood_df is not None and webbeds_df is not None:
                        # تأكد من أنهما DataFrames
                        if not isinstance(jood_df, pd.DataFrame):
                            st.error("❌ خطأ في قراءة ملف جود")
                            jood_df = None
                        if not isinstance(webbeds_df, pd.DataFrame):
                            st.error("❌ خطأ في قراءة ملف WebBeds")
                            webbeds_df = None
                    
                    if jood_df is None or webbeds_df is None:
                        st.error("❌ فشل تحميل أحد الملفات - تأكد من الصيغة والمحتوى")
                        st.stop()
                    
                    if jood_df is not None and webbeds_df is not None:
                        # التحقق من الأعمدة المطلوبة
                        required_webbeds = ['WebBeds Booking Number', 'Supplier reference']
                        required_jood = ['ClientReference', 'HotelConf']
                        
                        missing_wb = [col for col in required_webbeds if col not in webbeds_df.columns]
                        missing_jood = [col for col in required_jood if col not in jood_df.columns]
                        
                        if missing_wb:
                            st.error(f"❌ أعمدة مفقودة في ملف WebBeds: {', '.join(missing_wb)}")
                            st.info(f"📋 الأعمدة الموجودة: {', '.join(webbeds_df.columns.tolist())}")
                        elif missing_jood:
                            st.error(f"❌ أعمدة مفقودة في ملف جود: {', '.join(missing_jood)}")
                            st.info(f"📋 الأعمدة الموجودة: {', '.join(jood_df.columns.tolist())}")
                        else:
                            # استخراج أرقام الحجز
                            webbeds_df = webbeds_df.copy()
                            webbeds_df['BookingNumber'] = webbeds_df['WebBeds Booking Number'].apply(extract_booking_number)
                            
                            # تحويل ClientReference إلى نص
                            jood_df = jood_df.copy()
                            jood_df['Client_ref_clean'] = jood_df['ClientReference'].astype(str)
                            
                            results = []
                            automation_data = []
                            
                            for idx, wb_row in webbeds_df.iterrows():
                                booking_number = wb_row['BookingNumber']
                                supplier_ref = wb_row['Supplier reference']
                                
                                # البحث عن جميع المطابقات في ملف جود (قد يكون هناك تكرار)
                                jood_matches = jood_df[jood_df['Client_ref_clean'] == booking_number]
                                
                                if not jood_matches.empty:
                                    # التحقق من حالة Supplier Reference
                                    needs_reference = not is_valid_supplier_reference(supplier_ref)
                                    
                                    # إذا كان هناك أكثر من مطابقة واحدة
                                    if len(jood_matches) > 1:
                                        # جمع جميع HotelConf في نص واحد
                                        hotel_confs = jood_matches['HotelConf'].tolist()
                                        hotel_confs_str = ' | '.join([str(hc) for hc in hotel_confs])
                                        
                                        result = {
                                            'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                                            'Booking_Number': booking_number,
                                            'Current_Supplier_Reference': supplier_ref,
                                            'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                                            'Jood_Match': f'موجود ({len(jood_matches)} مرات)',
                                            'HotelConf': hotel_confs_str,
                                            'Action_Needed': 'يحتاج إضافة مرجع (متعدد)' if needs_reference else 'موجود بالفعل (متعدد)',
                                            'Status': 'يحتاج إجراء' if needs_reference else 'مكتمل'
                                        }
                                        
                                        # إضافة كل HotelConf للأتمتة إذا كان يحتاج مرجع
                                        if needs_reference:
                                            for _, jood_row in jood_matches.iterrows():
                                                hotel_conf = jood_row['HotelConf']
                                                if is_valid_hotel_conf(hotel_conf):
                                                    automation_data.append({
                                                        'ClientReference': booking_number,
                                                        'HotelConf': hotel_conf
                                                    })
                                    else:
                                        # مطابقة واحدة فقط
                                        jood_row = jood_matches.iloc[0]
                                        htel_rsv = jood_row['HotelConf']
                                        
                                        result = {
                                            'WebBeds_Booking_Number': wb_row['WebBeds Booking Number'],
                                            'Booking_Number': booking_number,
                                            'Current_Supplier_Reference': supplier_ref,
                                            'Supplier_Reference_Valid': is_valid_supplier_reference(supplier_ref),
                                            'Jood_Match': 'موجود',
                                            'HotelConf': htel_rsv,
                                            'Action_Needed': 'يحتاج إضافة مرجع' if needs_reference else 'موجود بالفعل',
                                            'Status': 'يحتاج إجراء' if needs_reference else 'مكتمل'
                                        }
                                        
                                        # إضافة للأتمتة إذا كان يحتاج مرجع
                                        if needs_reference and is_valid_hotel_conf(htel_rsv):
                                            automation_data.append({
                                                'ClientReference': booking_number,
                                                'HotelConf': htel_rsv
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
                            
                            comparison_results = pd.DataFrame(results)
                            automation_df = pd.DataFrame(automation_data)
                            
                            # عرض النتائج
                            st.success("✅ تمت المقارنة بنجاح! تحقق من الإحصائيات أدناه")
                            
                            # إحصائيات
                            st.markdown("""
                                <div class="section-header">
                                    <h3>📊 إحصائيات النتائج</h3>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric("🎯 إجمالي الحجوزات", len(comparison_results))
                            with col2:
                                matched = len(comparison_results[comparison_results['Jood_Match'].str.contains('موجود')])
                                st.metric("✅ موجود في جود", matched)
                            with col3:
                                multiple_matches = len(comparison_results[comparison_results['Jood_Match'].str.contains('مرات')])
                                st.metric("📌 حجوزات متعددة", multiple_matches)
                            with col4:
                                need_action = len(comparison_results[comparison_results['Status'] == 'يحتاج إجراء'])
                                st.metric("⚠️ يحتاج إضافة مرجع", need_action)
                            with col5:
                                completed = len(comparison_results[comparison_results['Status'] == 'مكتمل'])
                                st.metric("✨ مكتمل", completed)
                            
                            st.markdown("**📋 جدول النتائج المفصل:**")
                            st.dataframe(comparison_results, use_container_width=True)
                            
                            # تحميل النتائج
                            st.markdown("---")
                            st.markdown("**📥 تحميل النتائج:**")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                comparison_excel = export_excel({
                                    'comparison_results': comparison_results,
                                    'need_action': comparison_results[comparison_results['Status'] == 'يحتاج إجراء'],
                                    'completed': comparison_results[comparison_results['Status'] == 'مكتمل']
                                })
                                
                                st.download_button(
                                    label="📊 تحميل نتائج المقارنة (XLSX)",
                                    data=comparison_excel,
                                    file_name="webbeds_comparison_results.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                            
                            with col2:
                                if len(automation_df) > 0:
                                    csv_data = automation_df.to_csv(index=False, encoding='utf-8-sig')
                                    st.download_button(
                                        label="🤖 تحميل ملف الأتمتة (CSV)",
                                        data=csv_data,
                                        file_name="webbeds_automation_data.csv",
                                        mime="text/csv",
                                        use_container_width=True
                                    )
                                    
                                    # عرض معاينة ملف الأتمتة
                                    st.markdown("---")
                                    st.markdown("""
                                        <div class="section-header">
                                            <h3>🤖 معاينة ملف الأتمتة</h3>
                                            <p>هذا الملف يحتوي على جميع الحجوزات التي تحتاج إضافة مراجع</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # إحصائيات ملف الأتمتة
                                    unique_bookings_auto = automation_df['ClientReference'].nunique()
                                    total_refs_auto = len(automation_df)
                                    
                                    col_auto1, col_auto2 = st.columns(2)
                                    with col_auto1:
                                        st.metric("🎯 حجوزات فريدة", unique_bookings_auto)
                                    with col_auto2:
                                        st.metric("📌 إجمالي المراجع المراد إضافتها", total_refs_auto)
                                    
                                    st.info("💡 **ملاحظة:** إذا كان عدد المراجع > عدد الحجوزات، فهذا يعني وجود حجوزات متعددة المراجع بنفس الوقت")
                                    
                                    st.dataframe(automation_df.head(10), use_container_width=True)
                                    
                                    if len(automation_df) > 10:
                                        st.info(f"... و {len(automation_df) - 10} سجل إضافي")
                                else:
                                    st.success("✨ ممتاز! لا توجد حجوزات تحتاج إلى أتمتة - جميع المراجع موجودة بالفعل")
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء المقارنة:\n\n{str(e)}")
                    st.info("💡 **نصائح:**\n" +
                           "1. تأكد من أن الملفات بصيغة Excel/CSV صحيحة\n" +
                           "2. تأكد من أسماء الأعمدة الموجودة\n" +
                           "3. جرّب تحميل الملف مجدداً")
    else:
        st.info("📤 الرجاء تحميل كلا الملفين (جود و WebBeds) لبدء المقارنة")

elif operation_type == "Extranet (جميع الشركات الأخرى)":
    # Extranet Companies Logic
    st.markdown("""
        <div class="section-header">
            <h2>🏢 أتمتة الشركات - Extranet</h2>
            <p>مقارنة بيانات الشركات مع جود واستخراج المراجع الناقصة</p>
        </div>
    """, unsafe_allow_html=True)
    
    company_name = st.text_input(
        "📍 أدخل اسم الشركة:",
        placeholder="مثال: Almatar, EET Global, Traveasy, TDS, GTE, العطايا, Safa",
        help="أدخل اسم الشركة التي تريد معالجتها"
    )
    
    if not company_name:
        st.warning("⚠️ يرجى إدخال اسم الشركة أولاً")
        st.stop()
    
    st.markdown(f"### 🔄 معالجة الشركة: **{company_name}**")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        ### 1️⃣ ملف {company_name}
        
        - يحتوي على **Booking code** و **External reference**
        - صيغة: XLSX/CSV
        - ملف التصدير من نظام {company_name}
        """)
        file_company = st.file_uploader(
            f"اختر ملف {company_name}",
            type=['xlsx', 'xls', 'csv'],
            key="file_company",
            help=f"ملف يحتوي على بيانات الحجوزات من {company_name} (XLSX, XLS, CSV)"
        )
    
    with col2:
        st.markdown("""
        ### 2️⃣ ملف جود (Jood Arrivals)
        
        - يحتوي على **ClientReference** و **HotelConf**
        - صيغة: CSV
        - بيانات الوصول في نظام جود
        """)
        file_jood = st.file_uploader(
            "اختر ملف جود",
            type=['csv'],
            key="file_jood",
            help="ملف CSV من نظام جود"
        )
    
    st.markdown("---")
    
    if file_company and file_jood:
        if st.button("🚀 بدء المقارنة والتحليل", use_container_width=True):
            with st.spinner(f"⏳ جاري مقارنة {company_name} مع جود..."):
                try:
                    # قراءة ملف الشركة (مع حذف أول سطرين)
                    df_company = None
                    df_jood = None
                    
                    try:
                        if file_company.name.endswith('.csv'):
                            df_company = pd.read_csv(file_company, skiprows=2, encoding='utf-8-sig')
                        elif file_company.name.endswith('.xlsx'):
                            result = pd.read_excel(file_company, skiprows=2, engine='openpyxl')
                            if isinstance(result, dict):
                                df_company = result[list(result.keys())[0]]
                            else:
                                df_company = result
                        elif file_company.name.endswith('.xls'):
                            result = pd.read_excel(file_company, skiprows=2, engine='xlrd')
                            if isinstance(result, dict):
                                df_company = result[list(result.keys())[0]]
                            else:
                                df_company = result
                        else:
                            # محاولة افتراضية
                            df_company = load_excel(file_company)
                    except Exception as e:
                        # إذا فشلت الطريقة الأولى، محاولة التعامل مع الملف بذكاء
                        file_company.seek(0)
                        content = file_company.read()
                        file_company.seek(0)
                        
                        if content.startswith(b'PK'):  # XLSX
                            result = pd.read_excel(file_company, skiprows=2, engine='openpyxl')
                            if isinstance(result, dict):
                                df_company = result[list(result.keys())[0]]
                            else:
                                df_company = result
                        elif content.startswith(b'\xd0\xcf'):  # XLS
                            result = pd.read_excel(file_company, skiprows=2, engine='xlrd')
                            if isinstance(result, dict):
                                df_company = result[list(result.keys())[0]]
                            else:
                                df_company = result
                        else:
                            df_company = pd.read_csv(file_company, skiprows=2, encoding='utf-8-sig')

                    # قراءة ملف جود
                    try:
                        df_jood = pd.read_csv(file_jood, encoding='utf-8-sig')
                    except:
                        file_jood.seek(0)
                        df_jood = pd.read_csv(file_jood)
                    
                    # التحقق من النتائج
                    if df_company is None or not isinstance(df_company, pd.DataFrame):
                        st.error("❌ خطأ في قراءة ملف الشركة")
                        st.stop()
                    if df_jood is None or not isinstance(df_jood, pd.DataFrame):
                        st.error("❌ خطأ في قراءة ملف جود")
                        st.stop()

                    # تنظيف أسماء الأعمدة
                    df_company.columns = df_company.columns.str.strip()
                    df_jood.columns = df_jood.columns.str.strip()

                    # تحديد الأعمدة
                    col_booking_code = 'Booking code' 
                    col_ext_ref = 'External reference (from the property)' 
                    col_client_ref = 'ClientReference' 
                    col_hotel_conf = 'HotelConf' 

                    # التأكد من نوع البيانات (String)
                    df_company[col_booking_code] = df_company[col_booking_code].astype(str).str.strip()
                    df_jood[col_client_ref] = df_jood[col_client_ref].astype(str).str.strip()

                    # تنظيف قيم HCN
                    df_company[col_ext_ref] = df_company[col_ext_ref].fillna('').astype(str).str.strip()
                    df_company[col_ext_ref] = df_company[col_ext_ref].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)

                    df_jood[col_hotel_conf] = df_jood[col_hotel_conf].fillna('').astype(str).str.strip()
                    df_jood[col_hotel_conf] = df_jood[col_hotel_conf].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)

                    # دالة الفلترة (استبعاد sent)
                    def is_valid_conf(val):
                        if val == '' or val.lower() == 'nan':
                            return False
                        if 'sent' in val.lower():
                            return False
                        return True

                    # تجميع بيانات جود (مع التعامل مع التكرار)
                    jood_agg = df_jood.groupby(col_client_ref)[col_hotel_conf].apply(
                        lambda x: list(set([i for i in x if is_valid_conf(i)]))
                    ).reset_index()
                    jood_agg.rename(columns={col_hotel_conf: 'Jood_Confs_List'}, inplace=True)

                    # دمج الملفين
                    merged_df = pd.merge(df_company, jood_agg, left_on=col_booking_code, right_on=col_client_ref, how='left')

                    # استخراج النواقص
                    missing_data = []

                    for index, row in merged_df.iterrows():
                        booking_code = row[col_booking_code]
                        company_val_raw = row[col_ext_ref]
                        
                        # القيم الحالية في الشركة
                        company_vals_set = set([x for x in re.split(r'[-,\s]+', company_val_raw) if x])
                        
                        # القيم الموجودة في جود
                        jood_vals_list = row['Jood_Confs_List']
                        
                        if isinstance(jood_vals_list, list) and len(jood_vals_list) > 0:
                            jood_vals_set = set(jood_vals_list)
                            # الفرق: موجود في جود وغير موجود في الشركة
                            missing_in_company = jood_vals_set - company_vals_set
                            
                            if len(missing_in_company) > 0:
                                # دمج جميع المراجع الناقصة بـ " - "
                                missing_confs_str = ' - '.join(sorted(missing_in_company))
                                missing_data.append({
                                    f'Booking Code ({company_name})': booking_code,
                                    'HotelConf(jood)': missing_confs_str
                                })

                    # عرض النتائج وتحميل الملف
                    if missing_data:
                        result_df = pd.DataFrame(missing_data)
                        
                        # إحصائيات
                        unique_bookings = result_df[f'Booking Code ({company_name})'].nunique()
                        total_missing_confs = len(result_df)
                        
                        st.success(f"✅ تمت المقارنة بنجاح! تم العثور على {total_missing_confs} مرجع ناقص")
                        
                        # عرض إحصائيات مفصلة
                        st.markdown("""
                            <div class="section-header">
                                <h3>📊 إحصائيات المقارنة</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("🎯 إجمالي الحجوزات في الملف", len(df_company))
                        with col2:
                            st.metric("⚠️ حجوزات تحتاج تحديث", unique_bookings)
                        with col3:
                            st.metric("📌 إجمالي المراجع الناقصة", total_missing_confs)
                        
                        st.markdown("**📋 جدول المراجع الناقصة:**")
                        st.dataframe(result_df, use_container_width=True)

                        csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                        
                        st.markdown("---")
                        st.download_button(
                            label="📥 تحميل ملف النتائج (CSV)",
                            data=csv,
                            file_name=f'{company_name.lower()}_missing_hotel_confs.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                    else:
                        st.balloons()
                        st.success(f"""
                        ### ✨ ممتاز!
                        
                        لا توجد أرقام مراجع ناقصة في **{company_name}**
                        
                        جميع حجوزات {company_name} لديها المراجع الموجودة في جود ✅
                        """)

                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء المعالجة:\n\n{str(e)}")
                    st.info("💡 **نصائح للمساعدة:**\n" +
                           "1. تأكد من أن الملف ليس تالفاً أو معطوباً\n" +
                           "2. تأكد من امتداء الملف صحيح (.xlsx, .xls, .csv)\n" +
                           "3. تأكد من حذف أول سطرين من ملف الشركة إذا كانا عناوين\n" +
                           "4. جرّب تحويل الملف إلى CSV وحاول مرة أخرى")
    else:
        st.info("📤 الرجاء تحميل كلا الملفين (ملف الشركة وملف جود) لبدء المقارنة")

elif operation_type == "Almosafer":
    # Almosafer Logic
    st.markdown("""
        <div class="section-header">
            <h2>✈️ أتمتة حجوزات Almosafer</h2>
            <p>مقارنة بيانات المسافر مع جود واستخراج المراجع الناقصة</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**📁 رفع الملفات المطلوبة:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 1️⃣ ملف Almosafer
        
        - يحتوي على **Booking Ref.** و **confirmationNumber**
        - صيغة: CSV
        - ملف التصدير من نظام Almosafer
        """)
        file_almosafer = st.file_uploader(
            "اختر ملف Almosafer",
            type=['csv', 'xlsx', 'xls'],
            key="file_almosafer",
            help="ملف يحتوي على بيانات الحجوزات من Almosafer"
        )
    
    with col2:
        st.markdown("""
        ### 2️⃣ ملف جود (Jood Arrivals)
        
        - يحتوي على **ClientReference** و **HotelConf**
        - صيغة: CSV
        - بيانات الوصول في نظام جود
        """)
        file_jood_almosafer = st.file_uploader(
            "اختر ملف جود",
            type=['csv'],
            key="file_jood_almosafer",
            help="ملف CSV من نظام جود"
        )
    
    st.markdown("---")
    
    if file_almosafer and file_jood_almosafer:
        if st.button("🚀 بدء المقارنة والتحليل", key="almosafer_process", use_container_width=True):
            with st.spinner("⏳ جاري مقارنة Almosafer مع جود..."):
                try:
                    # قراءة ملف Almosafer
                    df_almosafer = None
                    df_jood = None
                    
                    try:
                        if file_almosafer.name.endswith('.csv'):
                            df_almosafer = pd.read_csv(file_almosafer, encoding='utf-8-sig')
                        elif file_almosafer.name.endswith('.xlsx'):
                            result = pd.read_excel(file_almosafer, engine='openpyxl')
                            if isinstance(result, dict):
                                df_almosafer = result[list(result.keys())[0]]
                            else:
                                df_almosafer = result
                        elif file_almosafer.name.endswith('.xls'):
                            result = pd.read_excel(file_almosafer, engine='xlrd')
                            if isinstance(result, dict):
                                df_almosafer = result[list(result.keys())[0]]
                            else:
                                df_almosafer = result
                    except Exception as e:
                        file_almosafer.seek(0)
                        df_almosafer = pd.read_csv(file_almosafer, encoding='utf-8-sig')
                    
                    # قراءة ملف جود
                    try:
                        df_jood = pd.read_csv(file_jood_almosafer, encoding='utf-8-sig')
                    except:
                        file_jood_almosafer.seek(0)
                        df_jood = pd.read_csv(file_jood_almosafer)
                    
                    # التحقق من النتائج
                    if df_almosafer is None or not isinstance(df_almosafer, pd.DataFrame):
                        st.error("❌ خطأ في قراءة ملف Almosafer")
                        st.stop()
                    if df_jood is None or not isinstance(df_jood, pd.DataFrame):
                        st.error("❌ خطأ في قراءة ملف جود")
                        st.stop()
                    
                    # تنظيف أسماء الأعمدة
                    df_almosafer.columns = df_almosafer.columns.str.strip()
                    df_jood.columns = df_jood.columns.str.strip()
                    
                    # التحقق من الأعمدة المطلوبة
                    col_booking_ref = 'Booking Ref.'
                    col_confirmation = 'confirmationNumber'
                    col_client_ref = 'ClientReference'
                    col_hotel_conf = 'HotelConf'
                    
                    # التحقق من وجود الأعمدة
                    missing_almosafer = []
                    missing_jood = []
                    
                    if col_booking_ref not in df_almosafer.columns:
                        missing_almosafer.append(col_booking_ref)
                    if col_confirmation not in df_almosafer.columns:
                        missing_almosafer.append(col_confirmation)
                    if col_client_ref not in df_jood.columns:
                        missing_jood.append(col_client_ref)
                    if col_hotel_conf not in df_jood.columns:
                        missing_jood.append(col_hotel_conf)
                    
                    if missing_almosafer:
                        st.error(f"❌ أعمدة مفقودة في ملف Almosafer: {', '.join(missing_almosafer)}")
                        st.info(f"📋 الأعمدة الموجودة: {', '.join(df_almosafer.columns.tolist())}")
                        st.stop()
                    
                    if missing_jood:
                        st.error(f"❌ أعمدة مفقودة في ملف جود: {', '.join(missing_jood)}")
                        st.info(f"📋 الأعمدة الموجودة: {', '.join(df_jood.columns.tolist())}")
                        st.stop()
                    
                    # تنظيف البيانات
                    df_almosafer[col_booking_ref] = df_almosafer[col_booking_ref].astype(str).str.strip()
                    df_almosafer[col_confirmation] = df_almosafer[col_confirmation].fillna('').astype(str).str.strip()
                    df_almosafer[col_confirmation] = df_almosafer[col_confirmation].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)
                    
                    df_jood[col_client_ref] = df_jood[col_client_ref].astype(str).str.strip()
                    df_jood[col_hotel_conf] = df_jood[col_hotel_conf].fillna('').astype(str).str.strip()
                    df_jood[col_hotel_conf] = df_jood[col_hotel_conf].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)
                    
                    # دالة الفلترة (استبعاد sent)
                    def is_valid_conf(val):
                        if val == '' or val.lower() == 'nan':
                            return False
                        if 'sent' in val.lower():
                            return False
                        return True
                    
                    # تجميع بيانات جود (مع التعامل مع التكرار)
                    jood_agg = df_jood.groupby(col_client_ref)[col_hotel_conf].apply(
                        lambda x: list(set([i for i in x if is_valid_conf(i)]))
                    ).reset_index()
                    jood_agg.rename(columns={col_hotel_conf: 'Jood_Confs_List'}, inplace=True)
                    
                    # دمج الملفين
                    merged_df = pd.merge(df_almosafer, jood_agg, left_on=col_booking_ref, right_on=col_client_ref, how='left')
                    
                    # استخراج النواقص - إذا كان HotelConf != confirmationNumber أو confirmationNumber فارغ
                    missing_data = []
                    comparison_results = []
                    
                    for index, row in merged_df.iterrows():
                        booking_ref = row[col_booking_ref]
                        almosafer_conf = row[col_confirmation]
                        
                        # القيم الموجودة في جود
                        jood_vals_list = row['Jood_Confs_List']
                        
                        if isinstance(jood_vals_list, list) and len(jood_vals_list) > 0:
                            jood_vals_set = set(jood_vals_list)
                            
                            # التحقق إذا كان confirmationNumber موجود أو مطابق
                            if almosafer_conf == '' or almosafer_conf == 'nan' or almosafer_conf not in jood_vals_set:
                                # يحتاج إضافة - نأخذ أول HotelConf من جود
                                for hotel_conf in jood_vals_list:
                                    if hotel_conf != almosafer_conf:  # فقط إذا لم يكن مطابق
                                        missing_data.append({
                                            'Booking Ref.': booking_ref,
                                            'HotelConf': hotel_conf
                                        })
                                
                                comparison_results.append({
                                    'Booking_Ref': booking_ref,
                                    'Almosafer_confirmationNumber': almosafer_conf if almosafer_conf else 'فارغ',
                                    'Jood_HotelConf': ' | '.join(jood_vals_list),
                                    'Status': 'يحتاج إجراء',
                                    'Reason': 'HCN غير مطابق أو فارغ'
                                })
                            else:
                                comparison_results.append({
                                    'Booking_Ref': booking_ref,
                                    'Almosafer_confirmationNumber': almosafer_conf,
                                    'Jood_HotelConf': ' | '.join(jood_vals_list),
                                    'Status': 'مكتمل',
                                    'Reason': 'HCN مطابق'
                                })
                        else:
                            comparison_results.append({
                                'Booking_Ref': booking_ref,
                                'Almosafer_confirmationNumber': almosafer_conf if almosafer_conf else 'فارغ',
                                'Jood_HotelConf': 'غير موجود في جود',
                                'Status': 'غير موجود',
                                'Reason': 'لا يوجد في جود'
                            })
                    
                    # عرض النتائج
                    if missing_data:
                        result_df = pd.DataFrame(missing_data)
                        comparison_df = pd.DataFrame(comparison_results)
                        
                        # إحصائيات
                        unique_bookings = result_df['Booking Ref.'].nunique()
                        total_missing_confs = len(result_df)
                        total_complete = len([r for r in comparison_results if r['Status'] == 'مكتمل'])
                        total_need_action = len([r for r in comparison_results if r['Status'] == 'يحتاج إجراء'])
                        
                        st.success(f"✅ تمت المقارنة بنجاح! تم العثور على {total_missing_confs} مرجع ناقص")
                        
                        # عرض إحصائيات مفصلة
                        st.markdown("""
                            <div class="section-header">
                                <h3>📊 إحصائيات المقارنة</h3>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("🎯 إجمالي الحجوزات", len(df_almosafer))
                        with col2:
                            st.metric("✅ مكتمل", total_complete)
                        with col3:
                            st.metric("⚠️ يحتاج تحديث", total_need_action)
                        with col4:
                            st.metric("📌 إجمالي المراجع", total_missing_confs)
                        
                        st.markdown("**📋 جدول المقارنة:**")
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        st.markdown("**📋 جدول المراجع الناقصة (للأتمتة):**")
                        st.dataframe(result_df, use_container_width=True)
                        
                        csv = result_df.to_csv(index=False, encoding='utf-8-sig')
                        
                        st.markdown("---")
                        st.download_button(
                            label="📥 تحميل ملف الأتمتة (CSV)",
                            data=csv,
                            file_name='almosafer_automation_data.csv',
                            mime='text/csv',
                            use_container_width=True
                        )
                    else:
                        st.balloons()
                        st.success("""
                        ### ✨ ممتاز!
                        
                        لا توجد أرقام مراجع ناقصة في **Almosafer**
                        
                        جميع حجوزات Almosafer لديها المراجع الموجودة في جود ✅
                        """)
                        
                        # عرض جدول المقارنة على أي حال
                        if comparison_results:
                            comparison_df = pd.DataFrame(comparison_results)
                            st.markdown("**📋 جدول المقارنة:**")
                            st.dataframe(comparison_df, use_container_width=True)
                
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء المعالجة:\n\n{str(e)}")
                    st.info("💡 **نصائح للمساعدة:**\n" +
                           "1. تأكد من أن الملف ليس تالفاً أو معطوباً\n" +
                           "2. تأكد من امتداء الملف صحيح (.csv, .xlsx, .xls)\n" +
                           "3. تأكد من وجود الأعمدة: Booking Ref. و confirmationNumber في ملف Almosafer\n" +
                           "4. تأكد من وجود الأعمدة: ClientReference و HotelConf في ملف جود")
    else:
        st.info("📤 الرجاء تحميل كلا الملفين (ملف Almosafer وملف جود) لبدء المقارنة")

# قسم معلومات الشركات والروابط
st.markdown("---")
st.markdown("""
    <div class="section-header">
        <h3>🔗 روابط الشركات المدعومة</h3>
        <p>اضغط على اسم الشركة للدخول إلى نظام Extranet الخاص بها</p>
    </div>
""", unsafe_allow_html=True)

companies_links = [
    ("🌍 EET Global", "https://www.eetglobal.com/extranet"),
    ("🏨 العطايا", "https://www.alatayadmc.com/extranet"),
    ("✈️ Safa Travel", "https://www.safa-travel.net/Extranet/alojamiento/listadoReservas.aspx?alojamiento=1496&idcco=2515&verVigente=1"),
]

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]

for idx, (company, url) in enumerate(companies_links):
    with cols[idx % 3]:
        st.markdown(f'<a href="{url}" target="_blank"><button style="width:100%; padding:12px; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">{company}</button></a>', unsafe_allow_html=True)
