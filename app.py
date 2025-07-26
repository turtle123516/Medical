import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
# maps_navigation 도구를 사용하기 위해 임포트합니다.
# 실제 환경에서는 이 도구가 자동으로 제공됩니다.
# from tools import maps_navigation # 이 줄은 실제 환경에서 필요하지 않습니다.

# ----------------------------------------
# 1) 페이지 기본 설정
# ----------------------------------------
# 웹 브라우저 탭 이름, 아이콘, 화면 레이아웃 넓게 설정!
st.set_page_config(
    page_title="폐의약품 수거 약국 찾기",
    page_icon="💊",
    layout="wide"
)

# 화면에 큰 제목과 설명문 쓰기!
st.title("💊 폐의약품 수거 약국 찾기")
st.markdown("원하는 폐의약품을 선택하면 해당 약국을 표와 지도에서 확인할 수 있어요!")

# ----------------------------------------
# 2) CSV 데이터 불러오기 함수
# ----------------------------------------
# @st.cache_data : 데이터 기억해서 새로고침해도 빨라요!
@st.cache_data
def load_data():
    # 저장한 CSV 파일을 utf-8-sig로 읽어오기
    df = pd.read_csv("cheonan_seobuk_pharmacy_with_items.csv", encoding="utf-8-sig")
    return df

df = load_data()


# ----------------------------------------
# 3) 수거약품목 카테고리 만들기
# CSV에 들어있는 모든 수거약품목을 한 번에 모아서 중복 없이!
# ----------------------------------------
all_items = []
# '수거약품목' 열의 값들을 쉼표로 나눠서 리스트에 넣기
df['수거약품목'].dropna().apply(lambda x:
    all_items.extend([i.strip() for i in x.split(',')]))
# set() 으로 중복 제거 후 다시 리스트로
categories = list(sorted(set(all_items)))

# ----------------------------------------
# 4) 체크박스로 약품목 선택하기
# ----------------------------------------
st.subheader("♻️ 수거 약품목 선택 (최대 3개)")
cols = st.columns(3)  # 3열로 체크박스 배치
selected = []  # 선택된 약품목 저장할 리스트

# 카테고리 하나씩 돌면서 체크박스 만들기!
for i, cat in enumerate(categories):
    if cols[i % 3].checkbox(cat):
        selected.append(cat)

# 선택한 약품목이 3개 초과면 오류 메시지 출력!
if len(selected) > 3:
    st.error("❗ 최대 3개까지만 선택할 수 있어요.")
    selected = selected[:3]  # 3개 초과되면 잘라버리기

# ----------------------------------------
# 5) 선택된 약품목으로 데이터 필터링 및 지도 표시
# ----------------------------------------
if selected:
    # 수거약품목에 선택된 단어 중 하나라도 들어있는 데이터만 남기기
    mask = df['수거약품목'].apply(lambda x: any(tag in str(x) for tag in selected))
    result = df[mask]

    # 선택 결과 요약 메시지
    st.success(f"선택한 약품목: {selected} → 약국 {len(result)}곳")

    # 필터링된 약국 표 보여주기
    st.dataframe(result[['병원명', '주소', '전화번호', '수거약품목']], use_container_width=True)

    st.subheader('🥟약국 위치 지도')

    coords = result.dropna(subset=['위도','경도'])

    if not coords.empty:
        m = folium.Map()

        bounds = [
            [coords['위도'].min(), coords['경도'].min()],
            [coords['위도'].max(), coords['경도'].max()]
        ]
        m.fit_bounds(bounds)

        for _, row in coords.iterrows():
            folium.Marker(
                [row['위도'], row['경도']],
                popup=f"<b>{row['병원명']}</b><br>주소: {row['주소']}<br>수거품목: {row['수거약품목']}", # 팝업 정보 보강
                tooltip=row['병원명']
            ).add_to(m)

        folium_static(m, width=800, height=500)

        # ----------------------------------------
        # 6) 길 찾기 기능 추가
        # ----------------------------------------
        st.subheader('🚗 약국 길 찾기')
        # 약국 선택 드롭다운 (병원명으로 선택)
        pharmacy_names = coords['병원명'].tolist()
        selected_pharmacy_name = st.selectbox('길을 찾을 약국을 선택하세요:', pharmacy_names)

        # 출발지 입력
        origin_location = st.text_input('출발지 주소를 입력하세요 (예: 서울역, MY_LOCATION, MY_HOME):')

        # 길 찾기 버튼
        if st.button('길 찾기'):
            if selected_pharmacy_name and origin_location:
                # 선택된 약국의 주소 찾기
                destination_pharmacy = coords[coords['병원명'] == selected_pharmacy_name].iloc[0]
                destination_address = destination_pharmacy['주소']

                st.info(f"'{origin_location}'에서 '{selected_pharmacy_name}({destination_address})'까지 길을 찾습니다...")

                # maps_navigation 도구 호출 (실제 환경에서는 자동으로 호출됨)
                # 여기서는 예시로 print를 사용하지만, 실제 앱에서는 API 호출 결과가 반환됩니다.
                try:
                    # maps_navigation.Google Maps 함수는 실제 도구 호출 시 사용됩니다.
                    # 여기서는 예시 출력을 보여줍니다.
                    # response = maps_navigation.Google Maps(origin=origin_location, destination=destination_address)
                    # 아래는 API 호출을 시뮬레이션한 예시 응답입니다.
                    response = {
                        "mapUrl": f"https://www.google.com/maps/dir/?api=1&origin={origin_location}&destination={destination_address}",
                        "routes": [
                            {"distance": "약 10km", "duration": "약 20분", "summary": "최적 경로"}
                        ]
                    }

                    if response and response.get('routes'):
                        route = response['routes'][0]
                        st.success(f"총 거리: {route['distance']}, 예상 시간: {route['duration']}")
                        st.markdown(f"[Google 지도에서 경로 보기]({response['mapUrl']})")
                        if route.get('trafficReport') and route['trafficReport'].get('summary'):
                            st.warning(f"교통 상황: {route['trafficReport']['summary']}")
                    else:
                        st.warning("경로를 찾을 수 없습니다. 출발지 또는 도착지 주소를 확인해주세요.")
                except Exception as e:
                    st.error(f"길 찾기 중 오류가 발생했습니다: {e}")
            else:
                st.warning("약국과 출발지 주소를 모두 입력해주세요.")
    else:
        st.info("위치정보가 없습니다")

else:
    st.info("위쪽에서 수거 약품목을 선택해주세요")