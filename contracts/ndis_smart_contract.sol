// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title NDISSmartContract
 * @dev A smart contract to manage funds and withdrawals for NDIS (National Disability Insurance Scheme).
 */


contract NDISSmartContract {

    enum RequestStatus { Pending, ServiceOffered, WaitingForAppraval, Approved }

    // Struct to represent a request
    struct Request {
        string jobNumber;
        address payable requester;
        uint amount; 
        string participantUnidNumber; 
        string serviceDescription; 
        RequestStatus status;
    }

    // Mapping to store requests
    mapping(bytes32 => Request) public requests;
    bytes32[] public requestIds;

    address public ndia; // NDIS Agency's address
    uint public participantFunds;
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

    // Event to log account registration details
    event AccountRegistered(address indexed account, bool isParticipantAccount);

    // Event to log service booking details
    event ServiceBooked(string jobNumber, address indexed participant, bytes32 requestId, string serviceDescription, uint amount, RequestStatus status);

    // Event to log service approval details
    event ServiceOffered(address indexed serviceProvider, address indexed participant, bytes32 requestId, string serviceDescription, RequestStatus status);

    // Event to log withdrawal details
    event Withdrawal(address indexed recipient, bytes32 requestId, uint amount, string participantUnidNumber, string serviceDescription, RequestStatus status);
    event WithdrawalRequestInitiated(address indexed recipient, bytes32 requestId, uint amount, RequestStatus status);

    /**
    * NDIS Functions 
    */

    // Function to handle deposits by NDIS Agency
    function deposit() external payable onlyNDIA {
        updateParticipantFunds();
    }

    // Function to register participant and service provider accounts
    function registerAccount(address payable account, bool isParticipantAccount) external onlyNDIA {
        require(!ndisParticipant[account] && !ndisServiceProvider[account], "Account already registered.");

        if (isParticipantAccount) {
            ndisParticipant[account] = true;
        } else {
            ndisServiceProvider[account] = true;
        }

        // Emit event to log account registration details
        emit AccountRegistered(account, isParticipantAccount);
    }

    // Function to approve a withdrawal request
    function approveWithdrawal(bytes32 requestId) external onlyNDIA {
        // Check if the request exists
        require(requests[requestId].status != RequestStatus.Approved, "Request already approved");
        require(requests[requestId].status == RequestStatus.WaitingForAppraval, "Request is waiting for approval");

        // Mark the service as approved
        requests[requestId].status = RequestStatus.Approved;

        // Transfer the approved amount to the recipient
        requests[requestId].requester.transfer(requests[requestId].amount);

        emit Withdrawal(requests[requestId].requester, requestId, requests[requestId].amount, requests[requestId].participantUnidNumber, requests[requestId].serviceDescription, requests[requestId].status);

        updateParticipantFunds();
    }

    /**
    * Participant Functions 
    */

    // Function for participants to book services
    function bookService(string memory jobNumber, string memory serviceDescription, uint amount, string memory participantUnidNumber) external onlyNdisParticipant {
        address payable requester = payable(msg.sender);
        bytes32 requestId = keccak256(abi.encodePacked(requester, serviceDescription, amount, participantUnidNumber, block.timestamp));

        // Create a service request and add it to the mapping
        requests[requestId] = Request({
            jobNumber: jobNumber,
            requester: requester,
            amount: amount,
            participantUnidNumber: participantUnidNumber,
            serviceDescription: serviceDescription,
            status: RequestStatus.Pending
        });

        requestIds.push(requestId);

        // Emit event to log service booking details
        emit ServiceBooked(jobNumber, msg.sender, requestId, serviceDescription, amount, RequestStatus.Pending);
    }

    /**
    * Service Provider Functions 
    */

    // Function for service providers to offer service bookings
    function offerService(address payable participant, bytes32 requestId, string memory serviceDescription) external onlyServiceProvider {
        require(requests[requestId].status == RequestStatus.Pending, "Request not pending");

        // Mark the service as offered
        requests[requestId].status = RequestStatus.ServiceOffered;

        // Emit event to log service approval details
        emit ServiceOffered(msg.sender, participant, requestId, serviceDescription, RequestStatus.ServiceOffered);
    }

    // Function to initiate a withdrawal request
    function initiateWithdrawalRequest(bytes32 requestId, uint amount) external onlyNdisParticipantAndNdisServiceProvider {
        address payable recipient = payable(msg.sender);
        require(requests[requestId].status == RequestStatus.ServiceOffered, "Service Rendered");
        require(participantFunds >= amount, "Insufficient funds!");

        // Mark the service as waiting for approval
        requests[requestId].status = RequestStatus.WaitingForAppraval;

        // Emit event to log service approval details
        emit WithdrawalRequestInitiated(recipient, requestId, amount, RequestStatus.WaitingForAppraval);
    }

    /**
    * Retrieve info and default functions 
    */

    // Function to retrieve all booking requests for a given recipient
    function getBookingRequests() external view returns (Request[] memory) {
        Request[] memory result = new Request[](requestIds.length);
        for (uint i = 0; i < requestIds.length; i++) {
            result[i] = requests[requestIds[i]];
        }
        return result;
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
        participantFunds = SafeMath.add(address(this).balance, participantFunds);
    }
}
