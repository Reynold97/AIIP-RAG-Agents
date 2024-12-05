import streamlit as st
from typing import Optional

def show_status_message(
    message: str,
    type: str = "info",
    duration: Optional[int] = None,
    key: Optional[str] = None
):
    """
    Display a status message using Streamlit.
    
    Args:
        message: Message to display
        type: Type of message (success, error, warning, info)
        duration: Duration to show message in seconds
        key: Unique key for the message
    """
    if type == "success":
        st.success(message, icon="✅")
    elif type == "error":
        st.error(message, icon="🚨")
    elif type == "warning":
        st.warning(message, icon="⚠️")
    else:
        st.info(message, icon="ℹ️")
        
    if duration:
        st.empty().success(message)
        time.sleep(duration)
        st.empty()

def show_operation_status(operation_name: str, success: bool = True):
    """
    Show operation status with appropriate styling.
    
    Args:
        operation_name: Name of the operation
        success: Whether operation was successful
    """
    if success:
        st.success(f"{operation_name} completed successfully!", icon="✅")
    else:
        st.error(f"{operation_name} failed. Please try again.", icon="🚨")