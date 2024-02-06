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
    function getWithdrawalRequests() external view returns (WithdrawalRequest[] memory) {
        return withdrawalRequests;
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
