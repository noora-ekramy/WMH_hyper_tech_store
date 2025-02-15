import os
import json
import streamlit as st

# Define the items directory
ITEMS_DIR = "items"

# List of categories (same as in `admin.py`)
categories = [
    "All", "GPUs", "CPUs", "Motherboards", "RAMs", "Storage (HDDs, SSDs)", "Power Supplies", 
    "Cases", "Cooling Systems (Fans, Liquid Coolers)", "Full PCs", "Laptops", 
    "Monitors", "Keyboards & Mice", "Headsets & Audio",
     "Software & Utilities", "Games", "Combo Deals & Offers", 
    "Fixing & Repair Services"
]

# Function to load all items from the "items" folder
def load_items():
    """Reads all item JSON files and returns a list of items."""
    items = []
    for folder in sorted(os.listdir(ITEMS_DIR), key=lambda x: int(x) if x.isdigit() else float("inf")):
        item_path = os.path.join(ITEMS_DIR, folder, "data.json")
        images_folder = os.path.join(ITEMS_DIR, folder, "images")
        
        if os.path.exists(item_path):
            with open(item_path, "r") as f:
                item_data = json.load(f)
                item_data["folder"] = folder  # Store folder number
                
                # Load images
                if os.path.exists(images_folder):
                    item_data["images"] = [os.path.join(images_folder, img) for img in os.listdir(images_folder) if img.endswith((".jpg", ".png"))]
                else:
                    item_data["images"] = []
                    
                items.append(item_data)
    return items

# Load all items
all_items = load_items()

# Sidebar for categories
st.sidebar.title("🛒 Categories")
selected_category = st.sidebar.radio("Choose a Category", categories)

# Search bar for filtering items
search_query = st.text_input("🔍 Search for products", "")

# Filter items based on selected category
filtered_items = all_items
if selected_category != "All":
    filtered_items = [item for item in all_items if item["category"] == selected_category]

# Apply search filter
if search_query:
    filtered_items = [item for item in filtered_items if search_query.lower() in item["name"].lower() or search_query.lower() in item["description"].lower()]

# Display items in a grid (3 items per row)
st.subheader(f"📌 {selected_category} Products")
cols = st.columns(3)
for i, item in enumerate(filtered_items):
    with cols[i % 3]:
        # Display product card
        if item["images"]:
            st.image(item["images"][0], use_column_width=True)
        st.write(f"**{item['name']}**")

        # Show original price (red, strikethrough) and final price (green, bold)
        st.markdown(f"""
            <p style="color:red; text-decoration: line-through; font-size:16px;">
                {item['price']} EGP
            </p>
            <p style="color:green; font-size:18px; font-weight:bold;">
                💰 {item['final_price']} EGP
            </p>
        """, unsafe_allow_html=True)

        # Show discount percentage if applicable
        if item["discount_percentage"] > 0:
            st.write(f"🔥 {item['discount_percentage']}% off!")

        # Ensure unique key by adding loop index (i)
        if st.button(f"View Details", key=f"details_{item['id']}_{i}"):
            st.session_state.selected_item = item
            st.session_state.show_details = True
            st.rerun()

# Handle item details popup
if "show_details" in st.session_state and st.session_state.show_details:
    item = st.session_state.selected_item

    st.markdown("---")
    st.header(f"🛍️ {item['name']}")
    st.write(f"**Category:** {item['category']}")
    st.write(f"**Condition:** {item.get('condition', 'Brand New')}")
    st.write(f"**Description:** {item['description']}")

    # Show original price (red, strikethrough) and final price (green, bold)
    st.markdown(f"""
        <p style="color:red; text-decoration: line-through; font-size:20px;">
            {item['price']} EGP
        </p>
        <p style="color:green; font-size:22px; font-weight:bold;">
            💰 {item['final_price']} EGP
        </p>
    """, unsafe_allow_html=True)

    # Show discount percentage if applicable
    if item["discount_percentage"] > 0:
        st.write(f"🔥 {item['discount_percentage']}% off!")

    # Display images in a slider
    if item["images"]:
        st.image(item["images"], width=400, caption=[f"Image {i+1}" for i in range(len(item["images"]))])

    # Close button
    if st.button("Close"):
        st.session_state.show_details = False
        st.rerun()
