import machine
import ds3231


def main():
    i2c = machine.I2C(1, sda=machine.Pin(2), scl=machine.Pin(3))

    rtc = ds3231.DS3231(i2c)

    print(f"device accessible: {rtc.is_device_accessible()}")

    if rtc.is_device_accessible():
        # current_datetime = ds3231.DateTime(2024, 7, 17, 10, 58, 0)
        # rtc.set_datetime(current_datetime)

        is_time_accurate = not rtc.is_osf_set()
        datetime = rtc.get_datetime()

        print(f"Datetime: {datetime}, ISO Date: {datetime.to_iso_string()}, is time accurate: {is_time_accurate}")


if __name__ == '__main__':
    main()
