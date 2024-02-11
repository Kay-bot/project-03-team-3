# Import libraries
import os
import streamlit as st
from web3 import Web3

from dotenv import load_dotenv

load_dotenv()

# Import function from contract
from functions.contract import connect_to_contract

contract = connect_to_contract()

account_address = os.getenv("NDIA")

# Function to display contract details
def display_contract_details():
    st.subheader("Contract Details")
    st.write(f"NDIA Address: {contract.functions.ndia().call()}")
    st.write(f"Participant Funds: {contract.functions.participantFunds().call()} wei")

    st.write("----") 
# Function to deposit funds by NDIA
def deposit_funds():
    st.subheader("Deposit Funds (NDIA Only)")

    # Input form
    deposit_amount = st.number_input("Enter deposit amount in wei:", min_value=0, step=1)
    

    if account_address:
        try:
            ndia_address = account_address

            if st.button("Deposit Funds"):
                # Check if the entered address is the NDIA address
                is_ndia = contract.functions.ndia().call() == ndia_address
                if not is_ndia:
                    st.error("Invalid NDIA address. Please provide the correct NDIA address.")
                    return

                tx_hash = contract.functions.deposit().transact({'from': ndia_address, 'value': deposit_amount})
                st.success(f"Deposit successful! Transaction Hash: {tx_hash.hex()}")
                # Refresh contract details after deposit
                display_contract_details()
        except Exception as e:
            st.error(f"Failed to deposit funds. Error: {e}")
    st.write("----")  


# Function to register participant and service provider accounts by NDIA
def register_account():
    st.subheader("Register Account")

    # Input form
    account_address = st.text_input("Enter Participant/ServiceProvider Address:", key="account_address")
    is_participant_account = True if st.checkbox("Register as a Participant Account") else False

    if account_address:
     
        try:
            # Button to execute the function
            if st.button("Register Account"):

                # Check if the entered address is the NDIA address
                is_ndia = contract.functions.ndia().call() == account_address
                if not is_ndia:
                    st.error("Invalid NDIA address. Please provide the correct NDIA address.")
                    return

                # Convert input values
                account_address = Web3.toChecksumAddress(account_address)

                # Check if the account is already registered
                if contract.functions.ndisParticipant(account_address).call() or \
                        contract.functions.ndisServiceProvider(account_address).call():
                    st.error("Account already registered.")
                else:
                    # Execute the Solidity function with onlyNDIA modifier
                    contract.functions.registerAccount(account_address, is_participant_account).transact({'from': account_address})

                    st.success("Account registered successfully.")
        except Exception as e:
            st.error(f"Error: {e}")
    st.write("----")       

def approve_withdrawal():
        st.subheader("Approve Withdrawal Request")
        
        # Retrieve all withdrawal requests
        withdrawal_request_filter = contract.events.WithdrawalRequestInitiated.createFilter(fromBlock="latest")
        all_withdrawal_requests = withdrawal_request_filter.get_all_entries()
        
        request_id = st.selectbox("Select Request ID:", [entry['args']['requestId'].hex() for entry in all_withdrawal_requests])
        
        approve_button = st.button("Approve Withdrawal")

        if approve_button:
            try:
                with st.spinner("Approving withdrawal..."):
                    # Call the contract function to approve the withdrawal
                    tx_hash = contract.functions.approveWithdrawal(bytes.fromhex(request_id)).transact({'from': account_address})
                
                st.success(f"Withdrawal request approved! Transaction Hash: {tx_hash.hex()}")
                
                # Trigger a rerun to update the UI
                st.experimental_rerun()

            except ValueError as ve:
                st.error(f"Failed to approve withdrawal. Invalid input. Error: {ve}")
            except TimeoutError as te:
                st.error(f"Failed to approve withdrawal. Transaction timed out. Error: {te}")
            except Exception as e:
                st.error(f"Failed to approve withdrawal. Unknown error. Error: {e}")   
        st.write("----")        

# Function to display withdrawal requests
def display_withdrawal_requests():
    st.subheader("Withdrawal Requests Viewer")
    
    # Retrieve all withdrawal requests from events
    withdrawal_request_filter = contract.events.WithdrawalRequestInitiated.createFilter(
        fromBlock=0
    )
    all_withdrawal_requests = withdrawal_request_filter.get_all_entries()

    requests = contract.functions.getBookingRequests().call()

    pending_requests = []

    for request in requests:
        address, amount, participant_unique_id, service_description, status = request

        # Only display requests with status 0
        if status == 2:
            pending_requests.append({
                "Recipient": address,
                "Service Description": service_description,
                "Amount": amount,
                "Status:" : "Wating for Approval"
            })      
    
    # Display the table if there are pending requests
    if pending_requests:
        st.table(pending_requests)
    else:
        st.write("No pending booking requests.")  

    st.write("----")    
    
   
