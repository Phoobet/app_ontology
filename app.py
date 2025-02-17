import streamlit as st
from rdflib import Graph, Namespace

def main():
    st.set_page_config(page_title="ข้อมูลจังหวัดท่องเที่ยว", layout="centered")
    
    st.markdown(
        """
        <style>
        .title {
            font-size: 2.5em;
            color: #2C3E50; /* สีเข้ม */
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5em;
        }
        .subtitle {
            font-size: 1.3em;
            color: #34495E; /* สีเทาเข้ม */
            text-align: center;
            margin-bottom: 1em;
        }
        .divider {
            height: 3px;
            background-color: #2980B9;
            margin: 1.5em 0;
        }
        .result-container {
            background-color: #ECF0F1;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 2em;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .result-title {
            font-size: 1.5em;
            font-weight: bold;
            color: #2980B9; /* สีฟ้า */
        }
        .result-value {
            font-size: 1.1em;
            margin-bottom: 1em;
            color: #2980B9; /* สีเข้ม */
        }
        .input-box {
            border-radius: 8px;
            padding: 0.8em;
            border: 1px solid #BDC3C7;
        }
        .search-button {
            background-color: #2980B9;
            color: white;
            border-radius: 8px;
            padding: 0.8em 2em;
            font-weight: bold;
            cursor: pointer;
        }
        .search-button:hover {
            background-color: #1F618D;
        }
        .error-message {
            color: #E74C3C; /* สีแดงสำหรับข้อความผิดพลาด */
            font-size: 1.2em;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="title">ค้นหาข้อมูลจังหวัดท่องเที่ยว</div>', unsafe_allow_html=True)

    # ตัวเลือกภาษา
    language = st.radio(
        "เลือกภาษาสำหรับการแสดงผล",
        ("ภาษาไทย", "English"),
        horizontal=True
    )

    # เปลี่ยนข้อความตามภาษาที่เลือก
    if language == "ภาษาไทย":
        search_placeholder = "ค้นหาข้อมูลจังหวัด, ชื่อท้องถิ่น, ต้นไม้ หรือ ดอกไม้"
        no_result_message = "ไม่พบข้อมูลที่สอดคล้องกับ: "
        result_title = "ผลลัพธ์ที่ค้นพบ:"
        province_name = "ชื่อจังหวัด:"
        local_name = "ชื่อท้องถิ่น:"
        tree = "ต้นไม้ประจำจังหวัด:"
        flower = "ดอกไม้ประจำจังหวัด:"
        motto = "คำขวัญจังหวัด:"
        seal = "ตราสัญลักษณ์:"
        latitude = "Latitude:"
        longitude = "Longitude:"
    else:
        search_placeholder = "Search for province, local name, tree, or flower"
        no_result_message = "No results found for: "
        result_title = "Search Results:"
        province_name = "Province Name:"
        local_name = "Local Name:"
        tree = "Tree of Province:"
        flower = "Flower of Province:"
        motto = "Province Motto:"
        seal = "Seal:"
        latitude = "Latitude:"
        longitude = "Longitude:"

    owl_file = "mytourism.owl"
    g = Graph()
    g.parse(owl_file)

    MYT = Namespace("http://www.my_ontology.edu/mytourism#")
    g.bind("myt", MYT)

    # ดึงข้อมูลจาก Ontology
    query_possible_values = """
    SELECT DISTINCT ?val
    WHERE {
      ?prov a myt:ThaiProvince . 
      {
        ?prov myt:hasNameOfProvince ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasTraditionalNameOfProvince ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasTree ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
      UNION
      {
        ?prov myt:hasFlower ?val .
        FILTER(lang(?val) = "th" || lang(?val) = "en")
      }
    }
    ORDER BY ?val
    """

    results_list = g.query(query_possible_values)
    possible_values = [str(row.val) for row in results_list]

    # เพิ่มฟีเจอร์เลือกจากตัวเลือกที่มี
    selected_value = st.selectbox(
        "เลือกข้อมูลที่คุณต้องการค้นหา",
        options=[""] + possible_values,
        help=search_placeholder
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if selected_value:
        query_info = f"""
        SELECT DISTINCT ?provName ?tradName ?tree ?flower ?motto ?seal ?lat ?long
        WHERE {{
            ?prov a myt:ThaiProvince .
            {{
                ?prov myt:hasNameOfProvince ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasTraditionalNameOfProvince ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasTree ?x .
                FILTER(str(?x) = "{selected_value}")
            }} UNION {{
                ?prov myt:hasFlower ?x .
                FILTER(str(?x) = "{selected_value}")
            }}
            OPTIONAL {{ ?prov myt:hasNameOfProvince ?provName . }}
            OPTIONAL {{ ?prov myt:hasTraditionalNameOfProvince ?tradName . }}
            OPTIONAL {{ ?prov myt:hasTree ?tree . }}
            OPTIONAL {{ ?prov myt:hasFlower ?flower . }}
            OPTIONAL {{ ?prov myt:hasMotto ?motto . }}
            OPTIONAL {{ ?prov myt:hasSeal ?seal. }}
            OPTIONAL {{ ?prov myt:hasLatitudeOfProvince ?lat. }}
            OPTIONAL {{ ?prov myt:hasLongitudeOfProvince ?long. }}
        }}
        """

        results_info = g.query(query_info)

        if len(results_info) == 0:
            st.markdown(f'<div class="error-message">{no_result_message} {selected_value}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-container"><div class="result-title">{result_title}</div>', unsafe_allow_html=True)
            for row in results_info:
                name_out = row.provName if row.provName else "-"
                trad_out = row.tradName if row.tradName else "-"
                tree_out = row.tree if row.tree else "-"
                flower_out = row.flower if row.flower else "-"
                motto_out = row.motto if row.motto else "-"
                seal_out = row.seal if row.seal else "-"
                lat_out = row.lat if row.lat else "-"
                long_out = row.long if row.long else "-"

                st.markdown(
                    f'<div class="result-value"><b>{province_name}</b> {name_out}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(f'<div class="result-value"><b>{local_name}</b> {trad_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{tree}</b> {tree_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{flower}</b> {flower_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{motto}</b> {motto_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{seal}</b> {seal_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{latitude}</b> {lat_out}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="result-value"><b>{longitude}</b> {long_out}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # เพิ่มปุ่มให้ค้นหาด้วย
    if not selected_value:
        st.markdown('<button class="search-button">ค้นหา</button>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
