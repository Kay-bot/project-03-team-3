// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title NDISSmartContract
 * @dev A smart contract to manage funds and withdrawals for NDIS (National Disability Insurance Scheme).
 */

contract NDISSmartContract {

    address public ndia; // NDIS Agency's address
    uint public participantFunds;


    // Array to store withdrawal requests
    WithdrawalRequest[] public withdrawalRequests;

    // Struct to represent a withdrawal request
    struct WithdrawalRequest {
        address payable requester;
        uint amount;
        string participantUnidNumber;
        string description;
        bool approved;
    }

    // Array to store service requests
    ServiceRequest[] public ServiceRequests;

    // Struct to represent service request
    struct ServiceRequest {
        address payable requester;
        string serviceDescription;
        bool offeredService;
    }

    // Mapping to store participant and service provider addresses
    mapping(address => bool) public ndisParticipant;
    mapping(address => bool) public ndisServiceProvider;

    // Constructor to set the NDIS Agency's address
    constructor() {
        ndia = msg.sender;
    }

    // Modifier to ensure only NDIS Agency can execute certain functions
    modifier onlyNDIA() {
        require(msg.sender == ndia, "Permission denied: Only NDIS Agency can execute this.");
        _;
    }

    modifier onlyNdisParticipantAndNdisServiceProvider() {
        require(ndisParticipant[msg.sender] || ndisServiceProvider[msg.sender], "Permission denied: Only ndisParticipant or ndisServiceProvider can execute this.");
        _;  // Continue with the execution of the function
    }

    modifier onlyNdisParticipant() {
        require(ndisParticipant[msg.sender], "Permission denied: Only ndisParticipant can execute this.");
        _;  // Continue with the execution of the function
    }

    // Modifier to ensure only service providers can execute certain functions
    modifier onlyServiceProvider() {
        require(ndisServiceProvider[msg.sender], "Permission denied: Only ndisServiceProvider can execute this.");
        _;
    }

    // Event to log withdrawal details
    event Withdrawal(address indexed recipient, uint amount, string participantUnidNumber, string description);
    event WithdrawalRequestInitiated(address indexed recipient, uint amount, string participantUnidNumber, string description);

    // Event to log service booking details
    event ServiceBooked(address indexed participant, string serviceDescription);

    // Event to log service approval details
    event ServiceOffered(address indexed serviceProvider, address indexed participant, string serviceDescription);

    // Function to handle deposits by NDIS Agency
    function deposit() external payable onlyNDIA {
        updateParticipantFunds();
    }

    // Function to initiate a withdrawal request
    function initiateWithdrawalRequest(uint amount, string memory participantUnidNumber, string memory description) external onlyNdisParticipantAndNdisServiceProvider {
        address payable recipient = payable(msg.sender);
        require(participantFunds >= amount, "Insufficient funds!");

        // Create a withdrawal request and add it to the array
        WithdrawalRequest memory newRequest = WithdrawalRequest({
            requester: recipient,
            amount: amount,
            participantUnidNumber: participantUnidNumber,
            description: description,
            approved: false
        });

        withdrawalRequests.push(newRequest);

        emit WithdrawalRequestInitiated(recipient, amount, participantUnidNumber, description);
    }

    // Function to approve a withdrawal request
    function approveWithdrawal(address payable recipient) external onlyNDIA {
        for (uint i = 0; i < withdrawalRequests.length; i++) {
            if (withdrawalRequests[i].requester == recipient && !withdrawalRequests[i].approved) {
                withdrawalRequests[i].approved = true;

                // Transfer the approved amount to the recipient
                recipient.transfer(withdrawalRequests[i].amount);

                emit Withdrawal(recipient, withdrawalRequests[i].amount, withdrawalRequests[i].participantUnidNumber, withdrawalRequests[i].description);
                break; // Stop iterating after the first approval
            }
        }
    }

    // Function to retrieve all withdrawal requests for a given recipient
    function getWithdrawalRequests() external view returns (WithdrawalRequest[] memory) {
        return withdrawalRequests;
    }

    // Function to retrieve all booking requests for a given recipient
    function getBookingRequests() external view returns (ServiceRequest[] memory) {
        return ServiceRequests;
    }

     // Function for participants to book services
    function bookService(string memory serviceDescription) external onlyNdisParticipant {
        address payable requester = payable(msg.sender);

        // Create a withdrawal request and add it to the array
        ServiceRequest memory newRequest = ServiceRequest({
            requester:requester,
            serviceDescription: serviceDescription,
            offeredService: false
        });

        ServiceRequests.push(newRequest);

        // Emit event to log service booking details
        emit ServiceBooked(msg.sender, serviceDescription);
    }

    // Function for service providers to approve service bookings
    function offerService(address payable participant, string memory serviceDescription) external onlyServiceProvider {
        // Find the corresponding service request
        for (uint i = 0; i < ServiceRequests.length; i++) {
            if (ServiceRequests[i].requester == participant && keccak256(abi.encodePacked(ServiceRequests[i].serviceDescription)) == keccak256(abi.encodePacked(serviceDescription)) && !ServiceRequests[i].offeredService) {
                // Mark the service as offered
                ServiceRequests[i].offeredService = true;

                // Emit event to log service approval details
                emit ServiceOffered(msg.sender, participant, serviceDescription);
                break; // Stop iterating after the first approval
            }
        }
    }

    // Function to register participant and service provider accounts
    function registerAccount(address payable account, bool isParticipantAccount) external onlyNDIA {
        require(!ndisParticipant[account] && !ndisServiceProvider[account], "Account already registered.");

        if (isParticipantAccount) {
            ndisParticipant[account] = true;
        } else {
            ndisServiceProvider[account] = true;
        }
    }

    // Receive function to handle incoming Ether
    receive() external payable {
        updateParticipantFunds();
    }

    // Fallback function to handle unexpected incoming Ether
    fallback() external payable {
        // Handle unexpected incoming Ether if necessary
    }

    // Internal function to update participantFunds
    function updateParticipantFunds() internal {
        participantFunds = address(this).balance;
    }
}
