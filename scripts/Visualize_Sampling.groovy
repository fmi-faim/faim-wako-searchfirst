// SPDX-FileCopyrightText: 2023 Friedrich Miescher Institute for Biomedical Research (FMI), Basel (Switzerland)
//
// SPDX-License-Identifier: MIT

#@ File (label="Segmentation image") seg_file
#@ String (value="Please drag and drop segmentation image file here", visibility="MESSAGE") hint
#@ Boolean (label="Display Wako Grid") display_grid
#@ Integer (label="First Pass Magnification", value=4) first_pass_mag
#@ Integer (label="Second Pass Magnification", value=40) second_pass_mag

import com.opencsv.CSVReader
import ij.gui.PointRoi
import ij.gui.Roi
import ij.gui.Overlay
import ij.IJ
import java.awt.Color

// Open segmentation image file
imp = IJ.openImage(seg_file.getPath())

// Open table file
acquisition_dir = seg_file.parent - ~/_segmentation/
csv_filename = seg_file.name  - ~/(_Objseg)?\.\w+$/ + ".csv" // remove extension

csv_file = new File(acquisition_dir, csv_filename)
assert csv_file.exists()
csv_file.withReader { r ->
	data = new CSVReader(r).readAll()
}

xpoints = data.collect { it[1] as float }
ypoints = data.collect { it[2] as float }

pointRoi = new PointRoi(xpoints as float[], ypoints as float[])

// Create grid
factor = second_pass_mag / first_pass_mag
width = imp.getWidth() / factor
height = imp.getHeight() / factor

ovl = new Overlay()
(factor as int).times { x ->
	(factor as int).times { y ->
		ovl.add(new Roi(x * width, y* height, width, height))
	}
}
ovl.setStrokeColor(new Color(1.0, 1.0, 0.0, 1.0))
if (display_grid) {
	imp.setOverlay(ovl)
}

imp.setRoi(pointRoi)
imp.show()
