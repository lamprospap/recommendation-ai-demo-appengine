import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import json
import pandas as pd
from PIL import Image
from io import BytesIO
from PIL import Image
import requests

def _set_block_container_style(
    max_width: int = 1000,
    max_width_100_percent: bool = False,
    padding_top: int = 1,
    padding_right: int = 1,
    padding_left: int = 1,
    padding_bottom: int = 20,
):
    if max_width_100_percent:
        max_width_str = f"max-width: 100%;"
    else:
        max_width_str = f"max-width: {max_width}px;"
    st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
        font-family: https://fonts.googleapis.com/css?family=Roboto:100,100i,300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=greek
    }}
    .reportview-container .fixed-width {{
    
    white-space: pre;
    font-size: .8rem;
    overflow-x: auto;
    }}

    .reportview-container .element-container {{
    margin: 0 0 1rem;
    display: flex;
    flex-direction: column;
    position: relative;
    
    }}

    .stBlock {{
        text-align: center;
    }}

    # .block-container {{
    # text-align: center;
    # }}

    .reportview-container .fixed-width{{
    }}

    .css-1pq2z0s {{
    font-size: 0.8rem;
    text-align: center;
    }}



    

.reportview-container .fixed-width {{
    white-space: pre;
    font-size: .8rem;
    overflow-x: auto;
    text-align: center;
}}

    
</style>
""",
        unsafe_allow_html=True,
    )
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
_set_block_container_style()

@st.cache(allow_output_mutation=True,ttl=3600)
def load_data():
    data = []
    def tryconvert(value):
        try:
            return value[0]['uri']
        except:
            return ''
    with open('migato_catalogue.json') as f:
        for line in f:
            data.append(json.loads(line))
    data = pd.DataFrame(data)
    t = pd.concat([pd.DataFrame(pd.json_normalize(x)) for x in data['product_metadata']],ignore_index=True)
    data = pd.concat([data,t],axis=1, sort=False)
    # data = data[data['images'].str.len() != 0]
    data['image'] = data['images'].apply(lambda x: tryconvert(x))
    data = data[['id','canonical_product_uri','title','image','exact_price.display_price','exact_price.original_price']]
    data.rename(columns={"exact_price.display_price":"display_price","exact_price.original_price":"original_price","canonical_product_uri":"url"},inplace=True)
    return data

data = load_data()
## Setup sidebar
def main():
    st.title("Migato Recommendation System Demo")
    st.info('This is an AI recommendation System for Migato website. The model prediction based in product catalogue items and user events')
    st.sidebar.image('https://demo-en.adsquirrel.io/static/images/logo2.png',width=200)
    st.sidebar.title("Parameters")
    # app_mode = st.sidebar.selectbox("Add Product ID",
    #         ["Show instructions", "Run the app", "Show the source code"])

    # visitorid = st.sidebar.selectbox("Add Visitor ID",
    #         ["Show instructions", "Run the app", "Show the source code"])
    # filter1 = st.sidebar.selectbox("Add filter ID",
    #         ["Show instructions", "Run the app", "Show the source code"])
    product_input = st.sidebar.text_input("ADD PRODUCT ID", '')
    st.sidebar.subheader('optional')    
    visitor_input = st.sidebar.text_input("ADD VISITOR ID", '')
    st.sidebar.subheader('optional')    
    user_input = st.sidebar.text_input("ADD USER ID", '')
    st.sidebar.subheader('FILTER PREDICTIONS')    

    filter1 = st.sidebar.selectbox("FILTER PREDICTION WITH PRODUCTS IN STOCK ONLY",
            ['',"filterOutOfStockItems"])
    filter2 = st.sidebar.multiselect("FILTER PREDICTIONS BY TAG",
            ['',"ΑΝΤΡΑΣ",'ΓΥΝΑΙΚΑ','ΠΑΙΔΙ'])
    prediction_button = st.sidebar.button('Predict')

    if prediction_button:
        if visitor_input and user_input:
            tmp = {'visitorId': visitor_input,'userId':user_input}
        elif visitor_input:
            tmp = {'visitorId': visitor_input}
        elif user_input:
            tmp = {'userId':user_input}
        else:
            tmp = {}
        filter_created = []
        if filter2:
            for f in filter2:
                filter_created.append('tag=' + '"'+f+'"')
            
        filter_created = ' '.join(filter_created)
        if filter1:
            filter_created = filter_created+' '+filter1
        if not filter_created:
            filter_created=''
        headers = {"Content-Type":"application/json"}
        params = {'filter': filter_created,
        'dryRun': 'False',
        'userEvent': {'eventType': 'detail-page-view',
        'userInfo': tmp,
        'productEventDetail': {'productDetails': [{'id': product_input.lstrip().rstrip()}]}}}
        url = 'https://recommendationengine.googleapis.com/v1beta1/projects/ocm-product-recommendations-ai/locations/global/catalogs/default_catalog/eventStores/default_event_store/placements/migato_new_placement:predict?key=AIzaSyDAlEp7dAQwsmq8vz_tgnpIwzF-4Z7Vu_Q'
        result = requests.post(url,data = json.dumps(params),headers=headers)
        result = json.loads(result.content)
        products = result['results']
        prod = [prod['id'] for prod in products]
        st.sidebar.image(data[data['id']==product_input.lstrip().rstrip()]['image'].iloc[0], use_column_width=True, caption=data[data['id']==product_input]['title'].iloc[0])
        for t in range(0,4):
                col1, col2,col3,col4,col5 = st.beta_columns((1, 1, 1, 1,1))
                try:
                    col1.image(data[data['id']==prod[(t*5)+0]]['image'].iloc[0], use_column_width=True,caption=data[data['id']==prod[(t*5)+0]]['title'].iloc[0])
                    col1.text(prod[(t*5)+0])
                    col1.markdown('~~'+str(data[data['id']==prod[(t*5)+0]]['original_price'].iloc[0])+'~~'  + '  ' + '**'+str(data[data['id']==prod[(t*5)+0]]['display_price'].iloc[0])+'**' +' €')
                except:
                    col1.image('https://www.brdtex.com/wp-content/uploads/2019/09/no-image.png', use_column_width=True,caption=data[data['id']==prod[(t*5)+0]]['title'].iloc[0])
                try:
                    col2.image(data[data['id']==prod[(t*5)+1]]['image'].iloc[0], use_column_width=True,caption=data[data['id']==prod[(t*5)+1]]['title'].iloc[0])
                    col2.text(prod[(t*5)+1])
                    col2.markdown('~~'+str(data[data['id']==prod[(t*5)+1]]['original_price'].iloc[0])+'~~'  + '  ' + '**'+str(data[data['id']==prod[(t*5)+1]]['display_price'].iloc[0])+'**' +' €')
                except:
                    col2.image('https://www.brdtex.com/wp-content/uploads/2019/09/no-image.png', use_column_width=True,caption=data[data['id']==prod[(t*5)+1]]['title'].iloc[0])
                try:
                    col3.image(data[data['id']==prod[(t*5)+2]]['image'].iloc[0], use_column_width=True,caption=data[data['id']==prod[(t*5)+2]]['title'].iloc[0])
                    col3.text(prod[(t*5)+2])
                    col3.markdown('~~'+str(data[data['id']==prod[(t*5)+2]]['original_price'].iloc[0])+'~~'  + '  ' + '**'+str(data[data['id']==prod[(t*5)+2]]['display_price'].iloc[0])+'**' +' €')
                except:
                    col3.image('https://www.brdtex.com/wp-content/uploads/2019/09/no-image.png', use_column_width=True,caption=data[data['id']==prod[(t*5)+2]]['title'].iloc[0])
                try:
                    col4.image(data[data['id']==prod[(t*5)+3]]['image'].iloc[0], use_column_width=True,caption=data[data['id']==prod[(t*5)+3]]['title'].iloc[0])
                    col4.text(prod[(t*5)+3])
                    col4.markdown('~~'+str(data[data['id']==prod[(t*5)+3]]['original_price'].iloc[0])+'~~'  + '  ' + '**'+str(data[data['id']==prod[(t*5)+3]]['display_price'].iloc[0])+'**' +' €')
                except:
                    col4.image('https://www.brdtex.com/wp-content/uploads/2019/09/no-image.png', use_column_width=True,caption=data[data['id']==prod[(t*5)+3]]['title'].iloc[0])
                try:
                    col5.image(data[data['id']==prod[(t*5)+4]]['image'].iloc[0], use_column_width=True,caption=data[data['id']==prod[(t*5)+4]]['title'].iloc[0])
                    col5.text(prod[(t*5)+4])
                    col5.markdown('~~'+str(data[data['id']==prod[(t*5)+4]]['original_price'].iloc[0])+'~~'  + '  ' + '**'+str(data[data['id']==prod[(t*5)+4]]['display_price'].iloc[0])+'**' +' €')
                except:
                    col5.image('https://www.brdtex.com/wp-content/uploads/2019/09/no-image.png', use_column_width=True,caption=data[data['id']==prod[(t*5)+4]]['title'].iloc[0])
        st.subheader('Prediction Format')
        st.code(result,language='javascript')


if __name__ == "__main__":
    main()