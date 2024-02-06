// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title NDISSmartContract
 * @dev A smart contract to manage funds and withdrawals for NDIS (National Disability Insurance Scheme).
 */

contract NDISSmartContract {

    address public ndia; // NDIS Agency's address
    address payable public ndisParticipant;
    address payable public ndisServiceProvider;
    uint public participantFunds;

    // // Mapping to track withdrawal requests
    // mapping(address => WithdrawalRequest) public withdrawalRequests;

    // Array to store withdrawal requests
    WithdrawalRequest[] public withdrawalRequests;

    // Add a counter for withdrawal requests
    uint public withdrawalRequestCount;

    // Struct to represent a withdrawal request
    struct WithdrawalRequest {
        address payable requester;
        uint amount;
        string participantUnidNumber;
        string description;
        bool approved;
    }

    // Constructor to set the NDIS Agency's address
    constructor() {
        ndia = msg.sender;
    }

    // Modifier to ensure only NDIS Agency can execute certain functions
    modifier onlyNDIA() {
        require(msg.sender == ndia, "Permission denied: Only NDIS Agency can execute this.");
        _;
    }

    // Event to log withdrawal details
    event Withdrawal(address indexed recipient, uint amount, string participantUnidNumber, string description);
    event WithdrawalRequestInitiated(address indexed recipient, uint amount, string participantUnidNumber, string description);

    // Function to handle deposits by NDIS Agency
    function deposit() external payable onlyNDIA {
        updateParticipantFunds();
    }

    // Function to initiate a withdrawal request
    function initiateWithdrawalRequest(uint amount, string memory participantUnidNumber, string memory description) external {
        address payable recipient = payable(msg.sender);
        require(recipient == ndisParticipant || recipient == ndisServiceProvider, "Permission denied: Only ndisParticipant or ndisServiceProvider can initiate withdrawal requests.");
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
    function approveWithdrawal(uint index) external onlyNDIA {
        require(index < withdrawalRequests.length, "Invalid index");

        WithdrawalRequest storage request = withdrawalRequests[index];
        require(!request.approved, "Withdrawal request already approved.");

        // Mark the withdrawal request as approved
        request.approved = true;

        // Perform the withdrawal
        request.requester.transfer(request.amount);

        emit Withdrawal(request.requester, request.amount, request.participantUnidNumber, request.description);
        updateParticipantFunds();
    }

    // Function to retrieve all withdrawal requests for a given recipient
    function getWithdrawalRequests(address recipient) external view returns (
        address[] memory requesters,
        uint[] memory amounts,
        string[] memory participantUnidNumbers,
        string[] memory descriptions,
        bool[] memory approvedStatuses
    ) {
        uint requestCount = 0;

        // Iterate over withdrawalRequests mapping to count matching requests
        for (uint i = 0; i < withdrawalRequests.length; i++) {
            WithdrawalRequest memory request = withdrawalRequests[i];

            // Check if the request exists and matches the recipient
            if (request.requester == recipient) {
                requestCount++;
            }
        }

        // Initialize arrays with the appropriate size
        requesters = new address[](requestCount);
        amounts = new uint[](requestCount);
        participantUnidNumbers = new string[](requestCount);
        descriptions = new string[](requestCount);
        approvedStatuses = new bool[](requestCount);

        // Iterate over withdrawalRequests mapping to populate the arrays with details
        uint currentIndex = 0;
        for (uint i = 0; i < withdrawalRequests.length; i++) {
            WithdrawalRequest memory request = withdrawalRequests[i];

            // Check if the request exists and matches the recipient
            if (request.requester == recipient) {
                requesters[currentIndex] = request.requester;
                amounts[currentIndex] = request.amount;
                participantUnidNumbers[currentIndex] = request.participantUnidNumber;
                descriptions[currentIndex] = request.description;
                approvedStatuses[currentIndex] = request.approved;
                currentIndex++;
            }
        }

        return (requesters, amounts, participantUnidNumbers, descriptions, approvedStatuses);
    }


    // Function to set participant and service provider accounts
    function setAccounts(address payable participant, address payable serviceProvider) external onlyNDIA {
        ndisParticipant = participant;
        ndisServiceProvider = serviceProvider;
        updateParticipantFunds();
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
