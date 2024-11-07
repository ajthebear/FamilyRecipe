import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import base64
import os  # Import to check if file exists

# Updated URL of the CSV file in GitHub
url = 'https://raw.githubusercontent.com/ajthebear/family-recipes/9d24313144ee037239270ae6070c0d70c9c001b5/Family_Recipe_Viewer_Cleaned_v8.csv'
@st.cache_data
def load_data():
    try:
        data = pd.read_csv(url)
        
        # List of required columns
        required_columns = [
            "Recipe Name", "with Title", "Calories", "Prep Time", "Cook Time", 
            "Recipe Bio", "Bust Out List", "Ingredients", "Instructions", 
            "Image URL", "Dairy-Free", "Vegetarian"
        ]
        
        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            st.error(f"Missing columns in CSV: {', '.join(missing_columns)}")
            st.write("Columns found in CSV:", data.columns.tolist())  # Display available columns for debugging
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

# Function to toggle favorites
def toggle_favorite(recipe_name):
    if recipe_name in st.session_state.favorites:
        st.session_state.favorites.remove(recipe_name)
        st.success(f"Removed '{recipe_name}' from favorites")
    else:
        st.session_state.favorites.append(recipe_name)
        st.success(f"Added '{recipe_name}' to favorites")

# Load data
recipe_data = load_data()

# Initialize session state for navigation, favorites, and form submissions
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None
if "page" not in st.session_state:
    st.session_state.page = "recipe_viewer"  # Default to the recipe viewer page

# Path to the file where submitted recipes will be stored
submitted_recipes_file = "submitted_recipes.csv"

# Navigation options
def set_page(page_name):
    st.session_state.page = page_name

# Define page content functions
def show_recipe_viewer():
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

def show_favorites():
    st.title("Favorite Recipes")
    if not st.session_state.favorites:
        st.info("No favorites added yet.")
    else:
        for fav_recipe in st.session_state.favorites:
            # Display the favorite recipe name as a clickable link
            if st.button(f"View {fav_recipe}", key=f"view_{fav_recipe}"):
                # Set selected recipe and switch to recipe viewer
                st.session_state.selected_recipe = fav_recipe
                set_page("recipe_viewer")
                # Force a rerun by toggling a dummy state variable
                st.session_state["_rerun"] = not st.session_state.get("_rerun", False)

def show_add_recipe():
    st.title("Submit a New Recipe")

    # Recipe form inputs
    recipe_name = st.text_input("Recipe Name")
    with_title = st.text_input("Subtitle")
    calories = st.number_input("Calories", min_value=0)
    prep_time = st.number_input("Prep Time (minutes)", min_value=0)
    cook_time = st.number_input("Cook Time (minutes)", min_value=0)
    recipe_bio = st.text_area("Recipe Bio")
    ingredients = st.text_area("Ingredients (comma-separated)")
    bust_out_list = st.text_area("Bust Out List (comma-separated)")
    instructions = st.text_area("Instructions (comma-separated)")
    dairy_free = st.checkbox("Dairy-Free")
    vegetarian = st.checkbox("Vegetarian")

    # Image upload
    image_file = st.file_uploader("Upload a Recipe Image", type=["jpg", "jpeg", "png"])

    if st.button("Submit Recipe"):
        # Convert image to a URL (for demonstration)
        image_url = ""
        if image_file is not None:
            # Convert image to base64 and create a data URL
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
            image_url = f"data:image/jpeg;base64,{image_data}"
        
        new_recipe = {
            "Recipe Name": recipe_name,
            "with Title": with_title,
            "Calories": calories,
            "Prep Time": prep_time,
            "Cook Time": cook_time,
            "Recipe Bio": recipe_bio,
            "Bust Out List": bust_out_list,
            "Ingredients": ingredients,
            "Instructions": instructions,
            "Image URL": image_url,
            "Dairy-Free": dairy_free,
            "Vegetarian": vegetarian
        }
        
        # Append the new recipe to the CSV file
        if os.path.exists(submitted_recipes_file):
            # If the file exists, open it in append mode
            with open(submitted_recipes_file, "a") as f:
                pd.DataFrame([new_recipe]).to_csv(f, header=False, index=False)
        else:
            # If the file doesn't exist, create it with a header
            pd.DataFrame([new_recipe]).to_csv(submitted_recipes_file, index=False)
        
        st.success(f"Recipe '{recipe_name}' submitted successfully!")

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("View Recipes"):
    set_page("recipe_viewer")
if st.sidebar.button("Favorites"):
    set_page("favorites")
if st.sidebar.button("Add Recipe"):
    set_page("add_recipe")

# Display the chosen view
if st.session_state.page == "favorites":
    show_favorites()
elif st.session_state.page == "recipe_viewer":
    show_recipe_viewer()
elif st.session_state.page == "add_recipe":
    show_add_recipe()