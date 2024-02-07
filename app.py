# Import libraries
from web3 import Web3
import streamlit as st

# import config
from functions.config import WEB3_PROVIDER_URI

# Import function from contract module
from functions.contract import connect_to_contract
# Import functions from ndia module
from functions.ndia import (
    display_contract_details,
    deposit_funds,
    register_account
)

# Import functions from utils module
from functions.utils import (
    display_withdrawal_requests,
    display_booking_requests,
    initiate_withdrawal_request,
    booking_requests
)

# Set page configuration
st.set_page_config(page_title="NDIS Smart Contract Interaction App", page_icon=":rocket:")

# Load the contract
contract = connect_to_contract()

# Streamlit app
def main():
    page = st.sidebar.selectbox("Select Page", ["NDIA", "Participants", "ServiceProviders"])
    
    if page == "NDIA":
        display_contract_details()
        deposit_funds()
        register_account()
        display_withdrawal_requests()
    elif page == "Participants":
        booking_requests() 
    elif page == "ServiceProviders":
        display_booking_requests()
        initiate_withdrawal_request()

# Main Streamlit app
if __name__ == "__main__":
    with st.sidebar:
        st.markdown("## Ethereum Node Configuration")

    with st.spinner("Connecting to Ethereum node..."):
        web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
        if web3.isConnected():
            st.success("Connected to Ethereum node")
            main()
        else:
            st.error("Failed to connect to Ethereum node. Please check the Web3 Provider URL.")
