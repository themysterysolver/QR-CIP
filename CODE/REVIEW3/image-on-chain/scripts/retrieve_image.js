const fs = require('fs');
const path = require('path');
const Web3 = require("web3");
const contract = require('@truffle/contract');  // <- Add this line

const web3 = new Web3("http://127.0.0.1:7545");
const imageStoreArtifact = require('../build/contracts/ImageStore.json');
const ImageStore = contract(imageStoreArtifact);
ImageStore.setProvider(web3.currentProvider);

const retrieveImage = async () => {
  const accounts = await web3.eth.getAccounts();
  const instance = await ImageStore.deployed();

  // Retrieve the stored image using the correct contract method
  const imageBase64 = await instance.retrieveImage(accounts[0]);

  // Write the image content to a file (in base64)
  const imagePath = path.join(__dirname, '../images/retrieved_image.txt');
  fs.writeFileSync(imagePath, imageBase64);

  console.log('Image retrieved and saved successfully!');
};

retrieveImage();
