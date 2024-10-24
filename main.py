import os
import streamlit as st
from openai import OpenAI
from io import BytesIO

# OpenAI API Key 설정 (streamlit secrets에서 가져오기)
openai_api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)

# 특정 경로의 텍스트 파일을 읽는 함수
def read_template_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            template = file.read()
        return template
    except Exception as e:
        return f"파일을 읽는 중 오류가 발생했습니다: {str(e)}"

# 판결문을 생성하는 함수
def generate_judgment(user_input, template):
    prompt = f"""
    다음은 이혼 판결문 작성 형식입니다:\n\n{template}\n\n
    그리고 아래는 사용자가 입력한 상황입니다:\n\n{user_input}\n\n
    이 상황을 바탕으로 위 형식에 맞게 이혼 판결문을 작성하세요.
    """
    
    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", 
                "content": prompt
                },  
                {"role": "user", "content": user_input} 
            ]
        )
        # 응답에서 텍스트 추출
        judgment_text = response.choices[0].message.content
        return judgment_text
    except Exception as e:
        return f"Error: {str(e)}"

# txt 파일로 저장
def generate_txt(judgment_text):
    buffer = BytesIO()
    buffer.write(judgment_text.encode('utf-8'))
    buffer.seek(0)
    return buffer

# Streamlit 웹 인터페이스
def main():
    # 이미지 파일 경로 설정 
    image_path = './t.png'
    st.image(image_path, use_column_width=True)

    # 설명 문구 추가
    st.write("관련 법률, 선행 판결문을 기반으로 상황에 따라 이혼 판결문을 생성해주는 서비스입니다.")

    # 사용자 입력 창에 주황색 테두리 및 안내문구 스타일 적용
    st.markdown("""
        <style>
        .stTextArea textarea {
            border: 2px solid #FF6600;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 사용자 입력을 위한 텍스트 필드
    user_input = st.text_area("이혼 상황에 대해 설명해주세요.", height=200)

    # 텍스트 파일 경로 설정 (개발자가 미리 넣어둔 경로)
    file_path = 'template.txt'  # 템플릿 파일의 경로
    
    # 템플릿 파일 읽기
    template_content = read_template_file(file_path)
    
    if '오류' in template_content:
        st.error(template_content)
    else:
        # 버튼 클릭 시 판결문 생성
        if st.button("판결문 생성"):
            if user_input:
                with st.spinner("판결문 생성 중..."):
                    judgment = generate_judgment(user_input, template_content)

                    # 다운로드 버튼을 판결문 출력 위로 이동
                    txt_buffer = generate_txt(judgment)
                    st.download_button(
                        label="텍스트 파일 다운로드",
                        data=txt_buffer,
                        file_name="판결문.txt",
                        mime="text/plain"
                    )

                    # 생성된 판결문 출력
                    st.subheader("생성된 판결문")
                    st.write(judgment)
            else:
                st.warning("상황을 입력해주세요.")

if __name__ == '__main__':
    init_api()
    main()
