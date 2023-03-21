import pandas as pd
import streamlit as st
import numpy as np
import base64

# Define a function to process the uploaded file
def process_file(file):
    au = pd.read_excel(file, sheet_name='Sheet1', parse_dates=['Invoice Date']).dropna(subset=['GSTIN of supplier'])
    pr = pd.read_excel(file, sheet_name='Sheet2', parse_dates=['Date'])
    for d in [au, pr]:
        d.columns = ['GSTIN', 'Invoice No', 'Date', 'IGST', 'CGST', 'SGST']
        d = d.groupby(['GSTIN', 'Date']).sum().reset_index().copy()
    df = pd.merge(au, pr, on=['GSTIN', 'Date'], how='outer')
    df['Flag'] = np.where(df['IGST_x'].isnull()&df['CGST_x'].isnull()&df['SGST_x'].isnull(),
                      1, 0)
    final = df[df['Flag']==1].drop(['IGST_x', 'CGST_x', 'SGST_x'], 1).copy()
    final.rename({'IGST_y':'IGST', 'CGST_y':'CGST', 'SGST_y':'SGST'}, inplace=True)
    final['Flag'].replace({1:'Not Found in 2A'}, inplace=True)
    # pr = pr.groupby(['GSTIN', 'Date']).sum().reset_index().copy()
    # au = au.groupby(['GSTIN', 'Date']).sum().reset_index().copy()
    return final

# Set up the Streamlit app
st.title('GST DOC 2.0')

# Create a file uploader widget
uploaded_file = st.file_uploader('Upload an Excel file with GST 2A and ITC', type=['xlsx'])

# Process the uploaded file and display the first few rows as a sample
if uploaded_file is not None:
    # Call the process_file function
    df = process_file(uploaded_file)

    # Display the first few rows of the processed DataFrame as a sample
    st.write('processed data:')
    st.write(df)

    # Create a download link for the processed file
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="processed_file.csv">Download the processed file</a>'
    st.markdown(href, unsafe_allow_html=True)
