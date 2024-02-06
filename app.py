import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Set page configuration
st.set_page_config(page_title="NDIS Smart Contract Interaction App", page_icon=":rocket:")

# Load environment variables
load_dotenv()
web3_provider = os.getenv("WEB3_PROVIDER_URI")
smart_contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

if not web3_provider or not smart_contract_address:
    st.error("Please set the environment variables WEB3_PROVIDER_URI and SMART_CONTRACT_ADDRESS.")
    st.stop()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(web3_provider))

# Define the SessionState class
class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

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

# Load the contract
contract = connect_to_contract()

# Streamlit app
def main():
    st.title("NDIS Smart Contract Interface")
    display_contract_details()
    display_withdrawal_requests()

# Function to display contract details
def display_contract_details():
    st.subheader("Contract Details")
    st.write(f"NDIA Address: {contract.functions.ndia().call()}")
    st.write(f"Participant Address: {contract.functions.ndisParticipant().call()}")
    st.write(f"Service Provider Address: {contract.functions.ndisServiceProvider().call()}")
    st.write(f"Participant Funds: {contract.functions.participantFunds().call()} wei")

# Function to display withdrawal requests
def display_withdrawal_requests():
    st.subheader("Withdrawal Requests")
    withdrawal_requests = contract.functions.getWithdrawalRequests(contract.functions.ndisParticipant().call()).call()

    if withdrawal_requests[0] != "0x0000000000000000000000000000000000000000":
        st.write("Withdrawal Request:")
        st.write(f"Requester: {withdrawal_requests[0]}")
        st.write(f"Amount: {withdrawal_requests[1]} wei")
        st.write(f"Participant UNID Number: {withdrawal_requests[2]}")
        st.write(f"Description: {withdrawal_requests[3]}")
        st.write(f"Approved: {withdrawal_requests[4]}")
    else:
        st.write("No pending withdrawal requests.")

# Main Streamlit app
if __name__ == "__main__":
    with st.sidebar:
        st.markdown("## Ethereum Node Configuration")
        web3_provider = st.text_input("Web3 Provider URL", "http://localhost:8545")

    with st.spinner("Connecting to Ethereum node..."):
        web3 = Web3(Web3.HTTPProvider(web3_provider))
        if web3.isConnected():
            st.success("Connected to Ethereum node")
            main()
        else:
            st.error("Failed to connect to Ethereum node. Please check the Web3 Provider URL.")
