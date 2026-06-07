"""
Streamlit Utilities - Helper functions for improved UX
"""

import streamlit as st
from typing import Callable, Any
import time

def show_error(message: str, icon="❌"):
    """Display formatted error message"""
    st.error(f"{icon} {message}")

def show_success(message: str, icon="✅"):
    """Display formatted success message"""
    st.success(f"{icon} {message}")

def show_info(message: str, icon="ℹ️"):
    """Display formatted info message"""
    st.info(f"{icon} {message}")

def show_warning(message: str, icon="⚠️"):
    """Display formatted warning message"""
    st.warning(f"{icon} {message}")

def with_retry(func: Callable, max_retries: int = 3) -> Any:
    """Retry failed API calls"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

def confirmation_dialog(title: str, message: str) -> bool:
    """Show confirmation dialog"""
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm", use_container_width=True):
            return True
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            return False
    return False

def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"

def format_date(date_str: str) -> str:
    """Format date string"""
    if date_str and 'T' in date_str:
        return date_str.split('T')[0]
    return date_str or 'N/A'

class APIResponseHandler:
    """Centralized API response handling"""
    
    @staticmethod
    def handle_success(response, message="Operation successful"):
        show_success(message)
        st.balloons()
        return response
    
    @staticmethod
    def handle_error(error_message):
        show_error(error_message)
        return None
    
    @staticmethod
    def handle_loading(message="Processing..."):
        with st.spinner(message):
            yield
