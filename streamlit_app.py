import streamlit as st
import pandas as pd
from urllib.parse import urlparse  # For URL validation

# URL of the CSV file in GitHub
url = 'https://raw.githubusercontent.com/ajthebear/family-recipes/476e7c2c98ac0330a579908b704db7f0ec9f142d/Family_Recipe_Viewer_Cleaned_v4.csv'

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

# Set up page navigation
page = st.sidebar.selectbox("Select Page", ["View Recipe", "Add Recipe"])

if page == "View Recipe":
    # View Recipe page
    st.title("Family Recipe Viewer")

    recipe_name = st.selectbox("Select a Recipe", recipe_data["Recipe Name"].unique())
    recipe = recipe_data[recipe_data["Recipe Name"] == recipe_name].iloc[0]

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
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Ingredients")
    ingredients = recipe["Ingredients"].split(",")
    for ingredient in ingredients:
        st.markdown(f"- {ingredient.strip()}")
    
    st.subheader("Bust Out List")
    bust_out_list = recipe["Bust Out List"].split(",")
    for item in bust_out_list:
        st.markdown(f"- {item.strip()}")

    st.subheader("Instructions")
    instructions = recipe["Instructions"].split(",")
    for idx, instruction in enumerate(instructions, start=1):
        st.markdown(f"**Step {idx}:** {instruction.strip()}")

elif page == "Add Recipe":
    # Add Recipe page
    st.title("Add a New Recipe")

    # Input fields
    recipe_name = st.text_input("Recipe Name")
    with_title = st.text_input("Secondary Title (e.g., 'with rice and veggies')")
    calories = st.number_input("Calories", min_value=0)
    prep_time = st.number_input("Prep Time (minutes)", min_value=0)
    cook_time = st.number_input("Cook Time (minutes)", min_value=0)
    recipe_bio = st.text_area("Recipe Bio")
    bust_out_list = st.text_area("Bust Out List (separate items with commas)")
    ingredients = st.text_area("Ingredients (separate items with commas)")
    instructions = st.text_area("Instructions (separate steps with commas)")
    image_url = st.text_input("Image URL")

    # Dietary flags
    dairy_free = st.checkbox("Dairy-Free")
    vegetarian = st.checkbox("Vegetarian")

    # Submit button
    if st.button("Submit Recipe"):
        # Add the new recipe to a DataFrame or CSV file
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

        # Optionally save this to a CSV
        try:
            new_df = pd.DataFrame([new_recipe])
            new_df.to_csv("user_recipes.csv", mode='a', header=False, index=False)  # Appends new recipe to a CSV file
            st.success("Recipe added successfully!")
        except Exception as e:
            st.error(f"An error occurred while saving the recipe: {e}")
