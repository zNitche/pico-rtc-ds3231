from micropython import const
from machine import I2C
import time

DATETIME_REG_ADDRESS = const(0x00)
STATUS_REG_ADDRESS = const(0x0F)
DEVICE_ADDRESS = const(0x68)


class DateTime:
    def __init__(self,
                 year: str | int, month: str | int, day: str | int,
                 hour: str | int, minutes: str | int, seconds: str | int):

        self.seconds = int(seconds)
        self.minutes = int(minutes)
        self.hour = int(hour)
        self.day = int(day)
        self.month = int(month)
        self.year = int(year)

    def to_iso_string(self) -> str:
        seconds = f"{self.seconds:02d}"
        minutes = f"{self.minutes:02d}"
        hour = f"{self.hour:02d}"
        day = f"{self.day:02d}"
        month = f"{self.month:02d}"

        return f"{self.year}-{month}-{day}T{hour}:{minutes}:{seconds}.000Z"

    @staticmethod
    def from_iso(iso_date: str):
        split_date = iso_date.split(".")[0].split("T")
        day_section = split_date[0].split("-")
        time_section = split_date[1].split(":")

        year = day_section[0]
        month = day_section[1]
        day = day_section[2]
        hour = time_section[0]
        minutes = time_section[1]
        seconds = time_section[2]

        return DateTime(year=year, month=month, day=day, hour=hour, minutes=minutes, seconds=seconds)

    def __str__(self):
        return f"{self.year}, {self.month}, {self.day}, {self.hour}, {self.minutes}, {self.seconds}"


class DS3231:
    def __init__(self, i2c: I2C, address: int = DEVICE_ADDRESS):
        self.i2c = i2c
        self.address = address

    def is_device_accessible(self) -> bool:
        return True if self.address in self.i2c.scan() else False

    def __write_to_mem(self, reg_address: int, data: bytearray, delay=50):
        self.i2c.writeto_mem(self.address, reg_address, data)
        time.sleep_ms(delay)

    def __bcd_to_dec(self, value: int) -> int:
        return int(f"{value:02x}", 10)

    def __dec_to_bcd(self, value: int) -> int:
        return int(str(value), 16)

    def is_osf_set(self) -> bool:
        buff = self.i2c.readfrom_mem(self.address, STATUS_REG_ADDRESS, 1)
        osf_bit = buff[0] >> 7 & 1

        return bool(osf_bit)

    def reset_osf(self):
        buff = self.i2c.readfrom_mem(self.address, STATUS_REG_ADDRESS, 1)
        status_reg = int.from_bytes(buff, "little")
        # set bit no. 1 to 0 -> reset osf flag
        status_reg = status_reg & ~ (1 << 7)

        self.__write_to_mem(STATUS_REG_ADDRESS, bytearray(status_reg))

    def get_datetime(self) -> DateTime:
        buff = self.i2c.readfrom_mem(self.address, DATETIME_REG_ADDRESS, 7)

        seconds = self.__bcd_to_dec(buff[0])
        minutes = self.__bcd_to_dec(buff[1])
        hour = self.__bcd_to_dec(buff[2])

        day = self.__bcd_to_dec(buff[4])
        # set century bit to 0 / remove it
        month = self.__bcd_to_dec(buff[5] & ~ 0x80)
        year = self.__bcd_to_dec(buff[6]) + 2000

        return DateTime(year, month, day, hour, minutes, seconds)

    def set_datetime(self, datetime: DateTime):
        buf = bytearray(7)

        buf[0] = self.__dec_to_bcd(datetime.seconds)
        buf[1] = self.__dec_to_bcd(datetime.minutes)
        buf[2] = self.__dec_to_bcd(datetime.hour)
        buf[3] = 0
        buf[4] = self.__dec_to_bcd(datetime.day)
        # set century bit to 1
        buf[5] = self.__dec_to_bcd(datetime.month) & ~ 0x80
        buf[6] = self.__dec_to_bcd(int(str(datetime.year)[-2:]))

        self.__write_to_mem(DATETIME_REG_ADDRESS, buf, delay=100)
        self.reset_osf()
