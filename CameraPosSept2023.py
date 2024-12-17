import pandas as pd
import os

# Code uses all jpg files in the selected folder
# Therefore, remove bad jpg files from the folder BEFORE running this code
# version created Aug. 2023 by Eric Tannant

def CameraPos2023():
    # Get the directory of the current Python script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    filetype = (".JPG", ".jpg")

    # EXTRACT image names from current directory
    image_files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(filetype)]
    Num_Good_Images = len(image_files)
    ID_Num = []

    for image_name in image_files:
        temp1 = image_name
        temp2 = temp1.split('_')
        temp3 = temp2[2]
        temp4 = temp3.split('.')
        ID_Num.append(int(temp4[0]))

    #Rinex Section
    #Get rinex file
    rinex_file = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(".pos")]
    rinex_file_path = os.path.join(script_directory, rinex_file[0]) if rinex_file else None

    if rinex_file_path:
        # Read Rinex data while skipping the header
        Rinex_data = pd.read_csv(rinex_file_path, skiprows=5, delimiter=r"\s+")
        Rinex_length = len(Rinex_data)
        Rinex = []

    for i in range(Rinex_length):
        HMS1 = Rinex_data.iloc[i, 5]
        HMS2 = HMS1.split(':')
        HMS3 = list(map(float, HMS2))
        HH, MM, SS = HMS3
        Seconds = HH * 60.0 * 60.0 + MM * 60.0 + SS
        Rinex.append([Seconds, Seconds / 60.0 / 60.0,
                      Rinex_data.iloc[i, 24], Rinex_data.iloc[i, 25],
                      Rinex_data.iloc[i, 33]])

    for t in range(1, Rinex_length):
        Current_time = Rinex[t][1]
        Past_time = Rinex[t - 1][1]
        if Current_time - Past_time <= 0:
            for i in range(t, Rinex_length):
                Rinex[i][1] += 24.0
            break

    # READ in Timestamp file
    timestamp_file = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f)) and f.endswith(".MRK")]
    image_timestamp = os.path.join(script_directory, timestamp_file[0]) if timestamp_file else None

    if image_timestamp:
        TimeStamp = pd.read_csv(image_timestamp, header=None, sep='\t')
        Num_Photos = len(TimeStamp)
        Offset = []

    ImageTime = []  # Store all ImageTime values
    ImageID = []

    for i in range(Num_Photos):
        ImageID_i = TimeStamp.iloc[i, 0]
        ImageID.append(ImageID_i)
        Seconds = TimeStamp.iloc[i, 1]
        ImageTime_i = (Seconds / 60.0 / 60.0) - int(Seconds / 60.0 / 60.0 / 24.0) * 24.0
        ImageTime.append(ImageTime_i)  # Store the ImageTime value
        East1 = TimeStamp.iloc[i, 4]
        East2 = East1.split(',')
        East4 = float(East2[0])
        North1 = TimeStamp.iloc[i, 3]
        North2 = North1.split(',')
        North4 = float(North2[0])
        Elev1 = TimeStamp.iloc[i, 5]
        Elev2 = Elev1.split(',')
        Elev4 = float(Elev2[0])
        Offset.append([East4, North4, Elev4])

    for t in range(1, Num_Photos):
        if ImageTime[t] - ImageTime[t - 1] < 0:
            for i in range(t, Num_Photos):
                ImageTime[i] += 24
            break

    # CALCULATE Timestamp location within rinex times and calculate camera location
    East = []
    North = []
    Elev = []

    for j in range(Num_Photos):
        Hour = ImageTime[j]
        east_offset, north_offset, elev_offset = Offset[j]

        for i in range(1, Rinex_length):
            Time_before = Rinex[i - 1][1]
            Time_after = Rinex[i][1]
            if Time_before < Hour < Time_after:
                delta_time1 = Time_after - Time_before
                delta_time2 = Hour - Time_before

                delta_east = Rinex[i][2] - Rinex[i - 1][2]
                EastXX = Rinex[i - 1][2] + delta_east * delta_time2 / delta_time1
                East_coord = EastXX + east_offset / 1000
                East.append(East_coord)

                delta_north = Rinex[i][3] - Rinex[i - 1][3]
                NorthXX = Rinex[i - 1][3] + delta_north * delta_time2 / delta_time1
                North_coord = NorthXX + north_offset / 1000
                North.append(North_coord)

                delta_elev = Rinex[i][4] - Rinex[i - 1][4]
                ElevXX = Rinex[i - 1][4] + delta_elev * delta_time2 / delta_time1
                Elev_coord = ElevXX - elev_offset / 1000
                Elev.append(Elev_coord)
                break
            else:
                if Rinex[i - 1][1] - Hour == 0:
                    East.append(Rinex[i - 1][2] + east_offset / 1000)
                    North.append(Rinex[i - 1][3] + north_offset / 1000)
                    Elev.append(Rinex[i - 1][4] - elev_offset / 1000)
                    break

    # WRITE file with image names and updated coordinates
    Output = pd.DataFrame(columns=['Image Name', 'East', 'North', 'Elevation'])

    i = 0
    for j in range(Num_Photos):
        if ID_Num[i] == ImageID[j]:
            Output.loc[i] = [image_files[i], East[j], North[j], Elev[j]]
            if i == Num_Good_Images - 1:
                break
            i += 1


    output_file_path = os.path.join(script_directory, 'Camera_coords.txt')
    Output.to_csv(output_file_path, sep=',', index=False, header=False)

# Call the main function
CameraPos2023()