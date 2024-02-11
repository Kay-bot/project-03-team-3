# Import libraries
import streamlit as st
from itertools import count

# Import function from contract
from functions.contract import connect_to_contract

counter_generator = count(start=1)

contract = connect_to_contract()
       
def offer_service():
    st.subheader("Offer Service Booking")

    service_provider_address = st.text_input("Service Provider Address*:")
    request_id = st.text_input("Select Request ID:" )
    service_description = st.text_input("Service Description")
    
    offer_button = st.button("Offer Service")

    if offer_button:
        try:
            with st.spinner("Offering service..."):
                # Call the contract function to offer the service
                tx_hash = contract.functions.offerService(service_provider_address, request_id, service_description).transact({'from': service_provider_address})
            
            st.success(f"Service offered! Transaction Hash: {tx_hash.hex()}")
            
            # Trigger a rerun to update the UI
            st.experimental_rerun()

        except ValueError as ve:
            st.error(f"Failed to offer service. Invalid input. Error: {ve}")
        except TimeoutError as te:
            st.error(f"Failed to offer service. Transaction timed out. Error: {te}")
        except Exception as e:
            st.error(f"Failed to offer service. Unknown error. Error: {e}")  
            
def initiate_withdrawal_request():
    st.subheader("Initiate Withdrawal Request")

    address = st.text_input("Enter Withdrawer Account Address:")
    
    # Retrieve all service requests
    service_request_filter = contract.events.ServiceOffered.createFilter(fromBlock="latest")
    service_requests = [entry['args'] for entry in service_request_filter.get_all_entries() if entry['args']['status'] == 1]  # 1 corresponds to RequestStatus.ServiceOffered
    amount = st.number_input("Enter amount in wei:", min_value=0, step=1)
    request_id = st.selectbox("Select Request ID:", ["0x" + entry['requestId'].hex() for entry in service_requests], key=f"select_request_{address}")
    
    initiate_button = st.button("Initiate Withdrawal Request")

    if initiate_button:
        try:
            with st.spinner("Initiating withdrawal request..."):
                # Call the contract function to initiate the withdrawal request
                tx_hash = contract.functions.initiateWithdrawalRequest(request_id, amount).transact({'from': address})
            
            st.success(f"Withdrawal request initiated! Transaction Hash: {tx_hash.hex()}")
            
            # Trigger a rerun to update the UI
            st.experimental_rerun()

        except ValueError as ve:
            st.error(f"Failed to initiate withdrawal request. Invalid input. Error: {ve}")
        except TimeoutError as te:
            st.error(f"Failed to initiate withdrawal request. Transaction timed out. Error: {te}")
        except Exception as e:
            st.error(f"Failed to initiate withdrawal request. Unknown error. Error: {e}")


def display_service_offered():
    st.subheader("Offer Requests Viewer")

    requests = contract.functions.getBookingRequests().call()

    pending_requests = []

    for request in requests:
        job_number, participant_address, amount, participant_unique_id, service_description, status = request

        # Only display requests with status 0
        if status == 1:
            pending_requests.append({
                "Job Number": job_number,
                "Participant Address": participant_address,
                "Service Description": service_description,
                "Amount": amount,
                "Status:" : "Service Offerred"
            })      
    
    # Display the table if there are pending requests
    if pending_requests:
        st.table(pending_requests)
    else:
        st.write("No pending booking requests.")  

    st.write("----")    
