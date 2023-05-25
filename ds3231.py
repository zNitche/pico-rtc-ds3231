# Micropython driver for the DS3231 RTC Module
# Lightweight version of https://github.com/pangopi/micropython-DS3231-AT24C32/blob/main/ds3231.py

from micropython import const


DATETIME_REG = const(0)
STATUS_REG = const(15)


class DS3231:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self._time_buffer = bytearray(7)

    def is_device_accessible(self):
        return True if self.addr in self.i2c.scan() else False

    def dec2bcd(self, decimal):
        return (decimal // 10) << 4 | (decimal % 10)

    def bcd2dec(self, bcd):
        return ((bcd >> 4) * 10) + (bcd & 0x0F)

    def get_date(self, check_accuracy=False):
        if check_accuracy and self.osf():
            raise Exception("Oscillator stop flag set. Time may not be accurate.")

        self.i2c.readfrom_mem_into(self.addr, DATETIME_REG, self._time_buffer)

        seconds = self.bcd2dec(self._time_buffer[0])
        minutes = self.bcd2dec(self._time_buffer[1])
        hour = self.bcd2dec(self._time_buffer[2])

        day = self.bcd2dec(self._time_buffer[4])
        month = self.bcd2dec(self._time_buffer[5] & 0x7f)
        year = self.bcd2dec(self._time_buffer[6]) + 2000

        return DateTime(year, month, day, hour, minutes, seconds)

    def set_date(self, datetime):
        self._time_buffer[0] = self.dec2bcd(datetime.seconds)
        self._time_buffer[1] = self.dec2bcd(datetime.minutes)
        self._time_buffer[2] = self.dec2bcd(datetime.hour)
        self._time_buffer[3] = 0
        self._time_buffer[4] = self.dec2bcd(datetime.day)
        self._time_buffer[5] = self.dec2bcd(datetime.month) & 0xff
        self._time_buffer[6] = self.dec2bcd(int(str(datetime.year)[-2:]))

        self.i2c.writeto_mem(self.addr, DATETIME_REG, self._time_buffer)

        self.reset_osf()

    def osf(self):
        return bool(self.i2c.readfrom_mem(self.addr, STATUS_REG, 1)[0] >> 7)

    def reset_osf(self):
        reg_buffer = bytearray(1)

        self.i2c.readfrom_mem_into(self.addr, STATUS_REG, reg_buffer)
        self.i2c.writeto_mem(self.addr, STATUS_REG, bytearray([reg_buffer[0] & 0x7f]))


class DateTime:
    def __init__(self, year, month, day, hour, minutes, seconds):
        self.seconds = seconds
        self.minutes = minutes
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year

    def to_iso_string(self):
        month = str(self.month).zfill(2)
        day = str(self.day).zfill(2)
        hour = str(self.hour).zfill(2)
        minutes = str(self.minutes).zfill(2)
        seconds = str(self.seconds).zfill(2)

        return f"{self.year}-{month}-{day}T{hour}:{minutes}:{seconds}.000Z"

    def __str__(self):
        return f"{self.year}, {self.month}, {self.day}, {self.hour}, {self.minutes}, {self.seconds}"
