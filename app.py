# Import libraries
import os
from web3 import Web3
import streamlit as st

# Import functions
from functions.ndia import (
    display_contract_details, 
    deposit_funds, 
    register_account,
    display_withdrawal_requests, 
    approve_withdrawal
)
from functions.utils import (
    display_booking_requests, 
    booking_requests, 
    service_request_lookup
)

from functions.provider import (
    offer_service,
    initiate_withdrawal_request,
    display_service_offered
)

from dotenv import load_dotenv

load_dotenv()

# Set page configuration
st.set_page_config(page_title="NDIS Smart Contract Interaction App", page_icon=":rocket:")

# Streamlit app
def main():
    
    page = st.sidebar.selectbox("Select Page", ["NDIA", "Participants", "ServiceProviders"])
    
    if page == "NDIA":
        display_contract_details()
        deposit_funds()
        register_account()
        display_withdrawal_requests()
        approve_withdrawal()
    elif page == "Participants":
        booking_requests() 
    elif page == "ServiceProviders":
        display_booking_requests()
        offer_service()
        display_service_offered()
        service_request_lookup()
        initiate_withdrawal_request()

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.experimental_rerun()
        
# Main Streamlit app
if __name__ == "__main__":
    with st.sidebar:
        st.markdown("## Ethereum Node Configuration")

    with st.spinner("Connecting to Ethereum node..."):
        web3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
        if web3.isConnected():
            st.success("Connected to Ethereum node")
            main()
        else:
            st.error("Failed to connect to Ethereum node. Please check the Web3 Provider URL.")
