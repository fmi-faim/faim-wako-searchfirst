// SPDX-FileCopyrightText: 2024 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
//
// SPDX-License-Identifier: MIT

path = getArgument();
classifierPath = "/path/to/classifier_v1.model";
mag_firstpass = 4;
mag_secondpass = 20;
overlap_ratio = 0.05;

// === don't edit below this line
mag_ratio = mag_firstpass / mag_secondpass;

// list all files in path
folderName = File.getName(path);
fileList = getFileList(path);

// setup segmentation folder
parent = File.getParent(path);
seg_folder = parent + File.separator + folderName + "_segmentation";
File.makeDirectory(seg_folder);

setBatchMode(false);
// loop over image data files (start with folder name)
for (i = 0; i < fileList.length; i++) {
	if (startsWith(fileList[i], folderName) && endsWith(fileList[i], ".tif")) {
		process(path, fileList[i], seg_folder);
	}
}
run("Quit");

function process(folder, tifFile, seg_folder) {
	// process a single tif file, write a csv file with coordinates
	name = File.getNameWithoutExtension(folder + File.separator + tifFile);
	print("Processing: " + name);
	open(folder + File.separator + tifFile);
	run("Subtract Background...", "rolling=50 light sliding");
	run("Bin...", "x=4 y=4 bin=Average");
	run("Trainable Weka Segmentation");
	wait(300);
	call("trainableSegmentation.Weka_Segmentation.loadClassifier", classifierPath);
	//call("trainableSegmentation.Weka_Segmentation.getResult");
	call("trainableSegmentation.Weka_Segmentation.getProbability");
	selectImage("Probability maps");
	run("Duplicate...", "use");
	selectImage("class 1");
	saveAs("Tiff", seg_folder + File.separator + name + "_prob.tif");
	run("Gaussian Blur...", "sigma=5 slice");
	setOption("BlackBackground", true);
	setThreshold(0.4, 1.0);
	run("Convert to Mask", "background=Dark black");
	// Remove small particles
	maskId = getImageID();
	// save image for quality control
	saveAs("PNG", seg_folder + File.separator + name + "_mask.png");

	// resize image by overlap ratio and magnification ratio
	n_tiles_x = Math.floor((1 + overlap_ratio) / mag_ratio); // 6
	n_tiles_y = Math.floor((1 + overlap_ratio) / mag_ratio);
	print("n_tiles: " + n_tiles_x);

	w = getWidth(); // 500
	h = getHeight();
	tile_w = (w * (1 - overlap_ratio) * mag_ratio); // 80
	tile_h = (h * (1 - overlap_ratio) * mag_ratio);
	print("tile_w: " + tile_w);

	offset_x = w/2;
	offset_y = h/2;
	margin_x = w * mag_ratio * overlap_ratio; // 20
	margin_y = h * mag_ratio * overlap_ratio;
	print("margin_x: " + margin_x);

	crop_w = w - margin_x; // 500 => 480
	crop_h = h - margin_y;
	print("crop_w: " + crop_w);
	run("Canvas Size...", "width=&crop_w height=&crop_h position=Center");

	target_w = n_tiles_x * tile_w; // 
	target_h = n_tiles_y * tile_h;
	print("target_w: " + target_w);
	run("Canvas Size...", "width=&target_w height=&target_h position=Center zero");
	run("Duplicate...", "title=mask"); // DEBUG
	run("32-bit");
	run("Size...", "width=&n_tiles_x height=&n_tiles_y depth=1 constrain average interpolation=None");

	// write csv
	height = getHeight();
	width = getWidth();
	rowIndex = 0;
	Table.create("Coordinates " + tifFile);
	for (x = 0; x < width; x++) {
		for (y = 0; y < height; y++) {
			if (getPixel(x, y) > 1.0) {
				Table.set("X", rowIndex, 4.0 * (x * tile_w + (0.5 * tile_w) + ((w - target_w)/2)));
				Table.set("Y", rowIndex, 4.0 * (y * tile_h + (0.5 * tile_h) + ((h - target_h)/2)));
				rowIndex++;
			}
		}
	}
	Table.showRowNumbers(true);
	Table.saveColumnHeader(false);
	Table.update();
	Table.save(folder + File.separator + name + ".csv");
	close(Table.title);
	close("*");
}


// (optional) read all Z slices for given file

// 