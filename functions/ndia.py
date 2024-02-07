# Import libraries
import streamlit as st
from web3 import Web3

# Import function from contract
from functions.contract import connect_to_contract

contract = connect_to_contract()

# Function to display contract details
def display_contract_details():
    st.subheader("Contract Details")
    st.write(f"NDIA Address: {contract.functions.ndia().call()}")
    st.write(f"Participant Funds: {contract.functions.participantFunds().call()} wei")
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