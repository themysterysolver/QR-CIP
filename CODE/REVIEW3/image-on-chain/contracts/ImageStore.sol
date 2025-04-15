pragma solidity ^0.8.0;

contract ImageStore {
    mapping(address => string) public images;

    // Store image as a string (base64 encoded or URL)
    function storeImage(string memory image) public {
        images[msg.sender] = image;
    }

    // Retrieve stored image
    function retrieveImage(address user) public view returns (string memory) {
        return images[user];
    }
}
