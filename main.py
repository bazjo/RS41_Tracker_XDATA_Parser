import struct

in_file_name = 'test.txt'
out_file_name = 'test.xdata.csv'
line_ending = '\n'

CRC16_INITIAL_VALUE = 0xFFFF
CRC16_XOR_OUT = 0x0000
CRC16_POLYNOMIAL = 0x1021

def crc16(data):
    xor_in = CRC16_INITIAL_VALUE  # initial value
    xor_out = CRC16_XOR_OUT  # final XOR value
    poly = CRC16_POLYNOMIAL  # generator polinom (normal form)

    reg = xor_in
    for octet in data:
        # reflect in
        for i in range(8):
            topbit = reg & 0x8000
            if octet & (0x80 >> i):
                topbit ^= 0x8000
            reg <<= 1
            if topbit:
                reg ^= poly
        reg &= 0xFFFF
        # reflect out
    return reg ^ xor_out

def gps_timestamp_to_time_string(gpsweek, gpsseconds, leapseconds):
    import datetime
    datetimeformat = "%Y-%m-%d,%H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06,00:00:00", datetimeformat)
    elapsed = datetime.timedelta(days=(gpsweek * 7), seconds=(gpsseconds - leapseconds))
    return datetime.datetime.strftime(epoch + elapsed, datetimeformat)


if __name__ == '__main__':
    zeros = bytes.fromhex('16 01 4F 50 54 45 43 30 30 31 16 00 00 00 00 00 1D 40 00 00 00 00 32 16 CD CC CC 3D BD FF 4B BF 47 49 9E BD 66 36 B1 33'.strip())
    print(zeros)
    print(hex(crc16(zeros)))

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

        xdata_length = frame_bytes[0x12C]
        xdata_payload = frame_bytes[0x12D:(0x12D + xdata_length)]
        xdata_crc = (frame_bytes[0x12D + xdata_length + 1] << 8) | frame_bytes[0x12D + xdata_length]
        calculated_crc = crc16(xdata_payload)

        measurement_bytes = xdata_payload[20:]
        print(len(measurement_bytes))
        formatter = '<' + 'f' * (len(measurement_bytes) // struct.calcsize('f'))
        numbers = struct.unpack(formatter, measurement_bytes)
        print(numbers)

        keys = ['accX', 'accY', 'accZ', 'gyrX', 'gyrY', 'gyrZ']
        imu_values = [dict(zip(keys, numbers[i:i+6])) for i in range(0, 30, 6)]
        print(imu_values)

        gps_string = gps_timestamp_to_time_string(gps_week, gps_time_of_week/1000, 0)

        print('Frame #:', frame_number,
              'Week:', gps_week,
              'TOW:', gps_time_of_week,
              'GPS Time:', gps_string,
              'xdata:', hex(xdata_length), xdata_payload[20:].decode('utf_8', errors='ignore'), hex(xdata_crc))

        out_file.writelines(gps_string + ',' + str(frame_number) + ',' + xdata_payload.decode('utf_8', errors='ignore') + ',' + line_ending)
