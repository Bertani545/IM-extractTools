# Run with vgmstream-cli and DATA2.DAT in the same folder
# Use the command 'python3 extarctAudio.py' to run it and wait for it to finish
# Will create a folder for each character and extract the files to them

from pathlib import Path
import subprocess


SoundPointer = 1
BINPointer = 1
lastNamePosition = 0;

filePointer = 0
nextFilePointer = 0;
firstSShd = 0x56FD8;
lastFilePointer = 0;
 
folderNames = []
fileName = "";

bufferSizeNames = 0x566a5 # All names are here *1024
bufferSizeFiles = 50 * 1024 * 1024 # Sufficiently big buffer



chunkFiles1 = 0
chunkFiles2 = 0

chunkNames = 0;

differentValues = []

Path("SOUND").mkdir(parents=True, exist_ok=True)

with open("DATA2.DAT", "rb") as voicesFile:

	chunkNames = voicesFile.read(bufferSizeNames); # Only once

	voicesFile.seek(firstSShd);
	chunkFiles1 = voicesFile.read(bufferSizeFiles);
	chunkFiles2 = voicesFile.read(bufferSizeFiles);

	#for i in range(85):
	while  SoundPointer >= 0:
		# Find the name
		SoundPointer = chunkNames.find(b'SOUND', lastNamePosition);
		BINPointer = chunkNames.find(b'.BIN', lastNamePosition);
		lastNamePosition = BINPointer + 4;

		# Extract name
		fileDir = chunkNames[SoundPointer: BINPointer+4].decode();

		# Separate it like SOUND / MASHIMARO / FILE
		parts = fileDir.split("/");

		if len(parts) == 3:
			_, folder, fileName = parts; 
		elif len(parts) == 2:
			_, fileName = parts;
			folder = "";
		else:
			break;
		fileName = fileName[:-4] #removes the .BIN

		if folder not in folderNames and folder:
			Path(f"SOUND/{folder}").mkdir(parents=True, exist_ok=True)
			folderNames.append(folder);



		# Create the sound raw data
		filePointer =  nextFilePointer;
		nextFilePointer = chunkFiles1.find(b'SShd', filePointer + 4);

		audioFile = 0;
		# Al files end with 0x756 zeroes
		if(nextFilePointer == -1):
			
			# For this cases, the next search is skipped
			if(chunkFiles1[-3:] == b'SSh' and chunkFiles2[:1] == b'd'):
				bytesPart1 = chunkFiles1[filePointer:-3]
				bytesPart2 = []

				chunkFiles2 = b'SSh' + chunkFiles2;
				nextFilePointer = 0;

			elif(chunkFiles1[-2:] == b'SS' and chunkFiles2[:2] == b'hd'):
				bytesPart1 = chunkFiles1[filePointer:-2]
				bytesPart2 = []

				chunkFiles2 = b'SS' + chunkFiles2;
				nextFilePointer = 0;

			elif(chunkFiles1[-1:] == b'S' and chunkFiles2[:3] == b'Shd'):
				bytesPart1 = chunkFiles1[filePointer:-1]
				bytesPart2 = []

				chunkFiles2 = b'S' + chunkFiles2;
				nextFilePointer = 0;

			else:
				# Search in next chunk
				nextFilePointer = chunkFiles2.find(b'SShd', 0);

				bytesPart1 = chunkFiles1[filePointer:]

				if(nextFilePointer == -1): # No more SShd
					bytesPart2 = chunkFiles2;
				else:
					bytesPart2 = chunkFiles2[:nextFilePointer];

			

			audioFile = bytesPart1 + bytesPart2;

			chunkFiles1 = chunkFiles2;
			chunkFiles2 = voicesFile.read(bufferSizeFiles);

		else:
			audioFile = chunkFiles1[filePointer: nextFilePointer]


		# Delete all zeroes at the end
		totalZeroes = 0
		for hx in reversed(audioFile):
			if(hx == 0x00):
				totalZeroes += 1
			else:
				break;
		audioFile = audioFile[:-totalZeroes]
		# Debug
		if totalZeroes not in differentValues:
			differentValues.append(totalZeroes);
			with open(Path("different.txt"), "a") as f:
				f.write(fileName + "\n");

		# Save the raw data for conversion
		with open(Path("temp"), "wb") as f:
			f.write(audioFile);

		# Use vgmstream to transform it
		finalPath = Path("SOUND/" + folder + "/" + fileName + ".wav");
		instruction = "./vgmstream-cli -silent -o " + str(finalPath) + " temp";
		subprocess.run(instruction, shell=True);



		
#print(differentValues)
#print(folderNames)