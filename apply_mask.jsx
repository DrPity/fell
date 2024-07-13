#target photoshop

// Function to apply mask
function applyMask(imageFile, maskFile, outputFolder) {
    // Open the original image
    var doc = open(imageFile);

    // Load the mask image
    var maskDoc = open(maskFile);

    // Select and copy the mask
    maskDoc.selection.selectAll();
    maskDoc.selection.copy();
    maskDoc.close(SaveOptions.DONOTSAVECHANGES);

    // Add a new layer mask to the original image
    var layer = doc.activeLayer;

    // Create a new layer for the mask
    var maskLayer = doc.artLayers.add();
    doc.paste();
    
    // Convert the pasted mask to a selection
    doc.selection.selectAll();
    doc.selection.load(doc.channels[doc.channels.length - 1], SelectionType.REPLACE);

    // Remove the mask layer
    maskLayer.remove();
    
    // Stop script execution here
    // alert("Mask has been applied. Script execution stopped.");  // Uncomment this line to show an alert
    return;

    // The following code will not execute
    /*
    // Apply the selection as a layer mask
    doc.activeLayer = layer;
    doc.activeLayer.addLayerMask(SelectionType.REPLACE);

    // Deselect to return to normal view
    doc.selection.deselect();

    // Save the result as PNG
    var outputFile = new File(outputFolder + "/" + imageFile.name.replace(/\.[^\.]+$/, ".png"));
    var pngOptions = new PNGSaveOptions();
    doc.saveAs(outputFile, pngOptions, true, Extension.LOWERCASE);

    // Save the result as PSD
    var outputPSDFile = new File(outputFolder + "/" + imageFile.name.replace(/\.[^\.]+$/, ".psd"));
    var psdOptions = new PhotoshopSaveOptions();
    doc.saveAs(outputPSDFile, psdOptions, true, Extension.LOWERCASE);

    // Close the document without saving
    doc.close(SaveOptions.DONOTSAVECHANGES);
    */
}

// Function to process each image and its corresponding mask
function processImages(inputFolder, maskFolder, outputFolder) {
    var imageFiles = inputFolder.getFiles(/\.(jpg|jpeg|png|tif|tiff)$/i);

    for (var i = 0; i < imageFiles.length; i++) {
        var imageFile = imageFiles[i];
        var maskFile = new File(maskFolder + "/" + imageFile.name);

        if (maskFile.exists) {
            applyMask(imageFile, maskFile, outputFolder);
        }
    }
}

// Main function to select folders and process images
function main() {
    var inputFolder = Folder.selectDialog("Select the folder with the original images");
    var maskFolder = Folder.selectDialog("Select the folder with the mask images");
    var outputFolder = Folder.selectDialog("Select the output folder");

    if (inputFolder && maskFolder && outputFolder) {
        processImages(inputFolder, maskFolder, outputFolder);
    }
}

main();
