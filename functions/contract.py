import os
import json
from web3 import Web3
from pathlib import Path
import streamlit as st

from functions.config import WEB3_PROVIDER_URI, SMART_CONTRACT_ADDRESS

if not WEB3_PROVIDER_URI or not SMART_CONTRACT_ADDRESS:
    st.error("Please set the environment variables WEB3_PROVIDER_URI and SMART_CONTRACT_ADDRESS.")
    st.stop()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

# Define the load_contract function
def connect_to_contract():
    try:
        # Load NDIS Contracts ABI
        with open(Path('./contracts/compiled/ndis_smart_contract.json')) as f:
            ndis_smart_contract_abi = json.load(f)
    except FileNotFoundError:
        st.error("Smart contract ABI file not found. Please ensure the file path is correct.")
        st.stop()

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=ndis_smart_contract_abi
    )
    # Return the contract from the function
    return contract