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

    // Event to log withdrawal details
    event Withdrawal(address indexed recipient, uint amount, string participantUnidNumber, string description);
    event WithdrawalRequestInitiated(address indexed recipient, uint amount, string participantUnidNumber, string description);

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
