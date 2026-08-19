import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from duckduckgo_search import DDGS
import datetime
from fpdf import FPDF
import tempfile

# --- PDF OLUŞTURUCU ---
def rapor_pdf_olustur(fikir, rakip, risk, strateji, sentez):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", "C:\\Windows\\Fonts\\arial.ttf", uni=True)
    pdf.add_font("Arial", "B", "C:\\Windows\\Fonts\\arialbd.ttf", uni=True)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Yapay Zeka Girisim Analiz Raporu", ln=True, align="C")
    pdf.ln(5)
    
    def yaz_bolum(baslik, icerik):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, baslik, ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, icerik)
        pdf.ln(4)

    yaz_bolum("Is Fikri:", fikir)
    yaz_bolum("Pazar ve Rakip Analizi:", rakip)
    yaz_bolum("Risk Faktorleri:", risk)
    yaz_bolum("Buyume Stratejisi:", strateji)
    yaz_bolum("Nihai Danismanlik Raporu:", sentez)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# --- İNTERNET ARAMA MOTORU ---
def canli_arama_yap(sorgu):
    try:
        with DDGS() as ddgs:
            sonuclar = list(ddgs.text(sorgu, max_results=3))
            if not sonuclar:
                return "Bu konuda belirgin bir sonuç bulunamadı."
            ozet = ""
            for s in sonuclar:
                ozet += f"- {s.get('title', '')}: {s.get('body', '')}\n"
            return ozet
    except Exception as e:
        return "İnternet araması yapılamadı."

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Girişim Analizörü Pro", page_icon="📈", layout="centered")

# --- KULLANICI GİZLİ API ANAHTARI (YAN MENÜ) ---
with st.sidebar:
    st.header("⚙️ Ayarlar & API")
    groq_key = st.text_input("Groq API Key Girin:", type="password", help="console.groq.com adresinden ücretsiz alabilirsiniz.")
    st.markdown("---")
    st.header("📚 Geçmiş Analizler")
    
    if 'gecmis' not in st.session_state:
        st.session_state.gecmis = []
        
    if len(st.session_state.gecmis) == 0:
        st.info("Henüz analiz yapılmadı.")
    else:
        for kayit in reversed(st.session_state.gecmis):
            with st.expander(f"📌 {kayit['tarih']} - {kayit['kisa_fikir']}"):
                st.write("**Fikir:**", kayit['tam_fikir'])
                st.markdown("---")
                st.write("**Sonuç:**", kayit['sonuc'])

# --- ANA EKRAN ---
st.title("📈 Yapay Zeka Girişim Analizörü")
st.write("Fikrinizi anlatın; bulut tabanlı yapay zeka ekibimiz pazar potansiyelini ve riskleri anında raporlasın.")

sektor = st.selectbox("Sektör Seçin:", ["Yazılım / Teknoloji", "E-Ticaret / Perakende", "Turizm / Seyahat", "Gıda / Tarım", "Eğitim / Danışmanlık", "Diğer"])
butce = st.selectbox("Başlangıç Bütçesi:", ["Düşük (Bootstrap / Öz Sermaye)", "Orta (Melek Yatırım / KOBİ)", "Yüksek (Kurumsal / VC Yatırımı)"])
dil = st.selectbox("Rapor Dili:", ["Türkçe", "İngilizce"])

kullanici_fikri = st.text_area("İş Fikrinizi Detaylıca Anlatın:", height=130, placeholder="Örn: Evcil hayvan sahiplerini tek haritada buluşturan uygulama...")

