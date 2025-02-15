import os
import json
import shutil
import streamlit as st

# Define directories
ITEMS_DIR = "items"
ADMIN_PASSWORD = "123456789"

# Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def authenticate(password):
    """Check if password is correct."""
    return password == ADMIN_PASSWORD

if not st.session_state.authenticated:
    st.title("Admin Login")
    password_input = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if authenticate(password_input):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password!")

if st.session_state.authenticated:
    
    # Streamlit Navigation
    st.title("Admin Panel")
    tab = st.sidebar.radio("Navigation", ["Add Item", "Manage Items"])

    # Function to get the next item ID
    def get_next_item_id():
        existing_folders = [int(folder) for folder in os.listdir(ITEMS_DIR) if folder.isdigit()]
        return max(existing_folders, default=0) + 1

    # Function to add an item
    def add_item(name, category, condition, description, price, discount_percentage, image_files):
        item_id = get_next_item_id()
        item_folder = os.path.join(ITEMS_DIR, str(item_id))
        os.makedirs(item_folder, exist_ok=True)

        images_folder = os.path.join(item_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        final_price = round(price - (price * discount_percentage / 100), 2)

        item_data = {
            "id": item_id,
            "name": name,
            "category": category,
            "condition": condition,
            "description": description,
            "price": price,
            "discount_percentage": discount_percentage,
            "final_price": final_price,
            "images": []
        }

        for index, image_file in enumerate(image_files):
            if image_file is not None:
                image_filename = f"img{index + 1}.jpg"
                image_path = os.path.join(images_folder, image_filename)
                with open(image_path, "wb") as f:
                    f.write(image_file.read())
                item_data["images"].append(image_filename)

        item_file_path = os.path.join(item_folder, "data.json")
        with open(item_file_path, "w") as f:
            json.dump(item_data, f, indent=4)

        st.success(f"Item '{name}' added successfully! (ID: {item_id})")

    # Function to get all items
    def get_all_items():
        items = []
        for folder in sorted(os.listdir(ITEMS_DIR), key=lambda x: int(x) if x.isdigit() else float("inf")):
            item_path = os.path.join(ITEMS_DIR, folder, "data.json")
            if os.path.exists(item_path):
                with open(item_path, "r") as f:
                    item_data = json.load(f)
                    item_data["folder"] = folder  # Store folder number
                    items.append(item_data)
        return items

    # Function to update an item
    def update_item(item_id, name, category, condition, description, price, discount_percentage):
        item_folder = os.path.join(ITEMS_DIR, str(item_id))
        item_path = os.path.join(item_folder, "data.json")

        if os.path.exists(item_path):
            with open(item_path, "r") as f:
                item_data = json.load(f)

            final_price = round(price - (price * discount_percentage / 100), 2)

            item_data["name"] = name
            item_data["category"] = category
            item_data["condition"] = condition
            item_data["description"] = description
            item_data["price"] = price
            item_data["discount_percentage"] = discount_percentage
            item_data["final_price"] = final_price

            with open(item_path, "w") as f:
                json.dump(item_data, f, indent=4)
            st.success(f"Item {name} updated successfully!")

    # Function to delete an item
    def delete_item(item_id):
        item_folder = os.path.join(ITEMS_DIR, str(item_id))
        if os.path.exists(item_folder):
            shutil.rmtree(item_folder)
            st.success(f"Item {item_id} deleted successfully!")
            st.rerun()  # 🔥 Refresh after deletion

    # Add Item Page
    if tab == "Add Item":
        st.header("Add New Item")

        name = st.text_input("Item Name")
        category = st.selectbox("Category", [
    "All", "GPUs", "CPUs", "Motherboards", "RAMs", "Storage (HDDs, SSDs)", "Power Supplies", 
    "Cases", "Cooling Systems (Fans, Liquid Coolers)", "Full PCs", "Laptops", 
    "Monitors", "Keyboards & Mice", "Headsets & Audio",
     "Software & Utilities", "Games", "Combo Deals & Offers", 
    "Fixing & Repair Services"
])
        condition = st.selectbox("Condition", ["Brand New", "Like New", "Pre-Owned"])
        description = st.text_area("Description")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        discount_percentage = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, format="%.1f")
        final_price = round(price - (price * discount_percentage / 100), 2)
        st.write(f"💰 **Final Price after Discount:** {final_price} EGP")

        image_files = st.file_uploader("Upload Item Images", type=["png", "jpg"], accept_multiple_files=True)

        if st.button("Add Item"):
            if name and category and description and price > 0 and image_files:
                add_item(name, category, condition, description, price, discount_percentage, image_files)
            else:
                st.warning("Please fill in all fields and upload at least one image.")

    # Manage Items Page
    elif tab == "Manage Items":
        st.header("Manage Items")

        all_items = get_all_items()
        if not all_items:
            st.write("No items available.")
        else:
            item_options = [f"{item['id']} - {item['name']}" for item in all_items]

            if "selected_item" not in st.session_state:
                st.session_state.selected_item = item_options[0] if item_options else None

            selected_item = st.selectbox("Select an item to edit", item_options, 
                                         index=item_options.index(st.session_state.selected_item) if st.session_state.selected_item in item_options else 0)

            if selected_item != st.session_state.selected_item:
                st.session_state.selected_item = selected_item
                st.rerun()

            item_id = int(selected_item.split(" - ")[0])
            item_data = next(item for item in all_items if item["id"] == item_id)

            new_name = st.text_input("Item Name", value=item_data["name"])
            new_category = st.selectbox("Category", [
    "All", "GPUs", "CPUs", "Motherboards", "RAMs", "Storage (HDDs, SSDs)", "Power Supplies", 
    "Cases", "Cooling Systems (Fans, Liquid Coolers)", "Full PCs", "Laptops", 
    "Monitors", "Keyboards & Mice", "Headsets & Audio",
     "Software & Utilities", "Games", "Combo Deals & Offers", 
    "Fixing & Repair Services"
], 
                                        index=[
    "All", "GPUs", "CPUs", "Motherboards", "RAMs", "Storage (HDDs, SSDs)", "Power Supplies", 
    "Cases", "Cooling Systems (Fans, Liquid Coolers)", "Full PCs", "Laptops", 
    "Monitors", "Keyboards & Mice", "Headsets & Audio",
     "Software & Utilities", "Games", "Combo Deals & Offers", 
    "Fixing & Repair Services"
].index(item_data["category"]))
            new_condition = st.selectbox(
                    "Condition", 
                    ["Brand New", "Like New", "Pre-Owned"], 
                    index=["Brand New", "Like New", "Pre-Owned"].index(item_data.get("condition", "Brand New"))  # Default to "Brand New"
                )
            new_description = st.text_area("Description", value=item_data["description"])
            new_price = st.number_input("Price", min_value=0.0, format="%.2f", value=float(item_data["price"]))
            # Get discount percentage with a default value
            new_discount = st.number_input(
                "Discount (%)", 
                min_value=0.0, max_value=100.0, format="%.1f", 
                value=float(item_data.get("discount_percentage", 0.0))  # Default to 0% if missing
            )
            final_price = round(new_price - (new_price * new_discount / 100), 2)

            # Show the final price
            st.write(f"💰 **Final Price after Discount:** {final_price} EGP")

            if st.button("Update Item"):
                update_item(item_id, new_name, new_category, new_condition, new_description, new_price, new_discount)

            if st.button("Delete Item", key=f"delete_{item_id}"):
                delete_item(item_id)

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
