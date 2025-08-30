import os

import requests
import streamlit as st

def get_api_response(question, session_id):
    """
    Send a chat request to the RAG API.

    Args:
        question (str): The user's question to send to the API.
        session_id (str): Optional session ID for conversation continuity.

    Returns:
        dict: API response as JSON, or None if request fails.
    """
    headers = {
        'accept': 'application/json'
    }
    params = {
        "request": question,
    }
    if session_id:
        params["session_id"] = session_id

    try:
        response = requests.post(f"http://{os.getenv("APP_HOST", "localhost")}:{os.getenv("APP_PORT", "8000")}/api/v1/rag/chat", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def upload_document(file):
    print("Uploading file...")

    try:
        files = {"file": (file.name, file, file.type)}

        response = requests.post(f"http://{os.getenv("APP_HOST", "localhost")}:{os.getenv("APP_PORT", "8000")}//api/v1/rag/store_document", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to upload file. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while uploading the file: {str(e)}")
        return None

def list_documents():
    st.error(f"Not implemented yet")
    return None
    try:
        response = requests.get("http://localhost:8000/list-docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document list. Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"An error occurred while fetching the document list: {str(e)}")
        return []

def delete_document(file_id):
    st.error(f"Not implemented yet")
    return None
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {"file_id": file_id}

    try:
        response = requests.post("http://localhost:8000/delete-doc", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to delete document. Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"An error occurred while deleting the document: {str(e)}")
        return None