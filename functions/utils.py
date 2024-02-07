# Import libraries
import streamlit as st
from itertools import count

# Import function from contract
from functions.contract import connect_to_contract

counter_generator = count(start=1)

contract = connect_to_contract()

# Function to display withdrawal requests
def display_withdrawal_requests():
    st.subheader("Withdrawal Requests Viewer")
    
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

def display_booking_requests():
    st.subheader("Booking Requests Viewer")

    # Retrieve all service requests 
    service_requests = contract.functions.getBookingRequests().call()

    # Check if there are no service requests
    if not service_requests:
        st.write("No service requests at the moment...")
        return

    pending_requests_exist = False

    for request in service_requests:
        address, service, is_offered = request

        # Skip displaying if service is already offered
        if is_offered:
            continue

        pending_requests_exist = True

        st.write(f"Participant Address: {address}")
        st.write(f"Service Required: {service}")
        st.write(f"Offered: {is_offered}")

        provider_address = st.text_input("Service Provider Address*:")

        unique_counter = next(counter_generator)
        approval_button_key = f"offer_button_{address}_{unique_counter}"

        offer_service_button = st.button("Offer Service", key=approval_button_key)
            
        if offer_service_button:
            
            try:
                # Disable the button after click
                with st.spinner("Offering service..."):
                    tx_hash = contract.functions.offerService(address).transact({'from': provider_address})
                st.success(f"Service offered! Transaction Hash: {tx_hash.hex()}")
                
                # Trigger a rerun to update the UI
                st.experimental_rerun()

            except Exception as e:
                st.error(f"Failed to offer service. Error: {e}")

        st.write("----")

    if not pending_requests_exist:
        st.write("No pending service requests at the moment...")  

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


def booking_requests():
    st.subheader("Book A Service")

    # Input form
    account_address = st.text_input("Enter Account Address:")
     # Define the list of service options
    service_options = [
        "Support Coordination",
        "Core Supports",
        "Capacity Building Supports",
        "Assistive Technology",
        "Home Modifications",
        "Therapeutic Supports",
        "Transport Supports",
        "Specialist Disability Accommodation (SDA)",
        "Early Childhood Early Intervention (ECEI)",
        "Reasonable and Necessary Supports"
    ]

    # Dropdown to select a service option
    selected_option = st.selectbox("Select a Service Option", service_options)

    if account_address: 
        try:
            
            requester_address = account_address

            if st.button("Book"):
                try:
                    tx_hash = contract.functions.bookService(selected_option).transact({'from': requester_address})
                    st.success(f"Withdrawal request initiated successfully! Transaction Hash: {tx_hash.hex()}")
                    # Refresh withdrawal requests after initiation
                    display_booking_requests()
                except Exception as e:
                    st.error(f"Failed to initiate withdrawal request. Error: {e}")

        except ValueError:
            st.error("Invalid input. Please enter a valid integer for the Ethereum account index.") 


#Helper function to  iterates through service rendered
def iterate_and_display(service_rendered):
    for index, attr_dict_str in enumerate(service_rendered):
        try:
            participant_address = attr_dict_str.args.participant
            service_provider_address = attr_dict_str.args.serviceProvider
            service_description = attr_dict_str.args.serviceDescription

            st.write(f"Participant Address: {participant_address}")
            st.write(f"Service Provider Address: {service_provider_address}")
            st.write(f"Service Description: {service_description}")

            # Button to confirm service rendered
            unique_counter = next(counter_generator)
            button_key = f"action_button_{index}_{unique_counter}"
            action_button = st.button("Confirm", key=button_key)

            st.write("----")

            if action_button:
                with st.spinner("Confirming service rendered....."):
                    tx_hash = contract.functions.confirmServiceRendered(service_description, service_provider_address).transact({'from':participant_address})
                st.success(f"Service offered! Transaction Hash: {tx_hash.hex()}")

                # Trigger a rerun to update the UI
                st.experimental_rerun()

        except Exception as e:
            st.warning(f"Error processing AttributeDict at index {index}: {e}")
            st.write("----")   