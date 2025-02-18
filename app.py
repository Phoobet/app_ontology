import streamlit as st
from rdflib import Graph, Namespace
from fuzzywuzzy import process

def main():
    st.set_page_config(page_title="ข้อมูลจังหวัดท่องเที่ยว", layout="centered")

    # เพิ่ม CSS ปรับแต่ง UI
    st.markdown("""
    <style>
        .title {
            font-size: 2.5em;
            color: #2C3E50;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5em;
        }
        .search-box {
            text-align: center;
            margin-bottom: 1em;
        }
        .divider {
            height: 3px;
            background-color: #2980B9;
            margin: 1.5em 0;
        }
        .card {
            background-color:rgb(160, 221, 236);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 1em;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .card-header {
            font-size: 1.3em;
            font-weight: bold;
            color: #2980B9;
        }
        .card-body {
            font-size: 1.1em;
            margin-bottom: 0.5em;
            color: #2C3E50;
        }
        .error-message {
            color: #E74C3C;
            font-size: 1.2em;
            font-weight: bold;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="title">ค้นหาข้อมูลจังหวัดท่องเที่ยว</div>', unsafe_allow_html=True)

    # ตัวเลือกภาษา
    display_lang = st.radio("เลือกภาษา", ["ภาษาไทย", "English"], horizontal=True)
    lang_code = "th" if display_lang == "ภาษาไทย" else "en"

    # โหลด OWL
    owl_file = "mytourism.owl"
    g = Graph()
    g.parse(owl_file)

    MYT = Namespace("http://www.my_ontology.edu/mytourism#")
    g.bind("myt", MYT)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ดึงรายชื่อทั้งหมดจากฐานข้อมูล
    all_provinces = [str(row.provName) for row in g.query("SELECT DISTINCT ?provName WHERE { ?prov a myt:ThaiProvince . ?prov myt:hasNameOfProvince ?provName . }")]

    # ใช้ fuzzywuzzy เพื่อให้ตัวเลือกใกล้เคียงแสดงให้ผู้ใช้
    search_value = st.selectbox("🔍 เลือกจังหวัด, ชื่อท้องถิ่น, ต้นไม้ หรือ ดอกไม้", options=[""] + all_provinces)

    if search_value:
        # คิวรีข้อมูลจังหวัด
        query_info = f"""
        SELECT DISTINCT ?provName ?tradName ?tree ?flower ?motto ?seal ?lat ?long
        WHERE {{
            ?prov a myt:ThaiProvince .
            {{
                ?prov myt:hasNameOfProvince ?x .
                FILTER(str(?x) = "{search_value}")
            }} UNION {{
                ?prov myt:hasTraditionalNameOfProvince ?x .
                FILTER(str(?x) = "{search_value}")
            }} UNION {{
                ?prov myt:hasTree ?x .
                FILTER(str(?x) = "{search_value}")
            }} UNION {{
                ?prov myt:hasFlower ?x .
                FILTER(str(?x) = "{search_value}")
            }}
            OPTIONAL {{ ?prov myt:hasNameOfProvince ?provName . FILTER(lang(?provName) = "{lang_code}") }}
            OPTIONAL {{ ?prov myt:hasTraditionalNameOfProvince ?tradName . FILTER(lang(?tradName) = "{lang_code}") }}
            OPTIONAL {{ ?prov myt:hasTree ?tree . FILTER(lang(?tree) = "{lang_code}") }}
            OPTIONAL {{ ?prov myt:hasFlower ?flower . FILTER(lang(?flower) = "{lang_code}") }}
            OPTIONAL {{ ?prov myt:hasMotto ?motto . FILTER(lang(?motto) = "{lang_code}") }}
            OPTIONAL {{ ?prov myt:hasSeal ?seal. }}
            OPTIONAL {{ ?prov myt:hasLatitudeOfProvince ?lat. }}
            OPTIONAL {{ ?prov myt:hasLongitudeOfProvince ?long. }}
        }}
        """
        results_info = g.query(query_info)

        if len(results_info) == 0:
            st.markdown(f'<div class="error-message">❌ ไม่พบข้อมูลที่สอดคล้องกับ: {search_value}</div>', unsafe_allow_html=True)
        else:
            province_data = {
                "จังหวัด / Province": set(),
                "จังหวัดตามประเพณี / Traditional": set(),
                "ต้นไม้ประจำจังหวัด / Tree": set(),
                "ดอกไม้ประจำจังหวัด / Flower": set(),
                "คำขวัญ / Motto": set(),
                "ตราสัญลักษณ์ / Seal": set(),
                "พิกัด (Latitude, Longitude)": set()
            }

            for row in results_info:
                if row.provName:
                    province_data["จังหวัด / Province"].add(row.provName)
                if row.tradName:
                    province_data["จังหวัดตามประเพณี / Traditional"].add(row.tradName)
                if row.tree:
                    province_data["ต้นไม้ประจำจังหวัด / Tree"].add(row.tree)
                if row.flower:
                    province_data["ดอกไม้ประจำจังหวัด / Flower"].add(row.flower)
                if row.motto:
                    province_data["คำขวัญ / Motto"].add(row.motto)
                if row.seal:
                    province_data["ตราสัญลักษณ์ / Seal"].add(row.seal)
                if row.lat and row.long:
                    province_data["พิกัด (Latitude, Longitude)"].add(f"{row.lat}, {row.long}")

            # แสดงผลข้อมูลแบบ Card-style
            for key, value in province_data.items():
                if value:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-header">{key}</div>
                        <div class="card-body">{", ".join(sorted(value))}</div>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ กรุณากรอกข้อมูลที่ต้องการค้นหา")

if __name__ == "__main__":
    main()
