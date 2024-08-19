import streamlit as st
import pandas as pd
import joblib
import numpy as np
from translate import Translator

# Set page configuration
st.set_page_config(page_title="Best Horticulture Crop Locations and Yield Prediction App", page_icon="🌾", layout="wide")

st.markdown(
    f"""
    <style>
    .main {{
        background-color: white;
        padding: 20px;
    }}
    .stButton button {{
        background-color: #4CAF50;
        color: white;
    }}
    .stTextInput input {{
        border-radius: 5px;
    }}
    .stSelectbox select {{
        background-color: #f0f2f6;
        border-radius: 5px;
        color: white;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #00008B;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        background-color: sea green;
        padding: 10px;
        border-radius: 5px;
    }}
    p, label {{
        color: #00008B;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        font-weight: bold;
        font-size: 20px;
    }}
    .stSelectbox label, .stTextInput label {{
        color: blue;
        font-size: 20px;
    }}
    </style>
    """, unsafe_allow_html=True
)

# Load the crop data and the random forest model
crop_data = pd.read_csv("new_Clean_horticulture.csv")
model = joblib.load("xgb_hort_comp_model.pkl.gz")
scaler = joblib.load("scaler.pkl")

# Get the list of unique crops and states from the dataset
crop_list = crop_data['Crop'].unique()
state_list = crop_data['State_Name'].unique()

# Initialize session state
if 'username' not in st.session_state:
    st.session_state['username'] = ''

if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

# Initialize translator
translator = Translator(to_lang=st.session_state['language'])

# Define a function to translate text
def translate_text(text, dest_language):
    if dest_language == 'en':
        return text
    return translator.translate(text)

# Define the layout of your app
def main():
    
    # Language selection
    language = st.selectbox('Select Language', ['en', 'hi', 'kn', 'mr', 'ml', 'te', 'bn'])
    st.session_state['language'] = language
    
    # Update the translator object with the selected language
    translator = Translator(to_lang=language)

    # Translate function with session state language
    def t(text):
        return translate_text(text, st.session_state['language'])
    
    st.title(t('🌾 Best Horticulture Crop Locations and Yield Prediction App'))

    # App description
    st.markdown(t("""
    ### Welcome to the Best Horticulture Crop Location Finder and Yield Prediction App!
    This app helps you find the best locations for growing various horticulture crops based on historical data across every states and districts of India. Select your desired crop name, state name, and district name to see the result.
    You can also calculate the yield of your crops by entering the production and area. 
    Make informed decisions to maximize your agricultural productivity!
    """))
    
    # Add a separator
    st.markdown("---")

    # Add a page for username input
    if not st.session_state['username']:

        # Display an image
        st.image("FarmoidLogo.jpg", use_column_width=False, width=350)
        st.header(t('Enter your username:'))

        username = st.text_input(t('Username'))
        if st.button(t('Submit')):
            if username:
                st.session_state['username'] = username
                st.rerun()
            else:
                st.warning(t('Please enter a username.'))
    else:
        st.subheader(t(f'Welcome, {st.session_state["username"]}!'))
        
        # Add a logout button
        if st.button(t('Logout')):
            st.session_state['username'] = ''
            st.rerun()

        st.markdown("---")

        # Add dropdown for user to select crop name
        st.header(t('!Find out much more about your desired horticulture crop!'))
        st.header(t('🌱 Select Crop Name:'))
        crop_name = st.selectbox(t('Crop Name'), crop_list, key='crop_name_select_state')

        # Add dropdown for user to select state
        st.header(t('🌎 Select State:'))
        state_name = st.selectbox(t('State Name'), state_list, key='state_name_select_state')

        # Filter the districts based on the selected state
        district_list = crop_data[crop_data['State_Name'] == state_name]['District_Name'].unique()

        # Add dropdown for user to select district
        st.header(t('🏘️ Select District:'))
        district_name = st.selectbox(t('District Name'), district_list, key='district_name_select_state')

        # Add a button to show the best locations for the crop in the selected state and district
        if st.button(t('Show Information About the Crop')):
            # Filter crop data based on user input
            filtered_crop_data = crop_data[(crop_data['Crop'] == crop_name) & (crop_data['State_Name'] == state_name) & (crop_data['District_Name'] == district_name)]

            # If there is data available for the selected crop, state, and district, display it
            if not filtered_crop_data.empty:
                # Find the location with the highest yield for the selected crop in the selected state and district
                best_location = filtered_crop_data.loc[filtered_crop_data['Yield'].idxmax()]

                # Display information about the best location for the crop
                st.subheader(t(f'🌾Get to know more about {crop_name} in {district_name}, {state_name}🌾'))
                st.write(t(f"**District:** {best_location['District_Name']}"))
                st.write(t(f"**Season:** {best_location['Season']}"))
                st.write(t(f"**Area:** {best_location['Area']} Hectares"))
                st.write(t(f"**Production:** {best_location['Production']} Tonnes"))
                st.write(t(f"**Yield:** {best_location['Yield']} Tonnes per Hectare"))

                # Find the year with the highest yield for the selected crop in the selected state and district
                best_year = filtered_crop_data.loc[filtered_crop_data['Yield'].idxmax(), 'Crop_Year']
                st.write(t(f"**Best Year for Crop Yield:** {best_year}"))

                # Find the month for the best yield
                best_month = best_location['Months']
                st.write(t(f"**Best Month:** {best_month}"))
            else:
                st.warning(t(f'No data available for {crop_name} in {district_name}, {state_name}.'))

        # Add a separator
        st.markdown("---")

        # Add input fields for user to enter production and area for yield calculation
        st.header(t('📏 Calculate Yield:'))
        production_calc = st.number_input(t('Production for Calculation'), min_value=0.0)
        production_unit = st.selectbox(t('Production Unit'), [t('Tonnes'), t('Quintal')])
        area_calc = st.number_input(t('Area for Calculation'), min_value=0.0)
        area_unit = st.selectbox(t('Area Unit'), [t('Hectare'), t('Acre')])

        # Add a button to calculate yield
        if st.button(t('Calculate Yield')):
            if area_calc > 0:
                # Convert units to standard units (Hectares for area, Tonnes for production)
                if area_unit == t("Acre"):
                    area_in_hectares = area_calc * 0.404686
                else:
                    area_in_hectares = area_calc

                if production_unit == t("Quintal"):
                    production_in_tonnes = production_calc * 0.1
                else:
                    production_in_tonnes = production_calc

                yield_value = production_in_tonnes / area_in_hectares

                # Determine the correct unit for display
                if production_unit == t("Tonnes") and area_unit == t("Hectare"):
                    unit = t("Tonnes per Hectare")
                elif production_unit == t("Quintal") and area_unit == t("Acre"):
                    unit = t("Quintal per Acre")
                elif production_unit == t("Tonnes") and area_unit == t("Acre"):
                    unit = t("Tonnes per Acre")
                elif production_unit == t("Quintal") and area_unit == t("Hectare"):
                    unit = t("Quintal per Hectare")
                else:
                    unit = t("Unknown Unit")

                st.success(t(f'Calculated Yield: {yield_value:.2f} {unit}'))
            else:
                st.error(t('Area must be greater than 0 to calculate yield.'))

# Run the app
if __name__ == '__main__':
    main()
