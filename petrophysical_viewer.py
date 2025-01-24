import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import lasio
import plotly.express as px
import numpy as np
import fitz  # PyMuPDF for handling PDF files
import io
from PIL import Image
# App title and description
st.title("Advanced Petrophysical Data Viewer")
st.write("Analyze petrophysical data with enhanced visualization and interactivity.")
# Sidebar for file uploads
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader(
   "Upload your petrophysical data file (CSV, LAS, PNG, PDF)",
   type=["csv", "las", "png", "pdf"]
)
# If a file is uploaded
if uploaded_file:
   file_type = uploaded_file.name.split('.')[-1]
   # Process CSV files
   if file_type == 'csv':
       data = pd.read_csv(uploaded_file)
       st.subheader("CSV Data Preview")
       st.dataframe(data)
       # Depth range slider
       depth_col = st.selectbox("Select Depth Column:", data.columns)
       min_depth, max_depth = st.slider(
           "Select Depth Range:",
           min_value=float(data[depth_col].min()),
           max_value=float(data[depth_col].max()),
           value=(float(data[depth_col].min()), float(data[depth_col].max()))
       )
       filtered_data = data[(data[depth_col] >= min_depth) & (data[depth_col] <= max_depth)]
       # Dropdown for properties
       property_col = st.selectbox("Select Property Column to Plot:", [col for col in data.columns if col != depth_col])
       # Depth vs Property Log with Color Scale
       st.subheader(f"{property_col} vs. {depth_col} with Color Scale")
       fig = px.scatter(
           filtered_data, x=property_col, y=depth_col,
           color=property_col, color_continuous_scale="Viridis",
           labels={depth_col: "Depth", property_col: property_col}
       )
       fig.update_layout(yaxis=dict(autorange="reversed"))
       st.plotly_chart(fig)
       # Histogram for Property Distribution
       st.subheader(f"Histogram of {property_col}")
       fig = px.histogram(filtered_data, x=property_col, nbins=50, title=f"Distribution of {property_col}")
       st.plotly_chart(fig)
       # Option to download filtered dataset
       st.sidebar.download_button(
           label="Download Filtered Data",
           data=filtered_data.to_csv(index=False),
           file_name="filtered_data.csv",
           mime="text/csv"
       )
   # Process LAS files
   elif file_type == 'las':
       las = lasio.read(uploaded_file)
       st.subheader("LAS File Data")
       st.text(las)
       las_df = las.df()
       st.write("**Preview of LAS Data:**")
       st.dataframe(las_df)
       # Depth range slider
       min_depth, max_depth = st.slider(
           "Select Depth Range:",
           min_value=float(las_df.index.min()),
           max_value=float(las_df.index.max()),
           value=(float(las_df.index.min()), float(las_df.index.max()))
       )
       filtered_las_df = las_df[(las_df.index >= min_depth) & (las_df.index <= max_depth)]
       # Plot Depth vs Log Property
       log_col = st.selectbox("Select Log Property to Plot:", las_df.columns)
       st.subheader(f"{log_col} vs. Depth with Zoom and Pan")
       fig = px.scatter(
           filtered_las_df, x=log_col, y=filtered_las_df.index,
           color=log_col, color_continuous_scale="Plasma",
           labels={"index": "Depth", log_col: log_col}
       )
       fig.update_layout(yaxis=dict(autorange="reversed"))
       st.plotly_chart(fig)
       # Histogram for Log Property
       st.subheader(f"Histogram of {log_col}")
       fig = px.histogram(filtered_las_df, x=log_col, nbins=50, title=f"Distribution of {log_col}")
       st.plotly_chart(fig)
       # Option to download filtered LAS data
       st.sidebar.download_button(
           label="Download Filtered LAS Data",
           data=filtered_las_df.to_csv(),
           file_name="filtered_las_data.csv",
           mime="text/csv"
       )
   # Process PNG files
   elif file_type == 'png':
       st.subheader("Log Image")
       st.image(uploaded_file, caption="Uploaded Log Image", use_column_width=True)
   # Process PDF files
   elif file_type == 'pdf':
       st.subheader("PDF Content")
       # Read the uploaded PDF file
       doc = fitz.open(uploaded_file)
       full_text = ""
       images = []
       # Extract text and images from each page of the PDF
       for page_num in range(len(doc)):
           page = doc.load_page(page_num)
           full_text += page.get_text()
           # Extract images from the page
           for img in page.get_images(full=True):
               xref = img[0]
               image = doc.extract_image(xref)
               image_bytes = image["image"]
               # Convert image to PIL format for display
               pil_image = Image.open(io.BytesIO(image_bytes))
               images.append(pil_image)
       # Display the extracted text
       st.text_area("Extracted PDF Text", full_text, height=300)
       # Display images extracted from PDF
       if images:
           st.subheader("Extracted Images from PDF")
           for img in images:
               st.image(img, caption="Extracted Image", use_column_width=True)
else:
   st.info("Please upload a file to begin.")
# Footer
st.write("Developed by Navneet Srivastav")