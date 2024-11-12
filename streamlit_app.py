import streamlit as st
import pandas as pd
from urllib.parse import urlparse
import base64
import os  # Import to check if file exists

# Updated URL of the CSV file in GitHub
url = 'https://raw.githubusercontent.com/ajthebear/family-recipes/8d6b6afd6f50569c9e9dad2113289058dd59861a/Family_Recipe_Viewer_Cleaned_v9.csv'

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
    
    st.markdown(f"<h1 style='text-align: center; color: #D9534F; font-size: 36px; font-family: Georgia, serif; font-weight: bold; "
    "background-color: #FAEBD7; padding: 10px; border-radius: 10px; text-shadow: 1px 1px 2px #888888;'>"
    f"{recipe['Recipe Name']}</h1>", unsafe_allow_html=True)
   
    st.markdown(f"<h2 style='text-align: center; color: #008080; font-size: 28px; font-family: Arial, sans-serif; "
    "font-weight: 600; text-transform: uppercase; background-color: #E0FFFF; padding: 8px; border-radius: 5px; "
    "letter-spacing: 1px; line-height: 1.3; margin-top: 20px; margin-bottom: 15px;'>"
    f"{recipe['with Title']}</h2>", unsafe_allow_html=True)
   
    st.markdown(f"<h3 style='text-align: center; color: #20B2AA; font-size: 24px; font-weight: bold; font-family: Arial, sans-serif; "
    "background-color: #E6E6FA; padding: 6px 12px; border-radius: 8px; text-shadow: 0.5px 0.5px 1px #666666; "
    "margin-top: 15px; margin-bottom: 15px;'>"
    f"{recipe['Calories']} Calories</h3>", unsafe_allow_html=True)

    image_url = recipe["Image URL"] if pd.notna(recipe["Image URL"]) and is_valid_url(str(recipe["Image URL"])) else "https://via.placeholder.com/150"
    st.image(image_url, use_container_width=True)
    
    
    col1, col2 = st.columns(2)
    with col1:
        prep_time = str(recipe['Prep Time']).strip()
        st.markdown(f"<p style='font-size: 18px; font-weight: bold; color: #FF6347; background-color: #FFF8DC; padding: 4px; "
    f"border-radius: 5px; text-align: center;'>⏱️ Prep Time: {prep_time} minutes</p>",
    unsafe_allow_html=True)

    with col2:
        cook_time = str(recipe['Cook Time']).strip()
        st.markdown(f"<p style='font-size: 18px; font-weight: bold; color: #20B2AA; background-color: #E0FFFF; padding: 4px; "
    f"border-radius: 5px; text-align: center;'>🍲 Cook Time: {cook_time} minutes</p>",
    unsafe_allow_html=True)
    
    # Display flags for Dairy-Free, Low Calorie, and Vegetarian
    st.markdown(
    "<hr style='border: 0; height: 3px; background: linear-gradient(to right, #FF6347, #20B2AA); box-shadow: 0 4px 4px -2px #aaa;'>",
    unsafe_allow_html=True)
    flag_col1, flag_col2, flag_col3 = st.columns(3)

    if recipe["Dairy-Free"]:
        with flag_col1:
            st.markdown(
            "<p style='font-size: 16px; font-weight: bold; color: #4169E1; background-color: #E6EFFF; padding: 8px; "
            "border-radius: 8px; text-align: center;'>🥛 Dairy-Free</p>",
            unsafe_allow_html=True
        )

    if recipe["Calories"] <= 675:
        with flag_col2:
            st.markdown(
            "<p style='font-size: 16px; font-weight: bold; color: #8B008B; background-color: #F3E6F5; padding: 8px; "
            "border-radius: 8px; text-align: center;'>🍏 Low Calorie</p>",
            unsafe_allow_html=True
        )

    if recipe["Vegetarian"]:
        with flag_col3:
            st.markdown(
            "<p style='font-size: 16px; font-weight: bold; color: #228B22; background-color: #E6FFE6; padding: 8px; "
            "border-radius: 8px; text-align: center;'>🥕 Vegetarian</p>",
            unsafe_allow_html=True
        )

    st.markdown(
    "<hr style='border: 0; height: 3px; background: linear-gradient(to right, #FF6347, #20B2AA); box-shadow: 0 4px 4px -2px #aaa;'>",
    unsafe_allow_html=True)

    # Recipe Bio section
    st.markdown("<h2 style='color: #FF6347; font-family: Georgia, serif;'>Recipe Bio</h2>", unsafe_allow_html=True)
    st.markdown(
    f"<div style='background-color: #FAF3E0; padding: 15px; border-radius: 10px; margin-top: 10px;'>"
    f"<p style='font-size: 16px; color: #008080; font-style: italic; line-height: 1.6; text-align: justify;'>{recipe['Recipe Bio']}</p>"
    "</div>",
    unsafe_allow_html=True)


    # Two-column layout for Ingredients and Bust Out List, now with bullet points in both sections
    col1, col2 = st.columns(2)
    with col1:
        # Ingredients Section
        st.markdown("<h2 style='color: #FF6347; font-family: Georgia, serif;'>Ingredients</h2>", unsafe_allow_html=True)

        # Split ingredients by commas, clean up whitespace, and build the HTML list
        ingredients = recipe["Ingredients"].split(",")  # Split ingredients by commas
        ingredients_list = "".join(f"<li style='margin-bottom: 5px;'>{ingredient.strip()}</li>" for ingredient in ingredients)

        # Display the ingredients as a single block
        st.markdown(f"<div style='background-color: #FAF3E0; padding: 10px; border-radius: 10px; margin-top: 10px;'>"
        f"<ul style='font-size: 16px; color: #008080; line-height: 1.6;'>{ingredients_list}</ul>""</div>",unsafe_allow_html=True)
        
    with col2:
        # Bust Out List Section
        st.markdown("<h2 style='color: #FF6347; font-family: Georgia, serif;'>Bust Out List</h2>", unsafe_allow_html=True)

        # Split bust-out list items by commas, clean up whitespace, and build the HTML list
        bust_out_list = recipe["Bust Out List"].split(",")  # Split items by commas
        bust_out_list_html = "".join(f"<li style='margin-bottom: 5px;'>{item.strip()}</li>" for item in bust_out_list)

        # Display the bust-out list as a single block
        st.markdown(f"<div style='background-color: #FAF3E0; padding: 10px; border-radius: 10px; margin-top: 10px;'>"f"<ul style='font-size: 16px; color: #008080; line-height: 1.6;'>{bust_out_list_html}</ul>""</div>",unsafe_allow_html=True)


    # Line break before instructions
    st.markdown("<hr style='border: 0; height: 3px; background: linear-gradient(to right, #FF6347, #20B2AA); box-shadow: 0 4px 4px -2px #aaa;'>",unsafe_allow_html=True)

    # Instructions Section
    st.markdown("<h2 style='color: #FF6347; font-family: Georgia, serif;'>Instructions</h2>", unsafe_allow_html=True)

    # Split instructions by commas, clean up whitespace, and build the HTML for each step
    instructions = recipe["Instructions"].split(",")
    instructions_html = "".join(f"<p style='font-size: 20px; margin-bottom: 10px; color: #008080; font-family: Arial, sans-serif;'>"f"<strong>Step {idx}:</strong> {instruction.strip()}</p>"for idx, instruction in enumerate(instructions, start=1))


    # Display the instructions as a single block
    st.markdown(
    f"<div style='background-color: #FAF3E0; padding: 15px; border-radius: 10px; margin-top: 10px;'>"f"{instructions_html}""</div>",unsafe_allow_html=True)

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

