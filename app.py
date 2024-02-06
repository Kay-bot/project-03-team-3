import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from itertools import count

counter_generator = count(start=1)

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
    page = st.sidebar.selectbox("Select Page", ["NDIA", "Participant/ServiceProvider"])
    
    if page == "NDIA":
        display_contract_details()
        deposit_funds()
        register_account()
        display_withdrawal_requests()
    elif page == "Participant/ServiceProvider":
        initiate_withdrawal_request()


# Function to display contract details
def display_contract_details():
    st.subheader("Contract Details")
    st.write(f"NDIA Address: {contract.functions.ndia().call()}")
    st.write(f"Participant Funds: {contract.functions.participantFunds().call()} wei")

# Function to display withdrawal requests
def display_withdrawal_requests():
    
    # Retrieve all withdrawal requests from blockchain
    withdrawal_requests = contract.functions.getWithdrawalRequests().call()
    
    # Check if there are no withdrawal requests
    if not withdrawal_requests:
        st.write("No pending withdrawal requests.")
        return

    # Loop through the filtered list for display
    for request in withdrawal_requests:
        # Check if the withdrawal request is not approved
        if not request[4]:
            st.write("Withdrawal Request:")
            st.write(f"Requester: {request[0]}")
            st.write(f"Amount: {request[1]} wei")
            st.write(f"Participant UNID Number: {request[2]}")
            st.write(f"Description: {request[3]}")
            st.write(f"Approved: {request[4]}")

            unique_counter = next(counter_generator)
            approval_button_key = f"approve_button_{request[0]}_{request[2]}_{unique_counter}"

            # Display the approval button only if the request is not already approved
            if not request[4]:
                approval_button = st.button(f"Approve Withdrawal for {request[0]}", key=approval_button_key)

                if approval_button:
                    try:
                        # Disable the button after click
                        with st.spinner("Approving withdrawal..."):
                            tx_hash = contract.functions.approveWithdrawal(request[0]).transact({'from': contract.functions.ndia().call()})
                        st.success(f"Withdrawal request approved! Transaction Hash: {tx_hash.hex()}")
                        
                        # Trigger a rerun to update the UI
                        st.experimental_rerun()

                    except Exception as e:
                        st.error(f"Failed to approve withdrawal request. Error: {e}")
            else:
                st.write("Withdrawal already approved.")
            st.write("----")


# Function to deposit funds by NDIA
def deposit_funds():
    st.subheader("Deposit Funds (NDIA Only)")
    deposit_amount = st.number_input("Enter deposit amount in wei:", min_value=0, step=1)

    if st.button("Deposit Funds"):
        try:
            tx_hash = contract.functions.deposit().transact({'from': contract.functions.ndia().call(), 'value': deposit_amount})
            st.success(f"Deposit successful! Transaction Hash: {tx_hash.hex()}")
            # Refresh contract details after deposit
            display_contract_details()
        except Exception as e:
            st.error(f"Failed to deposit funds. Error: {e}")

# Function to register participant and service provider accounts by NDIA
def register_account():
    st.subheader("Register Account")

    # Input form
    account_address = st.text_input("Enter Account Address:")
    is_participant_account = True if st.checkbox("Register as a Participant Account") else False

    # Button to execute the function
    if st.button("Register Account"):
        try:
            # Convert input values
            account_address = Web3.toChecksumAddress(account_address)

            # Check if the account is already registered
            if contract.functions.ndisParticipant(account_address).call() or \
                    contract.functions.ndisServiceProvider(account_address).call():
                st.error("Account already registered.")
            else:
                # Execute the Solidity function with onlyNDIA modifier
                contract.functions.registerAccount(account_address, is_participant_account).transact({'from': contract.functions.ndia().call()})

                st.success("Account registered successfully.")
        except Exception as e:
            st.error(f"Error: {e}")

# Function to initiate withdrawal request by ndisParticipant or ndisServiceProvider
def initiate_withdrawal_request():
    st.subheader("Initiate Withdrawal Request (NDIS Participant or NDIS ServiceProvider)")
    withdrawal_amount = st.number_input("Enter withdrawal amount in wei:", min_value=0, step=1)
    participant_unid_number = st.text_input("Enter participant UNID number:")
    withdrawal_description = st.text_input("Enter withdrawal description:")

    # Get the Ethereum account address based on user input
    address = st.text_input("Enter Account Address:")
    
    if address:  # Check if address has a non-empty value before attempting conversion
        try:

            requester_address = address

            if st.button("Initiate Withdrawal Request"):
                try:
                    tx_hash = contract.functions.initiateWithdrawalRequest(withdrawal_amount, participant_unid_number, withdrawal_description).transact({'from': requester_address})
                    st.success(f"Withdrawal request initiated successfully! Transaction Hash: {tx_hash.hex()}")
                    # Refresh withdrawal requests after initiation
                    display_withdrawal_requests()
                except Exception as e:
                    st.error(f"Failed to initiate withdrawal request. Error: {e}")
    
        except ValueError:
            st.error("Invalid input. Please enter a valid integer for the Ethereum account index.")

    else:
        st.warning("Please enter a valid value for Account Address.")



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
