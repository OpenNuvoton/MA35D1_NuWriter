# NOTE: This script is test under Python 3.x

__copyright__ = "Copyright (C) 2020~2021 Nuvoton Technology Corp. All rights reserved"
__version__ = "v0.36"

import os
import sys
import argparse
import json
import crcmod
from Crypto.Cipher import AES
import hashlib
import ecdsa
import binascii
from datetime import datetime
import random
import shutil
from tqdm import tqdm
from xusbcom import XUsbComList
from concurrent.futures import ThreadPoolExecutor, as_completed
from UnpackImage import UnpackImage
from collections import namedtuple
from struct import unpack
import time
import platform
# for debug
import usb.core
import usb.util

ACK = 0x55AA55AA
TRANSFER_SIZE = 4096
MAX_HEADER_IMG = 4
# SPI NOR align for erase/program starting address
SPINOR_ALIGN = 4096

# Storage device type
DEV_DDR_SRAM = 0
DEV_NAND = 1
DEV_SD_EMMC = 2
DEV_SPINOR = 3
DEV_SPINAND = 4
DEV_OTP = 6
DEV_USBH = 7
DEV_UNKNOWN = 0xFF

# For OTP programming
ACT_LOAD = 1
ACT_WRITE = 2
ACT_ERASE = 3
ACT_READ = 4
ACT_MSC = 5

# Command options
OPT_NONE = 0
OPT_SCRUB = 1       # For erase, use with care
OPT_WITHBAD = 1     # For read
OPT_EXECUTE = 2     # For write
OPT_VERIFY = 3      # For write
OPT_UNPACK = 4      # For pack
OPT_RAW = 5         # For write
OPT_EJECT = 6       # For msc
OPT_STUFF = 7       # For stuff pack

# OPT block definitions
OPT_OTPBLK1 = 0x100
OPT_OTPBLK2 = 0x200
OPT_OTPBLK3 = 0x400
OPT_OTPBLK4 = 0x800
OPT_OTPBLK5 = 0x1000
OPT_OTPBLK6 = 0x2000
OPT_OTPBLK7 = 0x4000
OPT_OTPKEY = 0x8000

# Image type definitions
IMG_DATA = 0
IMG_TFA = 1
IMG_UBOOT = 2
IMG_LINUX = 3
IMG_DDR = 4
IMG_TEE = 5
IMG_DTB = 6

# If attach is a must. maybe better for real chip.
# devices = []
mp_mode = False

WINDOWS_PATH = "C:\\Program Files (x86)\\Nuvoton Tools\\NuWriter\\"
LINUX_PATH = "/usr/share/nuwriter/"

def conv_env(env_file_name, blk_size) -> bytearray:

    try:
        with open(env_file_name, "r") as env_file:
            env_data = env_file.read().splitlines()
    except (IOError, OSError) as err:
        print(f"Open {env_file_name} failed")
        sys.exit(err)

    out = bytearray(4)   # Reserved for CRC
    for lines in env_data:
        out += bytes(lines, 'ascii')
        out += b'\x00'
    out += b'\x00'
    out += b'\xFF' * (blk_size - len(out))

    crc32_func = crcmod.predefined.mkCrcFun('crc-32')
    checksum = crc32_func(out[4:])
    out[0:4] = checksum.to_bytes(4, byteorder="little")

    return out


def get_dpm(dpm) -> int:
    return {
        'a35sdsdis': 0x00000001,
        'a35sdslock': 0x00000002,
        'a35sndsdis':  0x00000004,
        'a35sndslock': 0x00000008,
        'a35nsdsdis': 0x00000010,
        'a35nsdslock': 0x00000020,
        'a35nsndsdis': 0x00000040,
        'a35nsndslock': 0x00000080,
        'm4dsdis': 0x00000100,
        'm4dslock': 0x00000200,
        'm4ndsdis': 0x00000400,
        'm4ndslock': 0x00000800,
        'extdis': 0x00001000,
        'extlock': 0x00002000,
        'exttdis': 0x00004000,
        'exttlock': 0x00008000,
        'giccfgsdis': 0x00010000,
        'giccfgslock': 0x00020000
    }.get(dpm, 0)


def get_plm(plm) -> int:
    return {
        'oem': 0x1,
        'deploy': 0x3,
        'rma':  0x7,
        'prma': 0xF
    }.get(plm, 0)