def show_recipe_list():
    st.title("Recipe List")

    # Loop through each recipe to display an image in one column and a button in the other
    for index, row in recipe_data.iterrows():
        col1, col2 = st.columns([1, 3])  # Adjust column widths as desired

        with col1:
            # Display a small image (fallback to placeholder if URL is missing or invalid)
            image_url = row["Image URL"] if pd.notna(row["Image URL"]) and is_valid_url(row["Image URL"]) else "https://via.placeholder.com/80"
            st.markdown(
        f"""
        <div style='display: flex; justify-content: center; align-items: center; height: 100%; min-height: 150px;'>
            <img src='{image_url}' style='width: 99px; border-radius: 5px;'>
        </div>
        """,
        unsafe_allow_html=True
    )
            

        with col2:
            # Display a button for each recipe with clickable functionality
            if st.button(f"View {row['Recipe Name']}", key=f"select_{row['Recipe Name']}"):
                # Set selected recipe and navigate to recipe viewer
                st.session_state.selected_recipe = row["Recipe Name"]
                set_page("recipe_viewer")
                # Trigger a rerun by toggling a dummy state variable
                st.session_state["_rerun"] = not st.session_state.get("_rerun", False)

            # Display the recipe bio below the button
            st.markdown(f"<p style='font-size: 14px; color: #555;'>{row['Recipe Bio']}</p>", unsafe_allow_html=True)

# CSS to set the sidebar width and style sidebar buttons
sidebar_css = f"""
    <style>
    /* Set the sidebar width */
    .css-1d391kg {{"width": 220px;}}  /* Adjust this value to match your desired width */

    /* Style sidebar buttons */
    .stButton > button {{
        width: 100%;
        font-size: 18px;
        padding: 10px;
        background-color: #FF6347;
        color: white;
        border: none;
        border-radius: 8px;
        margin-top: 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }}
    
    /* Hover effect for buttons */
    .stButton > button:hover {{
        background-color: #FF4500;  /* Slightly darker on hover */
    }}
    </style>
"""
st.markdown(sidebar_css, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Recipe List"):
    set_page("recipe_list")
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
elif st.session_state.page == "recipe_list":
    show_recipe_list()
elif st.session_state.page == "add_recipe":
    show_add_recipe()
