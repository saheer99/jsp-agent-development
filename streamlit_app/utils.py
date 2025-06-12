import streamlit as st
import base64
from PIL import Image

def inject_custom_css():
    hide_streamlit_style = """ <style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} </style> """
    st.markdown(hide_streamlit_style,unsafe_allow_html=True)

    with open('streamlit_app/css/bootstrap-5.0.2/css/bootstrap.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    with open('streamlit_app/css/cg_streamlit.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    with open('streamlit_app/css/navbar-top-fixed.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    padding = 0
    st.markdown(f""" <style>
        .reportview-container .main .block-container{{
            padding-top: {padding}rem;
            padding-right: {padding}rem;
            padding-left: {padding}rem;
            padding-bottom: {padding}rem;
        }} </style> """, unsafe_allow_html=True)

def favicon(color):
    if(color==1):
        img_icon = Image.open("streamlit_app/images/Capgemini_Spade_Black_Mono_RGB.png")
    else:
        img_icon = Image.open("streamlit_app/images/Capgemini_Spade_2Colors_RGB.png")
    return img_icon

def navbar_component(page_header):
    with open("streamlit_app/images/LogoCapgeminiColor.png", "rb") as image_logo_file:
        image_logo_as_base64 = base64.b64encode(image_logo_file.read())

    component = rf'''
        <nav class="navbar navbar-expand-lg">
          <div class="container-fluid">
            <a class="navbar-brand d-flex align-items-center my-2 my-lg-0 me-lg-auto text-decoration-none" href="#">
              <div class="cap-logo">
                <img src="data:image/png;base64, {image_logo_as_base64.decode("utf-8")}" height="30"/>
              </div>
              <span>{page_header}</span>
            </a>
          </div>
        </nav>'''
    st.markdown(component, unsafe_allow_html=True)

def sidebar_background_image():
    with open("streamlit_app/images/sidebar_background.jpg", "rb") as image_logo_file:
        image_logo_as_base64 = base64.b64encode(image_logo_file.read())

    st.markdown(rf'''
        <style>
            [data-testid="stSidebar"] {{
                background-image: url(data:image/png;base64,{image_logo_as_base64.decode("utf-8")});
            }}
        </style>
        ''',
        unsafe_allow_html=True,
    )
