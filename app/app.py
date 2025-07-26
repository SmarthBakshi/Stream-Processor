import streamlit as st
import os

st.set_page_config(page_title="Football Stream Processor", layout="wide")

st.sidebar.title("📂 Menu")
page = st.sidebar.radio("Go to", [
    "📊 EDA & Visualizations",
    "🤖 Model Results",
    "⚽ Match Simulation",
    "ℹ️ About"
])

if page == "📊 EDA & Visualizations":
    st.title("📊 EDA & Data Visualizations")
    plot_folder = "resources/plots"
    if os.path.exists(plot_folder):
        for file in os.listdir(plot_folder):
            if file.endswith(".png"):
                st.image(os.path.join(plot_folder, file), use_column_width=True)
    else:
        st.warning("No plots found in resources/plots!")

elif page == "🤖 Model Results":
    st.title("🤖 Model Performance")
    st.metric("Best Accuracy", "0.84")
    st.write("Best Hyperparameters:")
    st.json({
        "learning_rate": 0.01,
        "max_depth": 5,
        "n_estimators": 100
    })

elif page == "⚽ Match Simulation":
    st.title("⚽ Simulate a Match")
    uploaded_file = st.file_uploader("Upload a match JSON file", type="json")
    
    if uploaded_file:
        st.success("Match file uploaded!")
        
        # Read file content
        match_json = json.load(uploaded_file) # TODO: Implement a way where user selects the match file from a list of available matches
        
        # Run simulation
        with st.spinner("Simulating..."):
            try:
                results = simulate_match(match_json)
                st.subheader("📋 Simulation Results")
                st.json(results)
            except Exception as e:
                st.error(f"❌ Simulation failed: {e}")
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")
    st.markdown("""
    **Football Stream Processor**  
    - ML pipeline with Optuna tuning  
    - Visual analysis with EDA plots  
    - Model tracking via MLFlow  
    - Fully containerized with Docker + CI/CD  
    """)
    st.markdown("[🔗 View GitHub Repository](https://github.com/yourusername/yourrepo)")
