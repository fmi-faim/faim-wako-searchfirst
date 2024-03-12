#@ File csv_file
#@ String folder_suffix

folder = csv_file.getParentFile()
result_folder = new File(folder.getParentFile(), "${folder.getName()}_${folder_suffix}")
result_folder.mkdir()
