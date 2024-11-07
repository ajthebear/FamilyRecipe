import streamlit as st
import pandas as pd
from urllib.parse import urlparse

# URL of the CSV file in GitHub
url = 'https://raw.githubusercontent.com/ajthebear/family-recipes/ed0d8ed220cdd9512c84c5432dfe1d1e39caf831/Family_Recipe_Viewer_Cleaned_v5.csv'

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(url)
        required_columns = [
            "Recipe Name", "with Title", "Calories", "Prep Time", "Cook Time", 
            "Recipe Bio", "Bust Out List", "Ingredients", "Instructions", 
            "Image URL", "Dairy-Free", "Vegetarian"
        ]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
            return pd.DataFrame()
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

# Load data
recipe_data = load_data()

# Initialize session state for favorites and selected recipe
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# Page navigation
page = st.sidebar.selectbox("Select Page", ["View Recipe", "Add Recipe", "Favorites"])

# Function to toggle favorites
def toggle_favorite(recipe_name):
    if recipe_name in st.session_state.favorites:
        st.session_state.favorites.remove(recipe_name)
        st.success(f"Removed '{recipe_name}' from favorites")
    else:
        st.session_state.favorites.append(recipe_name)
        st.success(f"Added '{recipe_name}' to favorites")

if page == "View Recipe":
    st.title("Family Recipe Viewer")
    
    # Select the recipe to display, defaulting to a selected favorite if available
    recipe_name = st.selectbox("Select a Recipe", recipe_data["Recipe Name"].unique(), 
                               index=recipe_data["Recipe Name"].tolist().index(st.session_state.selected_recipe) 
                               if st.session_state.selected_recipe else 0)
    recipe = recipe_data[recipe_data["Recipe Name"] == recipe_name].iloc[0]
    st.session_state.selected_recipe = recipe_name  # Store the selected recipe in session

    st.markdown(f"<h1 style='text-align: center; color: #FF6347;'>{recipe['Recipe Name']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: #FFA07A;'>{recipe['with Title']}</h2>", unsafe_allow_html=True)
    
    image_url = recipe["Image URL"] if pd.notna(recipe["Image URL"]) and is_valid_url(str(recipe["Image URL"])) else "https://via.placeholder.com/150"
    st.image(image_url, use_column_width=True)
    
    st.markdown(f"<h3 style='text-align: center; color: #008080;'>{recipe['Calories']} Calories</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Prep Time:** {recipe['Prep Time']} minutes")
    with col2:
        st.markdown(f"**Cook Time:** {recipe['Cook Time']} minutes")
    
    # Display flags for Dairy-Free, Low Calorie, and Vegetarian
    st.markdown("<hr>", unsafe_allow_html=True)
    flag_col1, flag_col2, flag_col3 = st.columns(3)
    if recipe["Dairy-Free"]:
        with flag_col1:
            st.markdown("<p style='font-size: 16px; color: green;'>Dairy-Free</p>", unsafe_allow_html=True)
    if recipe["Calories"] < 670:
        with flag_col2:
            st.markdown("<p style='font-size: 16px; color: blue;'>Low Calorie</p>", unsafe_allow_html=True)
    if recipe["Vegetarian"]:
        with flag_col3:
            st.markdown("<p style='font-size: 16px; color: purple;'>Vegetarian</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # Recipe Bio section
    st.subheader("Recipe Bio")
    st.markdown(f"<p style='font-size: 16px; color: #666666;'>{recipe['Recipe Bio']}</p>", unsafe_allow_html=True)

    # Two-column layout for Ingredients and Bust Out List, now with bullet points in both sections
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ingredients")
        ingredients = recipe["Ingredients"].split(",")  # Split ingredients by commas
        for ingredient in ingredients:
            st.markdown(f"- {ingredient.strip()}", unsafe_allow_html=True)
            
    with col2:
        st.subheader("Bust Out List")
        bust_out_list = recipe["Bust Out List"].split(",")  # Split bust-out list items by commas
        for item in bust_out_list:
            st.markdown(f"- {item.strip()}", unsafe_allow_html=True)

    # Line break before instructions
    st.markdown("<hr style='border-top: 3px solid #bbb;'>", unsafe_allow_html=True)

    # Left-aligned and enlarged cooking instructions
    st.subheader("Instructions")
    instructions = recipe["Instructions"].split(",")  # Split instructions by commas
    for idx, instruction in enumerate(instructions, start=1):
        st.markdown(f"<p style='font-size: 20px;'><strong>Step {idx}:</strong> {instruction.strip()}</p>", unsafe_allow_html=True)

    # Toggle favorite button
    if st.button("Add to Favorites" if recipe_name not in st.session_state.favorites else "Remove from Favorites"):
        toggle_favorite(recipe_name)

elif page == "Favorites":
    st.title("Favorite Recipes")
    if not st.session_state.favorites:
        st.info("No favorites added yet.")
    else:
        for fav_recipe in st.session_state.favorites:
            # Display the favorite recipe name as a clickable link
            if st.button(f"View {fav_recipe}", key=f"view_{fav_recipe}"):
                st.session_state.selected_recipe = fav_recipe
                st.experimental_rerun()  # Reload the app to show the View Recipe page with the selected recipe

elif page == "Add Recipe":
    # Add Recipe page code remains the same as in the previous example
    pass
