xdata_length = 35
in_file_name = 'ham1_O2100004.txt'
out_file_name = 'ham1_O2100004.xdata.csv'
line_ending = '\n'


def gps_timestamp_to_time_string(gpsweek, gpsseconds, leapseconds):
    import datetime
    datetimeformat = "%Y-%m-%d,%H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06,00:00:00", datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek * 7), seconds=(gpsseconds - leapseconds))
    return datetime.datetime.strftime(epoch + elapsed, datetimeformat)


if __name__ == '__main__':
    in_file = open(in_file_name, 'r')
    out_file = open(out_file_name, 'w')
    frames = in_file.readlines()

    out_file.writelines("Date, Time, Framenumber, xdata" + line_ending)

    for frame in frames:
        raw_string = frame.strip()
        frame_bytes = bytes.fromhex(raw_string)

        frame_number = (frame_bytes[0x3c] << 8) | frame_bytes[0x3b]
        gps_week = (frame_bytes[0x96] << 8) | frame_bytes[0x95]
        gps_time_of_week = (frame_bytes[0x9A] << 24) | (frame_bytes[0x99] << 16) | (frame_bytes[0x98] << 8) | frame_bytes[0x97]
        xdata_payload = frame_bytes[0x12E:(0x12E + xdata_length)].decode('utf_8', errors='ignore')

        gps_string = gps_timestamp_to_time_string(gps_week, gps_time_of_week/1000, 0)

        print('Frame #:', frame_number, 'Week:', gps_week, 'TOW:', gps_time_of_week, 'GPS Time:', gps_string, 'xdata:', xdata_payload)

        out_file.writelines(gps_string + ',' + str(frame_number) + ',' + xdata_payload + ',' + line_ending)
