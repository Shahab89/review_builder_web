import json
import os
from random import choice
import streamlit as st
import requests

#API_URL = os.environ.get('API_URL')
API_URL = 'http://127.0.0.1:8000/'  # Update with your API URL

ERROR_MESSAGE_TEMPLATE = """
Could not get {requested}

{error}
"""

EXAMPLE_PRODUCTS = [
    "Apple MacBook Pro 14-inch",
]


# Set the page configuration with a fancy title
st.set_page_config(page_title="Intelligent Review Builder with AI", page_icon="📝", layout="wide")


# Define the CSS to set the background image and improve styling
page_bg_img = '''
<style>

.left-side {
    padding: 20px;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.8); /* Light background for left side */
    margin-right: 10px; /* Adjust spacing */
}

.right-side {
    padding: 20px;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.8);  /* Light background for right side */
}

</style>
'''

# Inject the CSS into the Streamlit app
st.markdown(page_bg_img, unsafe_allow_html=True)

# Initialize session state variables
if 'product' not in st.session_state:
    st.session_state.product = choice(EXAMPLE_PRODUCTS)
if 'criteria' not in st.session_state:
    st.session_state.criteria = []
if 'rated_criteria' not in st.session_state:
    st.session_state.rated_criteria = {}
if 'reviews' not in st.session_state:
    st.session_state.reviews = []

# Function to fetch criteria from API or use dummy data
@st.cache_data(ttl=3600)
def fetch_criteria(product):
    if not API_URL:
        return ["Performance", "Display quality", "Battery life", "Portability",
                "Build quality", "Price"]
    try:
        res = requests.get(API_URL + 'criteria', params=dict(product=product))
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        st.error(ERROR_MESSAGE_TEMPLATE.format(requested='criteria', error=e))
        return []

# Function to fetch reviews from API or use dummy data
@st.cache_data(ttl=3600)
def fetch_reviews(product, rated_criteria):
    if not API_URL:
        return [
            """
            The Apple MacBook Pro 14-inch has been a reliable companion for my daily tasks. Its performance has met my expectations, allowing me to multitask smoothly. The display quality is crisp and clear, making movie nights even more enjoyable. While the battery life could be better, it's sufficient for my needs. The sleek design and sturdy build quality give me confidence in its durability.
            """,

            """
            I've been impressed with the Apple MacBook Pro 14-inch since the day I received it. The portability aspect is a game-changer for my on-the-go lifestyle, fitting seamlessly into my bag without weighing me down. The price point was reasonable considering the features it offers. The build quality speaks of Apple's commitment to excellence,and I appreciate the attention to detail in every aspect of the laptop.
            """,

            """
            Owning the Apple MacBook Pro 14-inch has elevated my work experience to a new level. Its performance capabilities have allowed me to tackle demanding tasks with ease, making my workflow more efficient. The display quality brings my work to life with vibrant colors and sharp details. While the battery life is decent, I find myself needing to recharge more frequently than I'd like. Overall, the MacBook Pro's blend of power, design, and functionality has made it a valuable addition to my tech arsenal.
            """
        ]
    try:
        res = requests.post(API_URL + 'reviews', params=dict(product=product, rated_criteria=json.dumps(rated_criteria)))
        res.raise_for_status()
        return res.json()
    except requests.RequestException as e:
        st.error(ERROR_MESSAGE_TEMPLATE.format(requested='reviews', error=e))
        return []


# Centered title at the top of the page
st.write("<h1>Intelligent Review Builder with AI 📝</h1>", unsafe_allow_html=True)

# Layout and interaction
col1, col2 = st.columns([1, 2])  # Adjusted column widths

# Left side: Input product and criteria
with col1:
    st.markdown("<div class='left-side'>", unsafe_allow_html=True)
    with st.form('product_form'):
        st.header("Product Name")
        product = st.text_input(label="Enter the product you want to review", value=st.session_state.product, max_chars=100)
        st.session_state.product = product
        if st.form_submit_button("Next"):
            st.session_state.criteria = fetch_criteria(product)
            st.session_state.rated_criteria = {}
            st.session_state.reviews = []

    if st.session_state.criteria:
        with st.form('criteria_form'):
            st.header("Rate Criteria")
            for criterion in st.session_state.criteria:
                st.write(f"### {criterion.capitalize()}")
                st.session_state.rated_criteria[criterion] = st.slider("", 1, 5, 3, key=criterion)
            if st.form_submit_button("Generate Reviews"):
                st.session_state.reviews = fetch_reviews(st.session_state.product, st.session_state.rated_criteria)
    st.markdown("</div>", unsafe_allow_html=True)

# Right side: Display reviews
with col2:
    st.markdown("<div class='right-side'>", unsafe_allow_html=True)

    if st.session_state.reviews:
        st.header("Reviews")
        for i, review in enumerate(st.session_state.reviews):
            st.markdown(f"#### Review #{i+1}")
            st.write(review)
    elif st.session_state.criteria:
        st.write("Write criteria ratings and click 'Generate Reviews' to see results.")
    st.markdown("</div>", unsafe_allow_html=True)