def conv_otp(opt_file_name) -> (bytearray, int):
    try:
        with open(opt_file_name, "r") as json_file:
            try:
                d = json.load(json_file)
            except json.decoder.JSONDecodeError as err:
                print(f"{opt_file_name} parsing error")
                sys.exit(err)
    except (IOError, OSError) as err:
        print(f"Open {opt_file_name} failed")
        sys.exit(err)
    # Bootcfg, DPM, PLM, and PWD 4 bytes each, MAC addr 8 bytes each, sec/nsec 88 bytes each
    data = bytearray(208)

    option = 0
    for key in d.keys():
        if key == 'boot_cfg':
            cfg_val = 0
            for sub_key in d['boot_cfg'].keys():
                if sub_key == 'posotp':
                    if d['boot_cfg']['posotp'] == 'enable':
                        cfg_val |= 1
                if sub_key == 'qspiclk':
                    if d['boot_cfg']['qspiclk'] == '60mhz':
                        cfg_val |= 2
                if sub_key == 'wdt0en':
                    if d['boot_cfg']['wdt0en'] == 'enable':
                        cfg_val |= 4
                if sub_key == 'uart0en':
                    if d['boot_cfg']['uart0en'] == 'enable':
                        cfg_val |= 0x10
                if sub_key == 'sd0bken':
                    if d['boot_cfg']['sd0bken'] == 'enable':
                        cfg_val |= 0x20
                if sub_key == 'tsiimg':
                    if d['boot_cfg']['tsiimg'] == 'enable':
                        cfg_val |= 0x40
                if sub_key == 'tsidbg':
                    if d['boot_cfg']['tsidbg'] == 'enable':
                        cfg_val |= 0x80
                if sub_key == 'bootsrc':
                    if d['boot_cfg']['bootsrc'] == 'sd' or d['boot_cfg']['bootsrc'] == 'emmc':
                        cfg_val |= 0x400
                    elif d['boot_cfg']['bootsrc'] == 'nand':
                        cfg_val |= 0x800
                    elif d['boot_cfg']['bootsrc'] == 'usb':
                        cfg_val |= 0xC00
                if sub_key == 'page':
                    if d['boot_cfg']['page'] == '4k':
                        cfg_val |= 0x1000
                    elif d['boot_cfg']['page'] == '8k':
                        cfg_val |= 0x2000
                    elif d['boot_cfg']['page'] == 'ignore':
                        cfg_val |= 0x3000
                if sub_key == 'option':
                    if d['boot_cfg']['option'] == 'sd1' or d['boot_cfg']['option'] == 'emmc1' or \
                       d['boot_cfg']['option'] == 't12' or d['boot_cfg']['option'] == 'spinand4':
                        cfg_val |= 0x4000
                    elif d['boot_cfg']['option'] == 't24' or d['boot_cfg']['option'] == 'spinor1':
                        cfg_val |= 0x8000
                    elif d['boot_cfg']['option'] == 'ignore' or d['boot_cfg']['option'] == 'spinor4':
                        cfg_val |= 0xC000
                if sub_key == 'secboot':
                    if d['boot_cfg']['secboot'] == 'disable':
                        cfg_val |= 0x5A000000
            data[0:4] = cfg_val.to_bytes(4, byteorder='little')
            option |= OPT_OTPBLK1
        elif key == 'dpm_plm':
            for sub_key in d['dpm_plm'].keys():
                if sub_key == 'dpm':
                    dpm_val = 0
                    for dpm_key in d['dpm_plm']['dpm'].keys():
                        dpm_val |= get_dpm(dpm_key)
                    if dpm_val != 0:
                        data[4:8] = dpm_val.to_bytes(4, byteorder='little')
                elif sub_key == 'plm':
                    plm_val = get_plm(d['dpm_plm']['plm'])
                    if plm_val != 0:
                        data[8:12] = plm_val.to_bytes(4, byteorder='little')
            option |= OPT_OTPBLK2
        elif key == 'mac0':
            data[12:18] = bytes.fromhex(d['mac0'])
            option |= OPT_OTPBLK3
        elif key == 'mac1':
            data[20:26] = bytes.fromhex(d['mac1'])
            option |= OPT_OTPBLK4
        elif key == 'dplypwd':
            data[28:32] = bytes.fromhex(d['dplypwd'])
            option |= OPT_OTPBLK5
        elif key == 'sec':
            newkey = bytes.fromhex(d['sec'])
            newkey += b'\x00' * (88 - len(newkey))
            print("===========")
            print(len(newkey))
            data[32:120] = newkey
            option |= OPT_OTPBLK6
        elif key == 'nonsec':
            newkey = bytes.fromhex(d['nonsec'])
            newkey += b'\x00' * (88 - len(newkey))
            data[120:208] = newkey
            option |= OPT_OTPBLK7
        elif key == 'huk0':
            newkey = bytes.fromhex(d['huk0']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['huk0']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x00\x00\x00\x00'
            newkey += int(d['huk0']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'huk1':
            newkey = bytes.fromhex(d['huk1']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['huk1']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x01\x00\x00\x00'
            newkey += int(d['huk1']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'huk2':
            newkey = bytes.fromhex(d['huk2']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['huk2']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x02\x00\x00\x00'
            newkey += int(d['huk2']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'key3':
            newkey = bytes.fromhex(d['key3']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['key3']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x03\x00\x00\x00'
            newkey += int(d['key3']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'key4':
            newkey = bytes.fromhex(d['key4']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['key4']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x04\x00\x00\x00'
            newkey += int(d['key4']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'key5':
            newkey = bytes.fromhex(d['key5']['key'])
            newkey += b'\x00' * (32 - len(newkey))
            newkey += int(d['key5']['size'], 0).to_bytes(4, byteorder='little')
            newkey += b'\x05\x00\x00\x00'
            newkey += int(d['key5']['meta'], 0).to_bytes(4, byteorder='little')
            data += newkey
        elif key == 'publicx':
            data += bytes.fromhex(d['publicx'])
            data += b'\x00\x01\x00\x00'    # 256 bits
            data += b'\x06\x00\x00\x00'
            data += b'\x11\x06\x04\x80'
        elif key == 'publicy':
            data += bytes.fromhex(d['publicy'])
            data += b'\x00\x01\x00\x00'    # 256 bits
            data += b'\x07\x00\x00\x00'
            data += b'\x11\x06\x04\x80'
        elif key == 'aeskey':
            data += bytes.fromhex(d['aeskey'])
            data += b'\x00\x01\x00\x00'    # 256 bits
            data += b'\x07\x00\x00\x00'
            data += b'\x11\x06\x00\x80'

    if len(data) > 208:
        option |= OPT_OTPKEY
    return data, option


def __img_erase(dev, media, start, length, option) -> int:

    nand_align, spinand_align = dev.get_align()

    if (media == DEV_NAND and  nand_align == 0) or \
       (media == DEV_SPINAND and spinand_align == 0):
        print("Unable to get block size")
        return -1

    if (media == DEV_NAND and start % nand_align != 0) or\
       (media == DEV_SPINAND and start % spinand_align != 0) or \
       (media == DEV_SPINOR and start % SPINOR_ALIGN != 0):
        print("Starting address must be block aligned")
        return -1

    cmd = start.to_bytes(8, byteorder='little')
    cmd += length.to_bytes(8, byteorder='little')
    cmd += ACT_ERASE.to_bytes(4, byteorder='little')
    cmd += option.to_bytes(4, byteorder='little')

    dev.set_media(media)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1
    bar = tqdm(total=100, position=dev.get_id(), ascii=True)
    previous_progress = 0
    while True:
        # xusb ack with total erase progress.
        ack = dev.read(4)
        if int.from_bytes(ack, byteorder="little") <= 100:
            bar.update(int.from_bytes(ack, byteorder="little") - previous_progress)
            previous_progress = int.from_bytes(ack, byteorder="little")
        if int.from_bytes(ack, byteorder="little") == 100:
            break
    bar.close()
    return 0


# default erase all (count=0)
def do_img_erase(media, start, length=0, option=OPT_NONE) -> None:
    global mp_mode

    # devices = XUsbComList(attach_all=mp_mode).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__img_erase, dev, media, start, length, option) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully erased {success} device(s)")
    if failed > 0:
        print(f"Failed to erase {failed} device(s)")


def __otp_program(dev, opt_writer, opt_data, option) -> int:

    img_length = len(opt_writer)
    cmd = b'\x00\x40\x00\x20\x00\x00\x00\x00'
    cmd += img_length.to_bytes(8, byteorder='little')
    cmd += ACT_LOAD.to_bytes(4, byteorder='little')
    cmd += option.to_bytes(4, byteorder='little')
    dev.set_media(DEV_OTP)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1

    for offset in range(0, img_length, TRANSFER_SIZE):
        xfer_size = TRANSFER_SIZE if offset + TRANSFER_SIZE < img_length else img_length - offset
        dev.write(opt_writer[offset: offset + xfer_size])
        ack = dev.read(4)
        if ack != xfer_size:
            print("Acked size error")
            return -1

    img_length = len(opt_data)

    cmd = b'\x00' * 8
    cmd += img_length.to_bytes(8, byteorder='little')
    cmd += ACT_WRITE.to_bytes(4, byteorder='little')
    cmd += option.to_bytes(4, byteorder='little')

    dev.set_media(DEV_OTP)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1
    # There's no way to tell the progress...
    dev.write(opt_data)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != img_length:
        print("Acked size error")
        return -1
    return 0


def do_otp_program(opt_file_name) -> None:
    global mp_mode

    # devices = XUsbComList(attach_all=mp_mode).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)

    try:
        with open("opt_writer.bin", "r") as writer_file:
            opt_writer = writer_file.read()
    except (IOError, OSError) as err:
        print(f"Open {opt_file_name} failed")
        sys.exit(err)

    otp_data, option = conv_otp(opt_file_name)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__otp_program, dev, opt_writer, otp_data, option) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully programmed {success} device(s)")
    if failed > 0:
        print(f"Failed to program {failed} device(s)")


def __pack_program(dev, media, pack_image, option) -> int:

    nand_align, spinand_align = dev.get_align()
    image_cnt = pack_image.img_count()

    if (media == DEV_NAND and  nand_align == 0) or \
       (media == DEV_SPINAND and spinand_align == 0):
        print("Unable to get block size")
        return -1

    for i in range(image_cnt):
        img_length, img_start, img_type = pack_image.img_attr(i)
        if (media == DEV_NAND and img_start % nand_align != 0) or \
           (media == DEV_SPINAND and img_start % spinand_align != 0) or \
           (media == DEV_SPINOR and img_start % SPINOR_ALIGN != 0):
            print("Starting address must be block aligned")
            return -1
        time.sleep(1)
        dev.set_media(media)
        cmd = img_start.to_bytes(8, byteorder='little')
        cmd += img_length.to_bytes(8, byteorder='little')
        cmd += ACT_WRITE.to_bytes(4, byteorder='little')
        cmd += img_type.to_bytes(4, byteorder='little')

        dev.write(cmd)
        ack = dev.read(4)
        if int.from_bytes(ack, byteorder="little") != ACK:
            print("Receive ACK error")
            return -1
        text = f"Programming {i}/{image_cnt}"
        bar = tqdm(total=img_length, position=dev.get_id(), ascii=True, desc=text)
        for offset in range(0, img_length, TRANSFER_SIZE):
            xfer_size = TRANSFER_SIZE if offset + TRANSFER_SIZE < img_length else img_length - offset
            dev.write(pack_image.img_content(i, offset, xfer_size))
            ack = dev.read(4)
            if int.from_bytes(ack, byteorder="little") != xfer_size:
                print("Ack size error")
                return -1
            bar.update(xfer_size)
        bar.close()
        dev.read(4)
        if option == OPT_VERIFY:
            dev.set_media(media)
            cmd = img_start.to_bytes(8, byteorder='little')
            cmd += img_length.to_bytes(8, byteorder='little')
            cmd += ACT_READ.to_bytes(4, byteorder='little')
            cmd += b'\x00' * 4

            dev.write(cmd)
            ack = dev.read(4)
            if int.from_bytes(ack, byteorder="little") != ACK:
                print("Receive ACK error")
                return -1
            remain = img_length
            text = f"Verifying {i}/{image_cnt}"
            bar = tqdm(total=img_length, position=dev.get_id(), ascii=True, desc=text)
            while remain > 0:
                ack = dev.read(4)
                # Get the transfer length of next read
                xfer_size = int.from_bytes(ack, byteorder="little")

                data = dev.read(xfer_size)
                dev.write(xfer_size.to_bytes(4, byteorder='little'))
                offset = img_length - remain

                # For SD/eMMC
                if xfer_size > remain:
                    xfer_size = remain
                    data = data[0: remain]

                if data != bytearray(pack_image.img_content(i, offset, xfer_size)):
                    print("Verify failed")
                    return -1
                remain -= xfer_size
                bar.update(xfer_size)
            bar.close()
    return 0


def do_pack_program(media, pack_file_name, option=OPT_NONE) -> None:
    global mp_mode

    # devices = XUsbComList(attach_all=mp_mode).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)

    pack_image = UnpackImage(pack_file_name)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__pack_program, dev, media, pack_image, option) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully programmed {success} device(s)")
    if failed > 0:
        print(f"Failed to program {failed} device(s)")


def __img_program(dev, media, start, img_data, option) -> int:

    nand_align, spinand_align = dev.get_align()

    if (media == DEV_NAND and  nand_align == 0) or \
       (media == DEV_SPINAND and spinand_align == 0):
        print("Unable to get block size")
        return -1

    if (media == DEV_NAND and start % nand_align != 0) or\
       (media == DEV_SPINAND and start % spinand_align != 0) or \
       (media == DEV_SPINOR and start % SPINOR_ALIGN != 0):
        print("Starting address must be block aligned")
        return -1

    img_length = len(img_data)
    print(f"image length is {img_length}")
    cmd = start.to_bytes(8, byteorder='little')
    cmd += img_length.to_bytes(8, byteorder='little')
    cmd += ACT_WRITE.to_bytes(4, byteorder='little')
    if option == OPT_EXECUTE:
        cmd += option.to_bytes(4, byteorder='little')
    else:
        cmd += b'\x00' * 4

    dev.set_media(media)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1

    # Set ascii=True is for Windows cmd terminal, position > 0 doesn't work as expected in cmd though...
    bar = tqdm(total=img_length, position=dev.get_id(), ascii=True, desc="Programming")
    for offset in range(0, img_length, TRANSFER_SIZE):
        xfer_size = TRANSFER_SIZE if offset + TRANSFER_SIZE < img_length else img_length - offset
        dev.write(img_data[offset: offset + xfer_size])
        ack = dev.read(4)
        if int.from_bytes(ack, byteorder="little") != xfer_size:
            print("Ack size error")
            return -1
        bar.update(xfer_size)
    dev.read(4)
    bar.close()
    if option == OPT_VERIFY:
        dev.set_media(media)
        cmd = start.to_bytes(8, byteorder='little')
        cmd += img_length.to_bytes(8, byteorder='little')
        cmd += ACT_READ.to_bytes(4, byteorder='little')
        cmd += b'\x00' * 4

        dev.write(cmd)
        ack = dev.read(4)
        if int.from_bytes(ack, byteorder="little") != ACK:
            print("Receive ACK error")
            return -1

        remain = img_length
        bar = tqdm(total=img_length, position=dev.get_id(), ascii=True, desc="Verifying")
        while remain > 0:
            ack = dev.read(4)
            # Get the transfer length of next read
            xfer_size = int.from_bytes(ack, byteorder="little")

            data = dev.read(xfer_size)
            dev.write(xfer_size.to_bytes(4, byteorder='little'))    #ack
            offset = img_length - remain

            # For SD/eMMC
            if xfer_size > remain:
                xfer_size = remain
                data = data[0: remain]

            if data != bytearray(img_data[offset: offset + xfer_size]):
                print("Verify failed")
                return -1
            remain -= xfer_size
            bar.update(xfer_size)
        print("Verify pass")
        bar.close()
    return 0


def do_img_program(media, start, image_file_name, option=OPT_NONE) -> None:
    global mp_mode

    # devices = XUsbComList(attach_all=mp_mode).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)
    try:
        with open(image_file_name, "rb") as image_file:
            img_data = image_file.read()

    except (IOError, OSError) as err:
        print(f"Open {image_file_name} failed")
        sys.exit(err)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__img_program, dev, media, start, img_data, option) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully programmed {success} device(s)")
    if failed > 0:
        print(f"Failed to program {failed} device(s)")


def do_img_read(media, start, out_file_name, length=0x1, option=OPT_NONE) -> None:
    # only support read from 1 device
    # devices = XUsbComList(attach_all=False).get_dev()
    _XUsbComList = XUsbComList(attach_all=False)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)
    # Only support one device in read function
    dev = devices[0]

    cmd = start.to_bytes(8, byteorder='little')
    cmd += length.to_bytes(8, byteorder='little')
    cmd += ACT_READ.to_bytes(4, byteorder='little')
    cmd += option.to_bytes(4, byteorder='little')

    dev.set_media(media)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1
    # FIXME: Don't know real length for "read all"
    bar = tqdm(total=length, ascii=True)
    data = b''
    remain = length

    while remain > 0:
        ack = dev.read(4)
        # Get the transfer length of next read
        xfer_size = int.from_bytes(ack, byteorder="little")

        data += dev.read(xfer_size)
        dev.write(xfer_size.to_bytes(4, byteorder='little'))    # ack
        remain -= xfer_size
        bar.update(xfer_size)
    try:
        with open(out_file_name, "wb") as out_file:
            out_file.write(data[0:length])
    except (IOError, OSError) as err:
        print(f"Open {out_file_name} failed")
        sys.exit(err)

    bar.close()


def __attach(dev, ini_data, xusb_data) -> int:
    ini_len = len(ini_data)
    out = int(ini_len).to_bytes(4, byteorder="little")
    out += b'\x00\x00\x03\x28'  # Execute address is 0x28030000
    dev.write(out)
    dev.write(ini_data)

    in_buf = dev.read(4)
    if int.from_bytes(in_buf, byteorder="little") != ini_len:
        print("Length error")
        return -1
    in_buf = dev.read(4)
    if int.from_bytes(in_buf, byteorder="little") != ACK:
        print("Ack error")
        return -1

    xusb_len = len(xusb_data)
    out = int(xusb_len).to_bytes(4, byteorder="little")
    #out += b'\x00\x00\x00\x90'  # Execute address is 0x90000000
    out += b'\x00\x00\x00\x87'  # Execute address is 0x90000000
    dev.write(out)
    for offset in range(0, xusb_len, TRANSFER_SIZE):
        xfer_size = TRANSFER_SIZE if offset + TRANSFER_SIZE < xusb_len else xusb_len - offset

        dev.write(xusb_data[offset: offset + xfer_size])
        if offset + xfer_size != xusb_len:  # Ignore the ack of last packet
            ack = dev.read(4)
            if int.from_bytes(ack, byteorder="little") != xfer_size:
                _ack = int.from_bytes(ack, byteorder="little")
                print(f"Ack size error {_ack} {xfer_size}")
                return -1

    return 0


def __get_info(dev) -> int:
    try:
        info = dev.get_info()
    except usb.core.USBError as err:
        sys.exit(err)

    _info_struct = namedtuple('_info_struct',
                              'page_per_blk page_size blk_cnt bad_clk_cnt oob_size usr_cfg0 spi_id usr_cfg1 quad_cmd \
                              read_sts_cmd write_sts_cmd sts_val dummy_byte blk rsv use_cfg2 snand_id snand_page_size \
                              snand_oob snand_quad_cmd snand_read_sts_cmd snand_write_sts_cmd snand_sts_val \
                              snand_dummy_byte snand_blk_cnt snand_page_per_blk')
    info_struct = _info_struct._make(unpack('<IIIIIIIIBBBBIIIIIHHBBBBIII', info))
    print("==== NAND ====")
    print("Page per block: " + str(info_struct.page_per_blk))
    print("Page size: " + str(info_struct.page_size))
    print("Block per flash: " + str(info_struct.blk_cnt))
    print("Bad block count: " + str(info_struct.bad_clk_cnt))
    print("Spare size: " + str(info_struct.oob_size))
    print("Is uer config: " + str(info_struct.usr_cfg0))

    print("==== SPI NOR ====")
    print("ID: " + str(info_struct.spi_id))
    print("Is uer config: " + str(info_struct.usr_cfg1))
    print("Quad read cmd: " + str(info_struct.quad_cmd))
    print("Read sts cmd: " + str(info_struct.read_sts_cmd))
    print("Write sts cmd: " + str(info_struct.write_sts_cmd))
    print("Sts value: " + str(info_struct.sts_val))
    print("Dummy byte: " + str(info_struct.dummy_byte))

    print("==== eMMC ====")
    print("Block: " + str(info_struct.blk))
    print("Reserved: " + str(info_struct.rsv))

    print("==== SPI NAND ====")
    print("Is uer config: " + str(info_struct.snand_dummy_byte))
    print("ID: " + str(info_struct.snand_id))
    print("Page size: " + str(info_struct.snand_page_size))
    print("Spare size: " + str(info_struct.snand_oob))
    print("Quad read cmd: " + str(info_struct.snand_quad_cmd))
    print("Read sts cmd: " + str(info_struct.snand_read_sts_cmd))
    print("Write sts cmd: " + str(info_struct.snand_write_sts_cmd))
    print("Sts value: " + str(info_struct.snand_sts_val))
    print("Dummy byte: " + str(info_struct.snand_dummy_byte))
    print("Block per flash: " + str(info_struct.snand_blk_cnt))
    print("Page per block: " + str(info_struct.snand_page_per_blk))

    dev.set_align(info_struct.page_size * info_struct.page_per_blk,
                  info_struct.snand_page_size * info_struct.snand_page_per_blk)

    return 0


def do_attach(ini_file_name, mp_mode1=False) -> None:
    init_location = "missing"
    if os.path.exists(ini_file_name):  # default use the init file in current directory
        init_location = ini_file_name
    else:
        if platform.system() == 'Windows':
            if os.path.exists(WINDOWS_PATH + "ddrimg\\" + ini_file_name):
                init_location = WINDOWS_PATH + "ddrimg\\" + ini_file_name
        elif platform.system() == 'Linux':
            if os.path.exists(LINUX_PATH + "ddrimg/" + ini_file_name):
                init_location = LINUX_PATH + "ddrimg/" + ini_file_name

    if init_location == "missing":
        print(f"Cannot find {ini_file_name}")
        sys.exit(3)
    try:
        with open(init_location, "rb") as ini_file:
            ini_data = ini_file.read()
    except (IOError, OSError) as err:
        print(f"Open {ini_file_name} failed")
        sys.exit(err)
    xusb_location = "missing"
    if os.path.exists("xusb.bin"):  # default use the xusb.bin in current directory
        xusb_location = "xusb.bin"
    else:
        if platform.system() == 'Windows':
            if os.path.exists(WINDOWS_PATH + "xusb.bin"):
                xusb_location = WINDOWS_PATH + "xusb.bin"
        elif platform.system() == 'Linux':
            if os.path.exists(LINUX_PATH + "xusb.bin"):
                xusb_location = LINUX_PATH + "xusb.bin"
    if xusb_location == "missing":
        print("Cannot find xusb.bin")
        sys.exit(3)

    try:
        with open(xusb_location, "rb") as xusb_file:
            xusb_data = xusb_file.read()
    except (IOError, OSError) as err:
        print("Open xusb.bin failed")
        sys.exit(err)

    # devices = XUsbComList(attach_all=mp_mode1).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode1)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__attach, dev, ini_data, xusb_data) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures, timeout=2):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully attached {success} device(s)")
    if failed > 0:
        print(f"Failed to attach {failed} device(s)")
    if success == 0:
        return

    # print("Sleep 2 second, let PC re-enumerate")
    # time.sleep(2)
    # For Palladium emulation
    # info = dev.get_info()
    # print('Press Enter after PC re-enumerate done', end='')
    # input()
    time.sleep(1)
    print("Get device info")

    # devices = XUsbComList(attach_all=mp_mode1).get_dev()
    _XUsbComListNew = XUsbComList(attach_all=mp_mode1)
    devices = _XUsbComListNew.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__get_info, dev) for dev in devices]

    success = 0
    failed = 0
    for future in as_completed(futures, timeout=2):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print(f"Successfully get info from {success} device(s)")


def do_unpack(pack_file_name) -> None:

    now = datetime.now()
    pack_image = UnpackImage(pack_file_name)
    image_cnt = pack_image.img_count()

    try:
        os.mkdir(now.strftime("%m%d-%H%M%S%f"))
    except (IOError, OSError) as err:
        sys.exit(err)

    for i in range(image_cnt):
        img_length, _, _ = pack_image.img_attr(i)
        try:
            with open(now.strftime("%m%d-%H%M%S%f") + "/img" + str(i) + ".bin", "wb") as img_file:
                img_file.write(pack_image.img_content(i, 0, img_length))
        except (IOError, OSError) as err:
            print("Create output image file failed")
            sys.exit(err)
    try:
        os.unlink("unpack")
    except (IOError, OSError):
        pass
    try:
        os.symlink(now.strftime("%m%d-%H%M%S%f"), "unpack")
    except (IOError, OSError):
        print("Create symbolic folder unpack failed")
    print("Unpack images to directory {} complete".format(now.strftime("%m%d-%H%M%S%f")))


def do_stuff(cfg_file) -> None:
    now = datetime.now()

    try:
        with open(cfg_file, "r") as json_file:
            try:
                d = json.load(json_file)
            except json.decoder.JSONDecodeError as err:
                print(f"{cfg_file} parsing error")
                sys.exit(err)
    except (IOError, OSError) as err:
        print(f"Open {cfg_file} failed")
        sys.exit(err)

    try:
        os.mkdir(now.strftime("%m%d-%H%M%S%f"))
        pack_file = open(now.strftime("%m%d-%H%M%S%f") + "/pack.bin", "wb")
    except (IOError, OSError) as err:
        sys.exit(err)

    offset = 0
    out = bytearray()

    # Start stuffing image
    for img in d["image"]:
        try:
            with open(img["file"], "rb") as img_file:
                data = img_file.read()
        except (IOError, OSError) as err:
            print(f"Open {img_file} failed")
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(err)
        if int(img["offset"], 0) < offset:
            print(f"Please place the files in {cfg_file} based on the ascending offset")
            sys.exit(4)
        elif int(img["offset"], 0) > offset:
            out += b'\xFF' * (int(img["offset"], 0) - offset)
            offset = int(img["offset"], 0)
        out += data
        offset += len(data)
    pack_file.write(out)
    pack_file.close()
    try:
        os.unlink("pack")
    except (IOError, OSError):
        pass
    try:
        os.symlink(now.strftime("%m%d-%H%M%S%f"), "pack")
    except (IOError, OSError):
        print("Create symbolic folder pack failed")
    print("Generate pack file in directory {} complete".format(now.strftime("%m%d-%H%M%S%f")))


def do_pack(cfg_file) -> None:
    now = datetime.now()

    try:
        with open(cfg_file, "r") as json_file:
            try:
                d = json.load(json_file)
            except json.decoder.JSONDecodeError as err:
                print(f"{cfg_file} parsing error")
                sys.exit(err)
    except (IOError, OSError) as err:
        print(f"Open {cfg_file} failed")
        sys.exit(err)

    try:
        os.mkdir(now.strftime("%m%d-%H%M%S%f"))
        pack_file = open(now.strftime("%m%d-%H%M%S%f") + "/pack.bin", "wb")
    except (IOError, OSError) as err:
        sys.exit(err)

    out = bytearray(b'\x20\x54\x56\x4e' + b'\xFF' * 12)  # NVT + CRC32 + image count + 4 reserved bytes

    # Start packing image
    img_cnt = 0
    for img in d["image"]:
        try:
            with open(img["file"], "rb") as img_file:
                data = img_file.read()
        except (IOError, OSError) as err:
            print(f"Open {img_file} failed")
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(err)

        img_cnt = img_cnt + 1

        img_len = len(data)
        out += img_len.to_bytes(8, byteorder="little")
        try:
            out += int(img["offset"], 0).to_bytes(8, byteorder="little")
        except ValueError as err:
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(err)
        out += img["type"].to_bytes(4, byteorder="little")
        out += b'\xFF' * 4
        out += data
        # Always put image start @ 16 byte boundary
        pad = 16 - (img_len + 8) & 0xF
        if pad != 16:
            out += b'\xFF' * pad

    # Fill image count
    out[8:12] = img_cnt.to_bytes(4, byteorder="little")

    # Fill CRC field
    crc32_func = crcmod.predefined.mkCrcFun('crc-32')
    checksum = crc32_func(out[8:])
    out[4:8] = checksum.to_bytes(4, byteorder="little")

    pack_file.write(out)
    pack_file.close()
    try:
        os.unlink("pack")
    except (IOError, OSError):
        pass
    try:
        os.symlink(now.strftime("%m%d-%H%M%S%f"), "pack")
    except (IOError, OSError):
        print("Create symbolic folder pack failed")
    print("Generate pack file in directory {} complete".format(now.strftime("%m%d-%H%M%S%f")))


def do_convert(cfg_file) -> None:

    now = datetime.now()

    try:
        with open(cfg_file, "r") as json_file:
            try:
                d = json.load(json_file)
            except json.decoder.JSONDecodeError as err:
                print(f"{cfg_file} parsing error")
                sys.exit(err)
    except (IOError, OSError) as err:
        print(f"Open {cfg_file} failed")
        sys.exit(err)
    try:
        os.mkdir(now.strftime("%m%d-%H%M%S%f"))
    except (IOError, OSError) as err:
        print("Create output directory failed")
        sys.exit(err)

    if "header" in d:
        out = bytearray(b'\x20\x54\x56\x4e' + b'\x00' * 8)  # NVT + CRC + LEN
        try:
            out += int(d["header"]["version"], 0).to_bytes(4, byteorder="little")
            # Fill SPI flash info
            out += int(d["header"]["spiinfo"]["pagesize"], 0).to_bytes(2, byteorder="little")
            out += int(d["header"]["spiinfo"]["sparearea"], 0).to_bytes(2, byteorder="little")
            out += int(d["header"]["spiinfo"]["pageperblk"], 0).to_bytes(2, byteorder="little")
            out += int(d["header"]["spiinfo"]["quadread"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["readsts"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["writests"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["stsvalue"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["dummy1"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["dummy2"], 0).to_bytes(1, byteorder="little")
            out += int(d["header"]["spiinfo"]["suspintvl"], 0).to_bytes(1, byteorder="little")
            out += b'\xFF' * 3  # 3 reserved bytes
            out += int(d["header"]["entrypoint"], 0).to_bytes(4, byteorder="little")
        except ValueError as err:
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(err)

        out += b'\xFF' * 4  # Reserve 4 bytes for image count

        # Generate key file iff secure boot is enabled
        if d["header"]["secureboot"] == 'yes':

            try:
                key_file = open(now.strftime("%m%d-%H%M%S%f") + "/header_key.txt", "w+")
            except (IOError, OSError) as err:
                print("Create key file failed")
                shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                sys.exit(err)

            if "aeskey" in d["header"]:
                try:
                    aeskey = bytes.fromhex(d["header"]["aeskey"])
                except ValueError as err:
                    sys.exit(err)
            else:
                aeskey = ''.join(['%x' % random.randrange(16) for _ in range(0, 64)])
                aeskey = binascii.unhexlify(bytes(aeskey, 'utf-8'))
            key_file.write("AES key:\n" + str.upper(aeskey.hex()))

            if "ecdsakey" in d["header"]:
                try:
                    sk = ecdsa.SigningKey.from_string(bytes.fromhex(d["header"]["ecdsakey"]),
                                                      curve=ecdsa.NIST256p,
                                                      hashfunc=hashlib.sha256)
                except ValueError as err:
                    sys.exit(err)
            else:
                sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc=hashlib.sha256)
            key_file.write("\nECDSA private key:\n" + str.upper(sk.to_string().hex()))

            vk = sk.verifying_key
            key_file.write("\nECDSA public key:\n" + format(vk.pubkey.point.x(), 'X') +
                           "\n" + format(vk.pubkey.point.y(), 'X') + "\n")

            key_file.close()

        img_cnt = len(d["header"]["image"])
        if img_cnt > MAX_HEADER_IMG:
            print("Can process 4 images in header max")
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(2)

        # Fill image information
        for i in range(img_cnt):
            img = d["header"]["image"][i]
            try:
                with open(img["file"], "rb") as img_file:
                    data = img_file.read()
            except (IOError, OSError) as err:
                print("Open image file failed")
                shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                sys.exit(err)
            try:
                out += int(img["offset"], 0).to_bytes(4, byteorder="little")
                out += int(img["loadaddr"], 0).to_bytes(4, byteorder="little")
                out += os.path.getsize(img["file"]).to_bytes(4, byteorder="little")
                out += int(img["type"]).to_bytes(4, byteorder="little")
            except ValueError as err:
                shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                sys.exit(err)

            if d["header"]["secureboot"] == 'yes':

                # Use CFB and each image is process independently, so call new() for every image
                aes_enc = AES.new(aeskey, AES.MODE_CFB, b'\x00' * 16, segment_size=128)
                data_out = aes_enc.encrypt(data)
                # R & S
                out += sk.sign(data_out)

                # Write encrypt image
                try:
                    with open(now.strftime("%m%d-%H%M%S%f") + '/enc_' + os.path.basename(img["file"]), "wb") as enc_file:
                        enc_file.write(data_out)
                except (IOError, OSError) as err:
                    print("Create encrypt file failed")
                    shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                    sys.exit(err)

            else:
                out += b'\xFF' * 64  # Just pack 0xFF if secure boot is disabled

        # Fill header length
        out[8:12] = int(len(out) - 8).to_bytes(4, byteorder="little")
        # Fill image count
        out[36:40] = img_cnt.to_bytes(4, byteorder="little")
        # Fill header checksum
        crc32_func = crcmod.predefined.mkCrcFun('crc-32')
        out[4:8] = crc32_func(out[8:]).to_bytes(4, byteorder="little")

        try:
            with open(now.strftime("%m%d-%H%M%S%f") + "/header.bin", "wb") as header_file:
                header_file.write(out)
        except (IOError, OSError) as err:
            print("Create header file failed")
            sys.exit(err)

    if "env" in d:
        try:
            with open(now.strftime("%m%d-%H%M%S%f") + "/uboot-env.bin", "wb") as out_file:
                out_file.write(conv_env(d["env"]["file"], int(d["env"]["blksize"], 0)))
        except (IOError, OSError, ValueError) as err:
            print("Create header file failed")
            sys.exit(err)
    # Misc images
    if "data" in d:
        try:
            key_file = open(now.strftime("%m%d-%H%M%S%f") + "/data_key.txt", "w+")
        except (IOError, OSError) as err:
            print("Create key file failed")
            shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
            sys.exit(err)

        if "aeskey" in d["data"]:
            try:
                aeskey = bytes.fromhex(d["data"]["aeskey"])
            except ValueError as err:
                sys.exit(err)
        else:
            aeskey = ''.join(['%x' % random.randrange(16) for _ in range(0, 64)])
            aeskey = binascii.unhexlify(bytes(aeskey, 'utf-8'))
        key_file.write("AES key:\n" + str.upper(aeskey.hex()))

        if "ecdsakey" in d["data"]:
            try:
                sk = ecdsa.SigningKey.from_string(bytes.fromhex(d["data"]["ecdsakey"]),
                                                  curve=ecdsa.NIST256p,
                                                  hashfunc=hashlib.sha256)
            except ValueError as err:
                sys.exit(err)
        else:
            sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p, hashfunc=hashlib.sha256)
        key_file.write("\nECDSA private key:\n" + str.upper(sk.to_string().hex()))

        vk = sk.verifying_key
        key_file.write("\nECDSA public key:\n" + format(vk.pubkey.point.x(), 'X') +
                       "\n" + format(vk.pubkey.point.y(), 'X') + "\n")
        key_file.close()

        for img in d["data"]["image"]:
            try:
                with open(img["file"], "rb") as img_file:
                    data = img_file.read()
            except (IOError, OSError) as err:
                print(f"Open {img_file} failed")
                shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                sys.exit(err)

            aes_enc = AES.new(aeskey, AES.MODE_CFB, b'\x00' * 16, segment_size=128)
            data_out = aes_enc.encrypt(data)

            try:
                with open(now.strftime("%m%d-%H%M%S%f") + '/enc_' + img["file"], "wb") as enc_file:
                    enc_file.write(data_out)
                with open(now.strftime("%m%d-%H%M%S%f") + '/sig_' + img["file"], "wb") as sig_file:
                    sig_file.write(sk.sign(data_out))  # R & S
            except (IOError, OSError) as err:
                print("Create encrypt/signature file failed")
                shutil.rmtree(now.strftime("%m%d-%H%M%S%f"))
                sys.exit(err)
    try:
        os.unlink("conv")
    except (IOError, OSError):
        pass
    try:
        os.symlink(now.strftime("%m%d-%H%M%S%f"), "conv")
    except (IOError, OSError):
        print("Create symbolic folder conv failed")
    print("Generate output image(s) in directory {} complete".format(now.strftime("%m%d-%H%M%S%f")))


def __msc(dev, media, reserve, option) -> int:

    cmd = reserve.to_bytes(8, byteorder='little')
    cmd += b'\x00' * 8
    cmd += ACT_MSC.to_bytes(4, byteorder='little')
    cmd += option.to_bytes(4, byteorder='little')

    dev.set_media(media)
    dev.write(cmd)
    ack = dev.read(4)
    if int.from_bytes(ack, byteorder="little") != ACK:
        print("Receive ACK error")
        return -1
    return 0


def do_msc(media, reserve, option=OPT_NONE) -> None:
    global mp_mode

    # devices = XUsbComList(attach_all=mp_mode).get_dev()
    _XUsbComList = XUsbComList(attach_all=mp_mode)
    devices = _XUsbComList.get_dev()

    if len(devices) == 0:
        print("Device not found")
        sys.exit(2)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(__msc, dev, media, reserve, option) for dev in devices]
    success = 0
    failed = 0
    for future in as_completed(futures):
        if future.result() == 0:
            success += 1
        else:
            failed += 1

    print("Successfully {} {} MSC device(s)".format("set" if option == "OPT_NONE" else "eject", success))
    if failed > 0:
        print("Failed to {} {} MSC device(s)".format("set" if option == "OPT_NONE" else "eject", failed))


def get_media(media) -> int:
    media = str.upper(media)
    return {
        'DDR': DEV_DDR_SRAM,
        'SRAM': DEV_DDR_SRAM,
        'SD': DEV_SD_EMMC,
        'EMMC': DEV_SD_EMMC,
        'NAND': DEV_NAND,
        'SPINAND': DEV_SPINAND,
        'SPINOR': DEV_SPINOR,
        'OTP': DEV_OTP,
        'USBH': DEV_USBH
    }.get(media, DEV_UNKNOWN)


def get_option(option) -> int:
    option = str.upper(option)
    return {
        'SCRUB': OPT_SCRUB,
        'WITHBAD': OPT_WITHBAD,
        'VERIFY':  OPT_VERIFY,
        'EXECUTE': OPT_EXECUTE,
        'UNPACK': OPT_UNPACK,
        'RAW': OPT_RAW,
        'EJECT': OPT_EJECT,
        'STUFF': OPT_STUFF
    }.get(option, OPT_NONE)


def get_type(img_type) -> int:
    img_type = str.upper(img_type)
    return {
        'TFA': IMG_TFA,
        'UBOOT': IMG_UBOOT,
        'LINUX':  IMG_LINUX,
        'DDR': IMG_DDR,
        'TEE': IMG_TEE
    }.get(img_type, IMG_DATA)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("CONFIG", nargs='?', help="Config file", type=str, default='')
    parser.add_argument("-a", "--attach", action='store_true', help="Attach to MA35D1")
    parser.add_argument("-o", "--option", nargs='+', help="Option flag")
    parser.add_argument("-t", "--type", nargs='+', help="Type flag")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--convert", action='store_true', help="Convert images")
    group.add_argument("-p", "--pack", action='store_true', help="Generate pack file")
    group.add_argument("-v", "--version", action='store_true', help="Show version number")
    group.add_argument("-r", "--read", nargs='+', help="Read flash")
    group.add_argument("-w", "--write", nargs='+', help="Write flash")
    group.add_argument("-e", "--erase", nargs='+', help="Erase flash")
    group.add_argument("-s", "--storage", nargs='+', help="Export eMMC/SD as Mass Storage Class")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.option:
        option = get_option(args.option[0])
    else:
        option = OPT_NONE

    # if args.type:
    #     img_type = get_type(args.type[0])
    # else:
    #     img_type = IMG_DATA

    cfg_file = args.CONFIG

    if args.attach:
        if not cfg_file:
            print("Please assign a DDR ini file")
            sys.exit(0)
        # do_attach(cfg_file, mp_mode=False)
        do_attach(cfg_file, mp_mode1=False)

    if args.convert:
        if cfg_file == '':
            print("No config file assigned")
            sys.exit(0)
        else:
            do_convert(cfg_file)
    elif args.pack:
        if cfg_file == '':
            print("No config file assigned")
            sys.exit(0)
        else:
            if option == OPT_UNPACK:
                do_unpack(cfg_file)
            elif option == OPT_STUFF:
                do_stuff(cfg_file)
            else:
                do_pack(cfg_file)
    elif args.read:
        # -r spinor all out.bin
        # -r nand 0x1000 0x100 out.bin
        arg_count = len(args.read)
        if arg_count < 3:
            print("At lease take 3 arguments")
            sys.exit(0)
        media = get_media(args.read[0])

        try:
            if media in [DEV_OTP, DEV_UNKNOWN]:
                raise ValueError(f"Cannot support read {str.upper(args.read[0])}")
            if arg_count == 3 and str.upper(args.read[1]) != 'ALL':
                raise ValueError("Unknown arguments")
        except ValueError as err:
            sys.exit(err)

        if str.upper(args.read[1]) == 'ALL':
            do_img_read(media, 0, args.read[2], 0, option)
        else:
            try:
                start = int(args.read[1], 0)
                length = int(args.read[2], 0)
            except ValueError as err:
                print("Wrong start/length value")
                sys.exit(err)
            do_img_read(media, start, args.read[3], length, option)

    elif args.write:
        # -w spinor 0x1000 image.bin
        # -w otp otp.json
        # -w nand pack.img
        arg_count = len(args.write)
        if arg_count < 2:
            print("At lease take 2 arguments")
            sys.exit(0)
        media = get_media(args.write[0])

        try:
            if media == DEV_UNKNOWN:
                raise ValueError(f"Unknown storage media {str.upper(args.write[0])}")
            if option == OPT_VERIFY and media == DEV_OTP:
                raise ValueError(f"Do not support verify option on {str.upper(args.write[0])}")
            if option == OPT_EXECUTE and media != DEV_DDR_SRAM:
                raise ValueError(f"Do not support execution on {str.upper(args.write[0])}")
            if option == OPT_RAW and media != DEV_NAND:
                raise ValueError(f"Do not support raw write on {str.upper(args.write[0])}")
        except ValueError as err:
            sys.exit(err)

        if arg_count == 2:
            if media == DEV_OTP:
                do_otp_program(args.write[1])
            else:
                do_pack_program(media, args.write[1], option)
        else:
            try:
                start = int(args.write[1], 0)
            except ValueError as err:
                print("Wrong start value")
                sys.exit(err)
            do_img_program(media, start, args.write[2], option)

    elif args.erase:
        # -e spinor all
        # -e nand 0x100000 0x10000 -o withbad
        arg_count = len(args.erase)
        if arg_count < 2:
            print("At lease take 2 arguments")
            sys.exit(0)
        media = get_media(args.erase[0])

        try:
            if media in [DEV_DDR_SRAM, DEV_OTP, DEV_SD_EMMC, DEV_UNKNOWN]:
                raise ValueError(f"{str.upper(args.erase[0])} does not support erase")
            if arg_count == 2 and str.upper(args.erase[1]) != 'ALL':
                raise ValueError("Unknown arguments")
        except ValueError as err:
            sys.exit(err)

        if str.upper(args.erase[1]) == 'ALL':
            do_img_erase(media, 0, 0, option)
        else:
            try:
                start = int(args.erase[1], 0)
                length = int(args.erase[2], 0)
            except ValueError as err:
                print("Wrong start/length value")
                sys.exit(err)
            do_img_erase(media, start, length, option)
    elif args.storage:
        # -s emmc 0x800000
        # -s emmc -o remove
        arg_count = len(args.erase)
        if arg_count != 2 and option != OPT_EJECT:
            print("Takes 2 arguments. Storage device and reserved size")
            sys.exit(0)
        media = get_media(args.storage[0])
        try:
            if media not in [DEV_SD_EMMC]:
                raise ValueError("Only support eMMC/SD")
            if option != OPT_NONE and option != OPT_EJECT:
                raise ValueError("Unsupported option")
        except ValueError as err:
            sys.exit(err)

        if option == OPT_EJECT:
            do_msc(media, 0, OPT_EJECT)
        else:
            try:
                reserve = int(args.storage[1], 0)
            except ValueError as err:
                print("Wrong reserve size")
                sys.exit(err)
            do_msc(media, reserve)
    elif args.version:
        print('NuWriter ' + __version__)
        print(__copyright__)



# Here goes the main function
if __name__ == "__main__":
    main()
