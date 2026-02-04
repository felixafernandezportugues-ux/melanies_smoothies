# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import snowflake.connector
from cryptography.hazmat.primitives import serialization

def get_snowflake_connection():
    # 1. Traer el string del secret
    raw_key = st.secrets["snowflake"]["private_key_raw"]
    
    # 2. Convertir a objeto de clave (Si tiene contraseña, ponla en password=b'tu_pass')
    p_key = serialization.load_pem_private_key(
        raw_key.encode(),
        password=None, 
        backend=None
    )

    # 3. Convertir a formato DER
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 4. Pasar la clave pkb al parámetro private_key
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        private_key=pkb,  # <--- AQUÍ está el truco
        role=st.secrets["snowflake"]["role"],
        warehouse=st.secrets["snowflake"]["warehouse"]
    )

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:',name_on_order)

cnx= st.connection("snowflake")
session=cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5,
    help="You can not choose more than 5 ingredients"
)
if ingredients_list:
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
    st.write(f'La lista de ingredientes es: {ingredients_string}')

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    #st.write(my_insert_stmt)
    #st.stop()

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered,{name_on_order}!', icon="✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
#st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
