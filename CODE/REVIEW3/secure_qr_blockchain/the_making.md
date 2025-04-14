### NOTES
---
```
python -m venv venv 
venv\Scripts\activate
pip install -r requirements.txt
pip install qrcode pillow opencv-python numpy

```
---

###### To view your etherium transaction
```
 https://sepolia.etherscan.io/tx/{your_tx_hash}
  https://sepolia.etherscan.io/tx/{8f1f4cd73a424472021e7cf7b21404b4cd51ee868fab96848c91b42a71faec12}
```

###### Defining smart_contract

- **StoreIPFS.sol**
```solidity[]
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract StoreIPFS {
    string[] public ipfsHashes;

    // Store a new IPFS hash (appended to the array)
    function storeIPFSHash(string memory ipfsHash) public {
        ipfsHashes.push(ipfsHash);
    }

    // Retrieve an IPFS hash by index
    function getIPFSHash(uint index) public view returns (string memory) {
        require(index < ipfsHashes.length, "Invalid index");
        return ipfsHashes[index];
    }

    // Get total number of IPFS hashes stored
    function getTotalHashes() public view returns (uint) {
        return ipfsHashes.length;
    }
}

```