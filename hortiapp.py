import streamlit as st
import pandas as pd
import joblib
from translate import Translator

# Set page configuration
st.set_page_config(page_title="Best Horticulture Crop Locations and Yield Prediction App", page_icon="🌾", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background-color: white;
        padding: 20px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput input {
        border-radius: 5px;
    }
    .stSelectbox select {
        background-color: #f0f2f6;
        border-radius: 5px;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00008B;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        background-color: sea green;
        padding: 10px;
        border-radius: 5px;
    }
    p, label {
        color: #00008B;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        font-weight: bold;
        font-size: 20px;
    }
    .stSelectbox label, .stTextInput label {
        color: blue;
        font-size: 20px;
    }
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

# Define a function to translate text
def translate_text(text, dest_language):
    if dest_language == 'en':
        return text
    translator = Translator(to_lang=dest_language)  # Initialize the translator here
    return translator.translate(text)

# Define the layout of your app
def main():
    # Language selection
    language = st.selectbox('Select Language', ['en', 'hi', 'kn', 'mr', 'ml', 'te', 'bn'], key='language_select')
    st.session_state['language'] = language

    # Translate function with session state language
    def t(text):
        return translate_text(text, st.session_state['language'])

    st.title(t('🌾 Best Horticulture Crop Locations and Yield Prediction App'))

    # App description
    st.markdown(t("""
    ### Welcome to the Best Horticulture Crop Location Finder and Yield Prediction App!
    This app helps you find the best locations for growing various horticulture crops based on historical data across every state and district of India. Select your desired crop name, state name, district name, season, and month to see the result.
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

        # Add dropdown for selecting season
        season_list = ['Kharif', 'Rabi', 'Whole Year', 'Summer', 'Winter', 'Autumn']
        st.header(t('🌦️ Select Season:'))
        season = st.selectbox(t('Season'), season_list, key='season_select_state')

        # Add dropdown for selecting month
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        st.header(t('📅 Select Month:'))
        month = st.selectbox(t('Month'), range(1, 13), format_func=lambda x: t(month_names[x]), key='month_select_state')

        # Add a button to show information about the crop
        if st.button(t('Show Information About the Crop')):
            # Filter crop data based on user input
            filtered_crop_data = crop_data[
                (crop_data['Crop'] == crop_name) & 
                (crop_data['State_Name'] == state_name) & 
                (crop_data['District_Name'] == district_name) & 
                (crop_data['Season'] == season) & 
                (crop_data['Months'] == month_names[month])
            ]

            # If there is data available for the selected crop, state, district, season, and month, display it
            if not filtered_crop_data.empty:
                best_location = filtered_crop_data.loc[filtered_crop_data['Yield'].idxmax()]
        
                st.subheader(t(f'🌾 Get to know more about {crop_name} in {district_name}, {state_name} 🌾'))
                st.write(t(f"**District:** {best_location['District_Name']}"))
                st.write(t(f"**Season:** {best_location['Season']}"))
                st.write(t(f"**Area:** {best_location['Area']} Hectares"))
                st.write(t(f"**Production:** {best_location['Production']} Tonnes"))
                st.write(t(f"**Yield:** {best_location['Yield']} Tonnes per Hectare"))
                st.write(t(f"**Best Month:** {best_location['Months']}"))
                st.write(t(f"**Best Year for Crop Yield:** {best_location['Crop_Year']}"))
        
            else:
                st.warning(t(f'No data available for {crop_name} in {district_name}, {state_name} for the selected season and month.'))
        
            # Display the best season and other information if data is unavailable in the specific location
            fallback_data = crop_data[
                (crop_data['Crop'] == crop_name) & 
                (crop_data['State_Name'] == state_name) & 
                (crop_data['District_Name'] == district_name)
            ]

            if not fallback_data.empty:
                best_fallback_location = fallback_data.loc[fallback_data['Yield'].idxmax()]
                st.info(t(f'Best season for growing {crop_name} in {district_name} is {best_fallback_location["Season"]}.'))
                st.write(t(f"**District:** {best_fallback_location['District_Name']}"))
                st.write(t(f"**Area:** {best_fallback_location['Area']} Hectares"))
                st.write(t(f"**Production:** {best_fallback_location['Production']} Tonnes"))
                st.write(t(f"**Yield:** {best_fallback_location['Yield']} Tonnes per Hectare"))
                st.write(t(f"**Best Month:** {best_fallback_location['Months']}"))
                st.write(t(f"**Best Year for Crop Yield:** {best_fallback_location['Crop_Year']}"))

            else:
                # If no data for the selected district is available, find data for the state
                state_fallback_data = crop_data[
                    (crop_data['Crop'] == crop_name) & 
                    (crop_data['State_Name'] == state_name)
                ]

                if not state_fallback_data.empty:
                    best_state_location = state_fallback_data.loc[state_fallback_data['Yield'].idxmax()]
                    st.info(t(f'Best location for growing {crop_name} in {state_name} is {best_state_location["District_Name"]} during {best_state_location["Season"]}.'))
                    st.write(t(f"**District:** {best_state_location['District_Name']}"))
                    st.write(t(f"**Area:** {best_state_location['Area']} Hectares"))
                    st.write(t(f"**Production:** {best_state_location['Production']} Tonnes"))
                    st.write(t(f"**Yield:** {best_state_location['Yield']} Tonnes per Hectare"))
                    st.write(t(f"**Best Month:** {best_state_location['Months']}"))
                    st.write(t(f"**Best Year for Crop Yield:** {best_state_location['Crop_Year']}"))

                else:
                    # Find the best overall location for the crop if no state-specific data is available
                    overall_fallback_data = crop_data[crop_data['Crop'] == crop_name]
                    if not overall_fallback_data.empty:
                        best_overall_location = overall_fallback_data.loc[overall_fallback_data['Yield'].idxmax()]
                        st.info(t(f'The best location for growing {crop_name} in India is {best_overall_location["District_Name"]}, {best_overall_location["State_Name"]} during {best_overall_location["Season"]}.'))
                        st.write(t(f"**District:** {best_overall_location['District_Name']}"))
                        st.write(t(f"**State:** {best_overall_location['State_Name']}"))
                        st.write(t(f"**Area:** {best_overall_location['Area']} Hectares"))
                        st.write(t(f"**Production:** {best_overall_location['Production']} Tonnes"))
                        st.write(t(f"**Yield:** {best_overall_location['Yield']} Tonnes per Hectare"))
                        st.write(t(f"**Best Month:** {best_overall_location['Months']}"))
                        st.write(t(f"**Best Year for Crop Yield:** {best_overall_location['Crop_Year']}"))
                    else:
                        st.error(t('No data available for the selected crop in India.'))
        
        # Add a section to calculate the crop yield based on production and area
        st.header(t('🌾 Calculate Crop Yield'))

        production = st.number_input(t('Total Production (in tonnes)'), min_value=0.0, step=0.01)
        area = st.number_input(t('Area (in hectares)'), min_value=0.0, step=0.01)

        # Add a button to calculate the crop yield
        if st.button(t('Calculate Yield')):
            if area != 0:
                yield_value = production / area
                st.success(t(f'The estimated yield for your crop is {yield_value:.2f} tonnes per hectare.'))
            else:
                st.warning(t('Area cannot be zero. Please enter a valid area.'))

# Run the app
if __name__ == '__main__':
    main()
