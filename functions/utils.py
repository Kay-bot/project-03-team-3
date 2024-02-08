# Import libraries
import streamlit as st
from itertools import count

# Import function from contract
from functions.contract import connect_to_contract

counter_generator = count(start=1)

contract = connect_to_contract()

def display_booking_requests():
    st.subheader("Booking Requests Viewer")

    requests = contract.functions.getBookingRequests().call()

    pending_requests = []

    for request in requests:
        participant_address, amount, participant_unique_id, service_description, status = request

        # Only display requests with status 0
        if status == 0:
            pending_requests.append({
                "Participant Address": participant_address,
                "Service Description": service_description,
                "Amount": amount,
                "Status:" : "Pending"
            })      
    
    # Display the table if there are pending requests
    if pending_requests:
        st.table(pending_requests)
    else:
        st.write("No pending booking requests.")  

    st.write("----")    


def service_request_lookup():
    st.subheader("Request ID look up")
    # Retrieve all service requests 
    service_request_filter = contract.events.ServiceBooked.createFilter(
        fromBlock=0
    )
   
    all_booking_requests = service_request_filter.get_all_entries()
   
    participant_address = st.text_input("Participant Provider Address*:")
   
    for request_entry in all_booking_requests:
        if participant_address == request_entry['args']['participant']:
            request_id = request_entry['args']['requestId'].hex()
            service_description = request_entry['args']['serviceDescription']
            amount = request_entry['args']['amount']

            st.write(f"Request ID: {request_id}")
            st.write(f"Participant Address: {participant_address}")
            st.write(f"Service Description: {service_description}")
            st.write(f"Amount: {amount}")
            st.write("------------")   
    st.write("----")

def booking_requests():
    st.subheader("Book A Service")

    # Input form
    account_address = st.text_input("Enter Account Address:")
     # Define the list of service options
    service_options = {
        "Support Coordination": 2000,
        "Core Supports": 3000,
        "Capacity Building Supports": 4000,
        "Assistive Technology": 1000,
        "Home Modifications": 10000,
        "Therapeutic Supports": 2000,
        "Transport Supports": 2500,
        "Specialist Disability Accommodation (SDA)": 30000,
        "Early Childhood Early Intervention (ECEI)": 15000,
        "Reasonable and Necessary Supports": 20000
    }
        
     # Dropdown to select a service option
    selected_option_name = st.selectbox("Select a Service Option", list(service_options.keys()))
    selected_option_value = service_options[selected_option_name]

    if account_address: 
        try:
            
            requester_address = account_address

            if st.button("Book"):
                try:
                    tx_hash = contract.functions.bookService(selected_option_name, selected_option_value, account_address).transact({'from': requester_address})
                    st.success(f"Withdrawal request initiated successfully! Transaction Hash: {tx_hash.hex()}")
                    # Refresh withdrawal requests after initiation
                    display_booking_requests()
                except Exception as e:
                    st.error(f"Failed to initiate withdrawal request. Error: {e}")

        except ValueError:
            st.error("Invalid input. Please enter a valid integer for the Ethereum account index.") 