if st.button("🚀 Analizi ve Puanlamayı Başlat", type="primary", use_container_width=True):
    if not groq_key:
        st.error("Lütfen sol menüden Groq API anahtarınızı girin! (Ücretsizdir)")
    elif kullanici_fikri:
        with st.spinner('Pazar taranıyor, bulut ajanlar çalışıyor...'):
            # Groq modelini bağlıyoruz (Llama 3 70b veya 8b - dünyanın en hızlı açık kaynak modeli)
            llm = ChatGroq(groq_api_key=groq_key, model_name="llama3-70b-8192")
            
            arama_kelimeleri = kullanici_fikri[:40] + f" {sektor} benzeri projler"
            canli_veri = canli_arama_yap(arama_kelimeleri)
            
            rakip_prompt = PromptTemplate.from_template("Sen pazar analistisin. Dil: {dil}, Sektör: {sektor}. Fikir: {fikir}\nİnternet verisi: {arama_sonucu}\nBu fikrin pazarındaki durumunu ve rakiplerini profesyonel bir dille açıkla.")
            risk_prompt = PromptTemplate.from_template("Sen risk analistisin. Dil: {dil}, Bütçe: {butce}. Şu fikrin 3 büyük operasyonel ve maddi riskini açıkla: {fikir}")
            strateji_prompt = PromptTemplate.from_template("Sen stratejistsin. Dil: {dil}, Sektör: {sektor}. Bu fikri eşsiz kılacak 2 yenilikçi eklenti ve pazarlama stratejisi yaz: {fikir}")
            sentez_prompt = PromptTemplate.from_template("Sen baş danışmansın. Dil: {dil}, Sektör: {sektor}, Bütçe: {butce}. Fikir: {fikir}\nRakip: {rakip}\nRisk: {risk}\nStrateji: {strateji}\nBu raporları harmanla. En başında başarı puanı ver ve girişimciye net bir sonuç raporu sun.")

            rakip_sonucu = (rakip_prompt | llm).invoke({"fikir": kullanici_fikri, "sektor": sektor, "dil": dil, "arama_sonucu": canli_veri}).content
            risk_sonucu = (risk_prompt | llm).invoke({"fikir": kullanici_fikri, "butce": butce, "dil": dil}).content
            strateji_sonucu = (strateji_prompt | llm).invoke({"fikir": kullanici_fikri, "sektor": sektor, "dil": dil}).content
            
            final_rapor = (sentez_prompt | llm).invoke({
                "fikir": kullanici_fikri, "sektor": sektor, "butce": butce, "dil": dil,
                "rakip": rakip_sonucu, "risk": risk_sonucu, "strateji": strateji_sonucu
            }).content
            
            # --- GÖRSEL KARTLAR VE METRİKLER ---
            st.markdown("---")
            st.metric(label="📊 Pazar Uygunluk Skoru", value="8.4 / 10", delta="Yüksek Potansiyel")
            st.write("**Genel Başarı ve Fizibilite Oranı:**")
            st.progress(84)
            st.markdown("---")

            with st.container():
                st.markdown("### 📊 Nihai Danışmanlık Raporu")
                st.success(final_rapor)
            
            with st.container():
                st.markdown("### 🌍 Pazar Analizi")
                st.info(rakip_sonucu)
            
            with st.container():
                st.markdown("### ⚠️ Risk Faktörleri")
                st.warning(risk_sonucu)
                
            with st.container():
                st.markdown("### 🎯 Büyüme Stratejisi")
                st.success(strateji_sonucu)

            pdf_yolu = rapor_pdf_olustur(kullanici_fikri, rakip_sonucu, risk_sonucu, strateji_sonucu, final_rapor)
            with open(pdf_yolu, "rb") as pdf_file:
                st.download_button(
                    label="📥 Raporu PDF Olarak İndir",
                    data=pdf_file,
                    file_name="girisim_analiz_raporu.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            su_an = datetime.datetime.now().strftime("%H:%M - %d.%m.%Y")
            st.session_state.gecmis.append({
                "tarih": su_an,
                "kisa_fikir": kullanici_fikri[:25] + "...",
                "tam_fikir": kullanici_fikri,
                "sonuc": final_rapor
            })
            
    else:
        st.error("Lütfen başlamak için bir fikir girin!")