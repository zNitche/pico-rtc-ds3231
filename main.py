import machine
import ds3231


def main():
    i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
    rtc_module = ds3231.DS3231(i2c)

    if rtc_module.is_device_accessible():
        # rtc_module.set_date(ds3231.DateTime(2023, 5, 24, 17, 10, 0))

        print(rtc_module.get_date(check_accuracy=True))


if __name__ == '__main__':
    main()
