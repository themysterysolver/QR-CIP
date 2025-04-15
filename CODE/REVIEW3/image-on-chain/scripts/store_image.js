const fs = require('fs');
const path = require('path');
const Web3 = require("web3");
const contract = require('@truffle/contract');  // <- Add this line

const web3 = new Web3("http://127.0.0.1:7545");
const imageStoreArtifact = require('../build/contracts/ImageStore.json');
const ImageStore = contract(imageStoreArtifact);
ImageStore.setProvider(web3.currentProvider);

const storeImage = async () => {
  const accounts = await web3.eth.getAccounts();
  const instance = await ImageStore.deployed();

  // Read the image file (image1.txt or new_image.txt)
  const imagePath = path.join(__dirname, '../images/image.txt'); // Image file path
  const imageText = fs.readFileSync(imagePath, 'utf8'); // Read as text (no encoding to base64)
  
  // Store the image text on the blockchain (as plain text)
  await instance.storeImage(imageText, { from: accounts[0] });
  console.log('New image stored successfully!');
};

storeImage();
