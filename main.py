import machine
import ds3231


def main():
    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
    rtc_module = ds3231.DS3231(i2c)

    if rtc_module.is_device_accessible():
        # rtc_module.set_datetime(ds3231.DateTime(2023, 6, 7, 15, 7, 0))

        datetime = rtc_module.get_datetime()
        time_accurate = rtc_module.is_time_accurate()

        print(f"Datetime: {datetime}, time accurate: {time_accurate}")


if __name__ == '__main__':
    main()
