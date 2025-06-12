from streamlit import *
import streamlit as st
import utils as utl
import os
import json
import time
import itertools
import pandas as pd, numpy as np
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript
from urllib.parse import urlparse

def init(page_header):
    #Favicon
    # pass 1 for black icon and 2 for blue icon
    img_icon = utl.favicon(2)

    st.set_page_config(page_icon=img_icon, page_title='JSP Agent', layout='wide', menu_items=None)

    #Design system CSS
    utl.inject_custom_css()
    # st.markdown(f'<script>window.prerenderReady=!1</script>', unsafe_allow_html=True)


    #Navbar
    utl.navbar_component(page_header)
    #Sidebar
    utl.sidebar_background_image()

def slide(file, _width=1200):
    st.image(file, width=_width)

def csv(file, show_filters=True):
    df = pd.read_csv(file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    if show_filters:
        def dropdown(col):
            items = df.iloc[:, col]
            items = items.to_list()
            items = [item for item in items if str(item) != 'nan']
            dedupe = ['[ALL]'] + list(dict.fromkeys(items))
            title = df.columns[col]
            return st.selectbox(title, dedupe)

        COLUMNS=min(6, len(df.columns))
        col = st.columns(COLUMNS)

        option=[]
        for ii in range(COLUMNS):
            with col[ii]:
                option.append( dropdown(ii) )

        for ii in range(COLUMNS):
            if (option[ii] != '[ALL]'):
                header = df.columns[ii]
                df = df[df[header] == option[ii]]

        st.divider()

    st.dataframe( df, hide_index=True )

from openai import AzureOpenAI

def gen_ai_query(prompt):
  endpoint = 'https://raise-llm-002.openai.azure.com/'
  deployment = 'gpt-4o'
  client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_version="2024-02-01",
  )
  response = client.chat.completions.create(
    model=deployment,
    temperature=0,
    messages=[
      {
        "role": "user",
        "content": prompt,
      },
    ],
  )
  return response.choices[0].message.content

def powerpoint(file):
    
    page_html = '''
<style>
section.wrapper {
  width: 100%;
}

.photo-gallery__wrapper {
  width: 1320px;
  margin: 0 auto;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
}
.photo-gallery__wrapper div {
  height: 45px;
  overflow: hidden;
}

.image-holder {
  width: 1320px;
  height: 740px;
  overflow: hidden;
  margin: 0 auto;
}
.image-holder img {
  width: 1280px;
  height: 720px;
  border: 1px solid #000;
  object-fit: cover;
  object-position: 50% 50%;
}
.image-thumbnail img {
  width: 64px;
  height: 36px;
  border: 1px solid #000;
  object-fit: cover;
  transition: transform 0.35s;
  transform: scale(1);
  filter: grayscale(1);
}
.image-thumbnail img.active {
  border: 2px solid #f00;
  filter: none;
}
.image-thumbnail img:hover {
  border: 1px solid #000;
  transition: transform 0.35s, filter 0.35s linear;
  transform: scale(1.1);
  filter: none;
}
</style>

<script>
let changeImage = (e) => {

    let imgSrc = e.src;
    imgSrc = imgSrc.replace(/720/g, '1280');
    document.querySelector('.image-holder > img').src = imgSrc;
    document.querySelector('.image-thumbnail > img.active').classList.toggle('active');
    e.classList.toggle('active');

};
</script>
'''

    current_file_path = os.path.abspath(file)
    directory_path = os.path.dirname( current_file_path )
    filename = os.path.basename( current_file_path )[:-3]
    img, label = [], []
    for image in os.scandir( "static/images/" + filename ):
        img.append(image.name)
        label.append(image.name[5:-4])
    label, img = sorted(label), sorted(img)
    
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    parsed = urlparse(url)

    page_html += f"""
    <section class="wrapper">
      <div class="image-holder">
        <img src="http://{parsed.netloc}/app/static/images/{filename}/{img[0]}" \>
      </div>
      <div class="photo-gallery__wrapper">
        <div class="image-thumbnail" onclick="changeImage(this);">
          <img src='http://{parsed.netloc}/app/static/images/{filename}/{img[0]}' alt='' onclick="changeImage(this);" class="active">
        </div>
    """
    begin, end = 1, len( img )
    for ii in range( begin, end ):
        page_html += f"""    <div class="image-thumbnail">
          <img src='http://{parsed.netloc}/app/static/images/{filename}/{img[ii]}' alt='' onclick="changeImage(this);">
        </div>"""
        if (ii+1) % 10 == 0:
            page_html += """  </div>
      <div class="photo-gallery__wrapper">"""

    page_html += """  </div>
    </section>
    """

    # code(page_html)

    html(page_html, height=1200)
